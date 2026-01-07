# services/lobby/repositories_sql.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Literal

import psycopg

from .domaine import Joueur, Table, StatutTable
from .ids import GenerateurIds


@dataclass(frozen=True)
class Db:
    dsn: str

    def connect(self) -> psycopg.Connection:
        return psycopg.connect(self.dsn, autocommit=False)


def _assurer_compteurs(cur) -> None:
    cur.execute(
        """
        create table if not exists lobby_compteurs (
          cle text primary key,
          valeur bigint not null
        )
        """
    )


class JoueurRepositorySQL:
    def __init__(self, db: Db, generateur_ids: GenerateurIds) -> None:
        self._db = db
        self._ids = generateur_ids

    def prochain_id(self) -> str:
        if self._ids.mode.lower().strip() == "sequentiel":
            with self._db.connect() as conn, conn.cursor() as cur:
                _assurer_compteurs(cur)
                cur.execute(
                    """
                    insert into lobby_compteurs(cle, valeur)
                    values ('joueur', 0)
                    on conflict (cle) do nothing
                    """
                )
                cur.execute(
                    """
                    update lobby_compteurs
                    set valeur = valeur + 1
                    where cle = 'joueur'
                    returning valeur
                    """
                )
                (valeur,) = cur.fetchone()
                conn.commit()
                return self._ids.id_joueur(int(valeur))
        return self._ids.id_joueur(None)

    def ajouter(self, joueur: Joueur) -> None:
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                insert into lobby_joueurs(id_joueur, nom, alias, courriel, mot_de_passe_hache)
                values (%s, %s, %s, %s, %s)
                on conflict (id_joueur) do update set
                  nom = excluded.nom,
                  alias = excluded.alias,
                  courriel = excluded.courriel,
                  mot_de_passe_hache = excluded.mot_de_passe_hache,
                  maj_le = now()
                """,
                (joueur.id_joueur, joueur.nom, joueur.alias, str(joueur.courriel), joueur.mot_de_passe_hache),
            )
            conn.commit()

    def trouver_par_id(self, id_joueur: str) -> Optional[Joueur]:
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                select id_joueur, nom, alias, courriel, mot_de_passe_hache
                from lobby_joueurs
                where id_joueur = %s
                """,
                (id_joueur,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return Joueur(
                id_joueur=row[0],
                nom=row[1],
                alias=row[2],
                courriel=row[3],
                mot_de_passe_hache=row[4],
            )

    def trouver_par_courriel(self, courriel: str) -> Optional[Joueur]:
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                select id_joueur, nom, alias, courriel, mot_de_passe_hache
                from lobby_joueurs
                where courriel = %s
                """,
                (courriel,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return Joueur(
                id_joueur=row[0],
                nom=row[1],
                alias=row[2],
                courriel=row[3],
                mot_de_passe_hache=row[4],
            )

    def lister(self) -> Iterable[Joueur]:
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                select id_joueur, nom, alias, courriel, mot_de_passe_hache
                from lobby_joueurs
                order by cree_le asc
                """
            )
            for row in cur.fetchall():
                yield Joueur(
                    id_joueur=row[0],
                    nom=row[1],
                    alias=row[2],
                    courriel=row[3],
                    mot_de_passe_hache=row[4],
                )


