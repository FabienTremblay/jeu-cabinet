from __future__ import annotations

from typing import Dict, Iterable, Optional, Literal

from .domaine import Joueur, Table, StatutTable
from .ids import GenerateurIds


class JoueurRepository:
    """Dépôt simple en mémoire pour les joueurs."""

    def __init__(self, generateur_ids: GenerateurIds | None = None) -> None:
        self._par_id: Dict[str, Joueur] = {}
        self._par_courriel: Dict[str, Joueur] = {}
        self._ids = generateur_ids or GenerateurIds(mode="sequentiel")

    def ajouter(self, joueur: Joueur) -> None:
        self._par_id[joueur.id_joueur] = joueur
        self._par_courriel[str(joueur.courriel)] = joueur

    def trouver_par_id(self, id_joueur: str) -> Optional[Joueur]:
        return self._par_id.get(id_joueur)

    def trouver_par_courriel(self, courriel: str) -> Optional[Joueur]:
        return self._par_courriel.get(courriel)

    def lister(self) -> Iterable[Joueur]:
        return self._par_id.values()

    def prochain_id(self) -> str:
        if self._ids.mode.lower().strip() == "sequentiel":
            return self._ids.id_joueur(len(self._par_id) + 1)
        return self._ids.id_joueur(None)


class TableRepository:
    """Dépôt en mémoire pour les tables du lobby."""

    def __init__(self, generateur_ids: GenerateurIds | None = None) -> None:
        self._par_id: Dict[str, Table] = {}
        self._compteur_parties: int = 0
        self._ids = generateur_ids or GenerateurIds(mode="sequentiel")

    def ajouter(self, table: Table) -> None:
        self._par_id[table.id_table] = table

    def trouver_par_id(self, id_table: str) -> Optional[Table]:
        return self._par_id.get(id_table)

    def prendre_siege(self, id_table: str, id_joueur: str, role: Literal["hote", "invite"]) -> Table:
        """
        Opération atomique (version mémoire) : charge -> muter -> persister -> retourner.
        """
        table = self.trouver_par_id(id_table)
        if table is None:
            raise ValueError("table_introuvable")

        table.prendre_siege(id_joueur, role)
        self.ajouter(table)
        return table

    def marquer_joueur_pret(self, id_table: str, id_joueur: str) -> Table:
        table = self.trouver_par_id(id_table)
        if table is None:
            raise ValueError("table_introuvable")
        table.marquer_joueur_pret(id_joueur)
        self.ajouter(table)
        return table

    def quitter_table(self, id_table: str, id_joueur: str) -> Table:
        table = self.trouver_par_id(id_table)
        if table is None:
            raise ValueError("table_introuvable")

        # déjà parti ? -> idempotence
        if (
            id_joueur != table.id_hote
            and id_joueur not in table.joueurs_assis
            and id_joueur not in table.joueurs_prets
        ):
            return table

        est_hote = (id_joueur == table.id_hote)
        table.retirer_joueur(id_joueur)

        if est_hote:
            # règle : si l'hôte quitte, on dissout la table
            table.terminer_partie()
            table.vider_joueurs()

        self.ajouter(table)
        return table

    def lister(self, statut: StatutTable | None = None) -> Iterable[Table]:
        for t in self._par_id.values():
            if statut is None or t.statut == statut:
                yield t

    def tous_les_joueurs_assis(self) -> set[str]:
        ids: set[str] = set()
        for table in self._par_id.values():
            ids.update(table.joueurs_assis)
        return ids

    def trouver_table_active_du_joueur(self, id_joueur: str) -> Optional[Table]:
        statuts_actifs: tuple[StatutTable, ...] = (
            StatutTable.OUVERTE,
            StatutTable.EN_PREPARATION,
            StatutTable.EN_COURS,
        )
        for table in self._par_id.values():
            if table.statut not in statuts_actifs:
                continue
            if table.id_hote == id_joueur or id_joueur in table.joueurs_assis:
                return table
        return None

    def trouver_par_id_partie(self, id_partie: str) -> Optional[Table]:
        for table in self._par_id.values():
            if table.id_partie == id_partie:
                return table
        return None

    def joueur_est_deja_installe(self, id_joueur: str) -> bool:
        return self.trouver_table_active_du_joueur(id_joueur) is not None

    def marquer_partie_lancee(self, id_table: str, id_partie: str) -> Table:
        table = self.trouver_par_id(id_table)
        if table is None:
            raise ValueError("table_introuvable")

        table.id_partie = id_partie
        table.statut = StatutTable.EN_COURS
        return table

    def prochain_id(self) -> str:
        if self._ids.mode.lower().strip() == "sequentiel":
            return self._ids.id_table(len(self._par_id) + 1)
        return self._ids.id_table(None)

    def prochain_id_partie(self) -> str:
        if self._ids.mode.lower().strip() == "sequentiel":
            self._compteur_parties += 1
            return self._ids.id_partie(self._compteur_parties)
        return self._ids.id_partie(None)

    def terminer_table(self, id_table: str) -> Table:
        table = self.trouver_par_id(id_table)
        if table is None:
            raise ValueError(f"table_introuvable: {id_table}")

        table.terminer_partie()
        return table

    def dissoudre_table(self, id_table: str) -> Table:
        table = self.trouver_par_id(id_table)
        if table is None:
            raise ValueError(f"table_introuvable: {id_table}")

        table.terminer_partie()
        table.vider_joueurs()
        return table