class TableRepositorySQL:
    def __init__(self, db: Db, generateur_ids: GenerateurIds) -> None:
        self._db = db
        self._ids = generateur_ids

    def prendre_siege(self, id_table: str, id_joueur: str, role: Literal["hote", "invite"]) -> Table:
        """
        Opération atomique (version SQL) : BEGIN -> SELECT FOR UPDATE -> muter -> persister -> COMMIT.
        Garantit la règle "place disponible" même en concurrence.
        """
        with self._db.connect() as conn:
            table = self._trouver_par_id_conn(conn, id_table, for_update=True)
            if table is None:
                raise ValueError("table_introuvable")

            table.prendre_siege(id_joueur, role)
            self._ajouter_conn(conn, table)
            conn.commit()
            return table

    def marquer_joueur_pret(self, id_table: str, id_joueur: str) -> Table:
        """
        Opération atomique (version SQL) : BEGIN -> SELECT FOR UPDATE -> muter -> persister -> COMMIT.
        """
        with self._db.connect() as conn:
            table = self._trouver_par_id_conn(conn, id_table, for_update=True)
            if table is None:
                raise ValueError("table_introuvable")

            table.marquer_joueur_pret(id_joueur)
            self._ajouter_conn(conn, table)
            conn.commit()
            return table

    def quitter_table(self, id_table: str, id_joueur: str) -> Table:
        """
        Opération atomique (version SQL) : BEGIN -> SELECT FOR UPDATE -> muter -> persister -> COMMIT.
        Règle métier : si l'hôte quitte, la table est dissoute.
        Idempotence : si déjà parti, on renvoie l'état courant sans erreur.
        """
        with self._db.connect() as conn:
            table = self._trouver_par_id_conn(conn, id_table, for_update=True)
            if table is None:
                raise ValueError("table_introuvable")

            if (
                id_joueur != table.id_hote
                and id_joueur not in table.joueurs_assis
                and id_joueur not in table.joueurs_prets
            ):
                return table

            est_hote = (id_joueur == table.id_hote)
            table.retirer_joueur(id_joueur)

            if est_hote:
                table.terminer_partie()
                table.vider_joueurs()

            self._ajouter_conn(conn, table)
            conn.commit()
            return table

    def _trouver_par_id_conn(self, conn: psycopg.Connection, id_table: str, *, for_update: bool) -> Optional[Table]:
        """
        Variante de trouver_par_id qui réutilise la même connexion (transaction),
        avec option FOR UPDATE pour sérialiser les prises de siège concurrentes.
        """
        with conn.cursor() as cur:
            cur.execute(
                f"""
                select id_table, nom_table, nb_sieges, id_hote, statut, skin_jeu, id_partie
                from lobby_tables
                where id_table = %s
                {'for update' if for_update else ''}
                """,
                (id_table,),
            )
            t = cur.fetchone()
            if not t:
                return None

            cur.execute(
                """
                select id_joueur, role, assis, pret
                from lobby_table_joueurs
                where id_table = %s
                """,
                (id_table,),
            )
            rows = cur.fetchall()
            joueurs_assis = [r[0] for r in rows if r[2]]
            joueurs_prets = [r[0] for r in rows if r[3]]

            return Table(
                id_table=t[0],
                nom_table=t[1],
                nb_sieges=t[2],
                id_hote=t[3],
                statut=StatutTable(t[4]),
                skin_jeu=t[5],
                id_partie=t[6],
                joueurs_assis=joueurs_assis,
                joueurs_prets=joueurs_prets,
            )

    def _ajouter_conn(self, conn: psycopg.Connection, table: Table) -> None:
        """
        Variante de ajouter() qui réutilise la même connexion (transaction),
        sans commit implicite.
        """
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into lobby_tables(id_table, nom_table, nb_sieges, id_hote, statut, skin_jeu, id_partie)
                values (%s, %s, %s, %s, %s, %s, %s)
                on conflict (id_table) do update set
                  nom_table = excluded.nom_table,
                  nb_sieges = excluded.nb_sieges,
                  id_hote = excluded.id_hote,
                  statut = excluded.statut,
                  skin_jeu = excluded.skin_jeu,
                  id_partie = excluded.id_partie,
                  maj_le = now()
                """,
                (
                    table.id_table,
                    table.nom_table,
                    table.nb_sieges,
                    table.id_hote,
                    table.statut.value if hasattr(table.statut, "value") else str(table.statut),
                    table.skin_jeu,
                    table.id_partie,
                ),
            )

            cur.execute("delete from lobby_table_joueurs where id_table = %s", (table.id_table,))

            cur.execute(
                """
                insert into lobby_table_joueurs(id_table, id_joueur, role, assis, pret)
                values (%s, %s, %s, %s, %s)
                """,
                (table.id_table, table.id_hote, "hote", True, table.id_hote in table.joueurs_prets),
            )

            for idj in table.joueurs_assis:
                if idj == table.id_hote:
                    continue
                cur.execute(
                    """
                    insert into lobby_table_joueurs(id_table, id_joueur, role, assis, pret)
                    values (%s, %s, %s, %s, %s)
                    """,
                    (table.id_table, idj, "invite", True, idj in table.joueurs_prets),
                )

    def prochain_id(self) -> str:
        if self._ids.mode.lower().strip() == "sequentiel":
            with self._db.connect() as conn, conn.cursor() as cur:
                _assurer_compteurs(cur)
                cur.execute(
                    """
                    insert into lobby_compteurs(cle, valeur)
                    values ('table', 0)
                    on conflict (cle) do nothing
                    """
                )
                cur.execute(
                    """
                    update lobby_compteurs
                    set valeur = valeur + 1
                    where cle = 'table'
                    returning valeur
                    """
                )
                (valeur,) = cur.fetchone()
                conn.commit()
                return self._ids.id_table(int(valeur))
        return self._ids.id_table(None)

    def prochain_id_partie(self) -> str:
        if self._ids.mode.lower().strip() == "sequentiel":
            with self._db.connect() as conn, conn.cursor() as cur:
                _assurer_compteurs(cur)
                cur.execute(
                    """
                    insert into lobby_compteurs(cle, valeur)
                    values ('partie', 0)
                    on conflict (cle) do nothing
                    """
                )
                cur.execute(
                    """
                    update lobby_compteurs
                    set valeur = valeur + 1
                    where cle = 'partie'
                    returning valeur
                    """
                )
                (valeur,) = cur.fetchone()
                conn.commit()
                return self._ids.id_partie(int(valeur))
        return self._ids.id_partie(None)

    def ajouter(self, table: Table) -> None:
        with self._db.connect() as conn:
            self._ajouter_conn(conn, table)
            conn.commit()

    def trouver_par_id(self, id_table: str) -> Optional[Table]:
        with self._db.connect() as conn:
            return self._trouver_par_id_conn(conn, id_table, for_update=False)

    def lister(self, statut: StatutTable | None = None) -> Iterable[Table]:
        with self._db.connect() as conn, conn.cursor() as cur:
            if statut is None:
                cur.execute("select id_table from lobby_tables order by cree_le asc")
                ids = [r[0] for r in cur.fetchall()]
            else:
                cur.execute(
                    "select id_table from lobby_tables where statut = %s order by cree_le asc",
                    (statut.value if hasattr(statut, "value") else str(statut),),
                )
                ids = [r[0] for r in cur.fetchall()]

        for idt in ids:
            t = self.trouver_par_id(idt)
            if t is not None:
                yield t

    def tous_les_joueurs_assis(self) -> set[str]:
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute("select distinct id_joueur from lobby_table_joueurs where assis = true")
            return {r[0] for r in cur.fetchall()}

    def trouver_table_active_du_joueur(self, id_joueur: str) -> Optional[Table]:
        statuts_actifs = (
            StatutTable.OUVERTE.value,
            StatutTable.EN_PREPARATION.value,
            StatutTable.EN_COURS.value,
        )
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                select t.id_table
                from lobby_tables t
                join lobby_table_joueurs tj on tj.id_table = t.id_table
                where tj.id_joueur = %s
                  and t.statut = any(%s)
                order by t.cree_le asc
                limit 1
                """,
                (id_joueur, list(statuts_actifs)),
            )
            row = cur.fetchone()
            if not row:
                return None
            return self.trouver_par_id(row[0])

    def trouver_par_id_partie(self, id_partie: str) -> Optional[Table]:
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(
                "select id_table from lobby_tables where id_partie = %s limit 1",
                (id_partie,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return self.trouver_par_id(row[0])

    def joueur_est_deja_installe(self, id_joueur: str) -> bool:
        return self.trouver_table_active_du_joueur(id_joueur) is not None

    def marquer_partie_lancee(self, id_table: str, id_partie: str) -> Table:
        table = self.trouver_par_id(id_table)
        if table is None:
            raise ValueError("table_introuvable")
        table.id_partie = id_partie
        table.statut = StatutTable.EN_COURS
        self.ajouter(table)
        return table

    def terminer_table(self, id_table: str) -> Table:
        table = self.trouver_par_id(id_table)
        if table is None:
            raise ValueError(f"table_introuvable: {id_table}")
        table.terminer_partie()
        self.ajouter(table)
        return table

    def dissoudre_table(self, id_table: str) -> Table:
        table = self.trouver_par_id(id_table)
        if table is None:
            raise ValueError(f"table_introuvable: {id_table}")
        table.terminer_partie()
        table.vider_joueurs()
        self.ajouter(table)
        return table
