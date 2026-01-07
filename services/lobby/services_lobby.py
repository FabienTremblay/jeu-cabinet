# services/lobby/services_lobby.py
from __future__ import annotations

import hashlib
import secrets
from typing import List, Optional, Literal

from fastapi import HTTPException, status

from .domaine import Joueur, Table, StatutTable
from .repositories import JoueurRepository, TableRepository
from .schemas import (
    DemandeInscription,
    ReponseInscription,
    DemandeConnexion,
    ReponseConnexion,
    DemandeCreationTable,
    ReponseTable,
    DemandePriseSiege,
    ReponseJoueurSiege,
    DemandeJoueurPret,
    DemandeLancerPartie,
    ReponsePartieLancee,
    ReponseJoueur,
    ReponseListeJoueursLobby,
    ReponseJoueurTable,
    ReponseListeJoueursTable,
    SkinInfo, ReponseListeSkins,
    ReponseContexteReprise,
)

from .events import (
    EvenementJoueurCree,
    EvenementJoueurIntroduit,
    EvenementJoueurConnecte,
    EvenementTableCree,
    EvenementJoueurARejointTable,
    EvenementJoueurPret,
    EvenementPartieLancee,
    JoueurPartie,
)
from .kafka_producteur import ProducteurEvenements
from .settings import Settings

SKINS_DISPONIBLES = [
    {
        "id_skin": "debut_mandat",
        "nom": "Début de mandat",
        "description": "Skin de démarrage classique pour apprendre le jeu.",
    },
    {
        "id_skin": "Mandat_difficile",
        "nom": "Second mandat",
        "description": "Il n'y en aura pas de facile pour remporter la prochaine élection",
    },
    {
        "id_skin": "debut_mandat_bre",
        "nom": "Test du BRE",
        "description": "On essaie",
    },
    # ...
]

def hacher_mot_de_passe(mot: str) -> str:
    return hashlib.sha256(mot.encode("utf-8")).hexdigest()


def verifier_mot_de_passe(mot: str, hache: str) -> bool:
    return hacher_mot_de_passe(mot) == hache


class ServiceLobby:
    """
    Service applicatif du lobby.

    Il orchestre :
    - la gestion des joueurs (inscription / connexion),
    - la gestion des tables (création / liste),
    - la prise de siège, l'état prêt, et le lancement de partie.
    """

    def __init__(
        self,
        settings: Settings,
        joueurs: JoueurRepository,
        tables: TableRepository,
        producteur: ProducteurEvenements,
    ) -> None:
        self.settings = settings
        self.joueurs = joueurs
        self.tables = tables
        self.producteur = producteur

    # -------------------------------------------------------------------------
    # joueurs : inscription / connexion
    # -------------------------------------------------------------------------

    async def inscrire_joueur(self, demande: DemandeInscription) -> ReponseInscription:
        # courriel déjà utilisé ?
        existant = self.joueurs.trouver_par_courriel(str(demande.courriel))
        if existant is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="courriel_deja_utilise",
            )

        id_joueur = self.joueurs.prochain_id()
        mot_de_passe_hache = hacher_mot_de_passe(demande.mot_de_passe)

        joueur = Joueur(
            id_joueur=id_joueur,
            nom=demande.nom,
            alias=demande.alias,
            courriel=demande.courriel,
            mot_de_passe_hache=mot_de_passe_hache,
        )
        self.joueurs.ajouter(joueur)

        # événements
        evt_cree = EvenementJoueurCree(
            id_joueur=joueur.id_joueur,
            nom=joueur.nom,
            alias=joueur.alias,
            courriel=joueur.courriel,
        )
        evt_introduit = EvenementJoueurIntroduit(
            id_joueur=joueur.id_joueur,
            origine="inscription",
        )
        await self.producteur.publier(self.settings.kafka_topic_evenements_joueurs, evt_cree)
        await self.producteur.publier(self.settings.kafka_topic_evenements_joueurs, evt_introduit)

        return ReponseInscription(
            id_joueur=joueur.id_joueur,
            nom=joueur.nom,
            alias=joueur.alias,
            courriel=joueur.courriel,
        )

    async def connecter_joueur(self, demande: DemandeConnexion) -> ReponseConnexion:
        joueur = self.joueurs.trouver_par_courriel(str(demande.courriel))
        if joueur is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="joueur_introuvable",
            )

        if not verifier_mot_de_passe(demande.mot_de_passe, joueur.mot_de_passe_hache):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="mot_de_passe_invalide",
            )

        jeton_session = secrets.token_urlsafe(32)

        # contexte de reprise : table active du joueur (si elle existe)
        table_active = self.tables.trouver_table_active_du_joueur(joueur.id_joueur)
        id_table = table_active.id_table if table_active is not None else None
        id_partie = table_active.id_partie if table_active is not None else None
        statut_table = (
            table_active.statut.value if table_active is not None and hasattr(table_active.statut, "value") else None
        )
        skin_jeu = table_active.skin_jeu if table_active is not None else None

        evt_connecte = EvenementJoueurConnecte(
            id_joueur=joueur.id_joueur,
            origine="connexion",
        )
        await self.producteur.publier(self.settings.kafka_topic_evenements_joueurs, evt_connecte)

        return ReponseConnexion(
            id_joueur=joueur.id_joueur,
            nom=joueur.nom,
            alias=joueur.alias,
            courriel=joueur.courriel,
            jeton_session=jeton_session,
            id_table=id_table,
            id_partie=id_partie,
            statut_table=statut_table,
            skin_jeu=skin_jeu,
        )

    async def contexte_reprise(self, id_joueur: str) -> ReponseContexteReprise:
        """
        Retourne le contexte de reprise (table/partie) pour un joueur.
        Utile pour un refresh UI ou un retour de navigation sans reconnexion.
        """
        # sécurité minimale: joueur connu ?
        joueur = self.joueurs.trouver_par_id(id_joueur)
        if joueur is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="joueur_introuvable",
            )

        table_active = self.tables.trouver_table_active_du_joueur(id_joueur)
        return ReponseContexteReprise(
            id_joueur=id_joueur,
            id_table=table_active.id_table if table_active is not None else None,
            id_partie=table_active.id_partie if table_active is not None else None,
            statut_table=(table_active.statut.value if table_active is not None else None),
            skin_jeu=table_active.skin_jeu if table_active is not None else None,
        )

    # -------------------------------------------------------------------------
    # tables : création / liste
    # -------------------------------------------------------------------------

    async def creer_table(self, demande: DemandeCreationTable) -> ReponseTable:
        # un joueur ne peut être hôte que d'une table active à la fois
        table_existante = self.tables.trouver_table_active_du_joueur(demande.id_hote)
        if table_existante is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="table_deja_active_pour_ce_joueur",
            )

        # validation skin
        if demande.skin_jeu is not None:
            ids_valides = {s["id_skin"] for s in SKINS_DISPONIBLES}
            if demande.skin_jeu not in ids_valides:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="skin_invalide",
                )

        id_table = self.tables.prochain_id()
        table = Table(
            id_table=id_table,
            nom_table=demande.nom_table,
            nb_sieges=demande.nb_sieges,
            id_hote=demande.id_hote,
            mot_de_passe_table=demande.mot_de_passe_table,
            skin_jeu=demande.skin_jeu,
        )
        self.tables.ajouter(table)

        evt = EvenementTableCree(
            id_table=table.id_table,
            nom_table=table.nom_table,
            nb_sieges=table.nb_sieges,
            id_hote=table.id_hote,
            skin_jeu=table.skin_jeu,
        )
        await self.producteur.publier(self.settings.kafka_topic_evenements_tables, evt)

        return ReponseTable.from_table(table)

    async def lister_skins(self) -> ReponseListeSkins:
        return ReponseListeSkins(
            skins=[SkinInfo(**data) for data in SKINS_DISPONIBLES]
        )

    async def lister_joueurs_lobby(self) -> list[ReponseJoueur]:
        """
        Joueurs connus qui ne sont impliqués dans aucune table active
        (ni comme hôte, ni comme joueur assis).
        """
        joueurs_dto: list[ReponseJoueur] = []

        for j in self.joueurs.lister():
            # si le joueur est déjà à une table active (hôte ou assis),
            # on ne le considère plus "dans le lobby"
            if self.tables.joueur_est_deja_installe(j.id_joueur):
                continue

            joueurs_dto.append(
                ReponseJoueur(
                    id_joueur=j.id_joueur,
                    nom=j.nom,
                    alias=j.alias,
                    courriel=j.courriel,
                )
            )

        return joueurs_dto

    async def lister_tables(self, statut: Optional[StatutTable]) -> List[ReponseTable]:
        tables = self.tables.lister(statut)
        return [ReponseTable.from_table(t) for t in tables]

    # -------------------------------------------------------------------------
    # sièges / prêts / lancement de partie
    # -------------------------------------------------------------------------

    async def prendre_siege(self, id_table: str, demande: DemandePriseSiege) -> ReponseJoueurSiege:
        # existence table (404 cohérent)
        table = self.tables.trouver_par_id(id_table)
        if table is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="table_introuvable")

        # un joueur ne peut pas être à plusieurs tables actives
        table_active = self.tables.trouver_table_active_du_joueur(demande.id_joueur)
        if table_active is not None and table_active.id_table != table.id_table:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="joueur_deja_a_une_autre_table",
            )

        try:
            # IMPORTANT: opération atomique côté repo (persistance durable en SQL)
            table = self.tables.prendre_siege(
                id_table=id_table,
                id_joueur=demande.id_joueur,
                role=demande.role,
            )
        except ValueError as e:
            if str(e) == "table_introuvable":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="table_introuvable",
                ) from e
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            ) from e

        evt = EvenementJoueurARejointTable(
            id_table=table.id_table,
            id_joueur=demande.id_joueur,
            role=demande.role,
        )
        await self.producteur.publier(self.settings.kafka_topic_evenements_tables, evt)

        return ReponseJoueurSiege(
            id_table=table.id_table,
            id_joueur=demande.id_joueur,
            role=demande.role,
            statut_table=table.statut.value,
        )

    async def lister_joueurs_table(self, id_table: str) -> List[ReponseJoueurTable]:
        """
        Retourne la liste des joueurs d'une table pour l'API.

        - id_table : identifiant de la table
        - réponse : ReponseListeJoueursTable(id_table, joueurs=[...])
        """
        table = self.tables.trouver_par_id(id_table)
        if table is None:
            # cohérent avec le reste du service
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="table_introuvable",
            )

        joueurs_dto: List[ReponseJoueurTable] = []

        # on utilise les joueurs "présents" : hôte + joueurs assis, sans doublons
        for id_j in table.liste_joueurs_presents():
            joueur = self.joueurs.trouver_par_id(id_j)
            if joueur is None:
                # données incohérentes, on ignore
                continue

            role: Literal["hote", "invite"] = "hote" if id_j == table.id_hote else "invite"
            pret = id_j in table.joueurs_prets

            joueurs_dto.append(
                ReponseJoueurTable(
                    id_joueur=joueur.id_joueur,
                    nom=joueur.nom,
                    alias=joueur.alias,
                    courriel=joueur.courriel,
                    role=role,
                    pret=pret,
                )
            )

        return joueurs_dto


    async def marquer_joueur_pret(self, id_table: str, id_joueur: str) -> ReponseTable:
        try:
            table = self.tables.marquer_joueur_pret(id_table=id_table, id_joueur=id_joueur)
        except ValueError as e:
            if str(e) == "table_introuvable":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="table_introuvable",
                ) from e
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            ) from e

        evt = EvenementJoueurPret(
            id_table=table.id_table,
            id_joueur=id_joueur,
        )
        await self.producteur.publier(self.settings.kafka_topic_evenements_tables, evt)

        return ReponseTable.from_table(table)

    async def quitter_table(self, id_table: str, id_joueur: str) -> ReponseTable:
        """Permet à un joueur de quitter sa table (retour au lobby).

        Règle métier : si c'est l'hôte qui quitte, la table est dissoute.
        """
        try:
            table = self.tables.quitter_table(id_table=id_table, id_joueur=id_joueur)
        except ValueError as e:
            if str(e) == "table_introuvable":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="table_introuvable",
                ) from e
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            ) from e

        return ReponseTable.from_table(table)

    async def quitter_partie(self, id_partie: str, id_joueur: str) -> ReponseTable:
        # 1) trouver la table par id_partie
        table = self.tables.trouver_par_id_partie(id_partie)
        if table is None:
            # idempotence / sécurité : soit 404, soit ignore
            raise HTTPException(
                status_code=404,
                detail="table_introuvable_pour_cette_partie",
            )

        # 2) réutiliser la logique de quitter_table
        return await self.quitter_table(id_table=table.id_table, id_joueur=id_joueur)

    async def terminer_table(self, id_table: str) -> ReponseTable:
        """Marque une table comme terminée côté lobby.

        Cette méthode est prévue pour être appelée par un worker qui
        consomme les événements de fin de partie côté moteur, ou par
        une action explicite de l'hôte si tu le souhaites.
        """
        try:
            table = self.tables.terminer_table(id_table)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="table_introuvable",
            ) from e

        return ReponseTable.from_table(table)

    async def joueur_quitte_partie_definitivement(
        self,
        id_partie: str,
        id_joueur: str,
    ) -> None:
        """
        Synchronise le lobby lorsqu'un joueur quitte définitivement une partie
        (op_code D600: partie.joueur_quitte_definitivement).

        Règles:
        - on libère le joueur pour qu'il puisse participer à une autre table;
        - on ne réutilise pas la table pour d'autres joueurs;
        - si le dernier joueur quitte, on marque la table comme terminée;
        - le traitement est idempotent : si l'état est déjà à jour, on sort
          sans erreur.
        """
        # 1) trouver la table associée à cette partie
        table = self.tables.trouver_par_id_partie(id_partie)
        if table is None:
            # rien à faire : on tolère l'absence de table (idempotence / replays)
            return

        # sécurité : cohérence élémentaire
        if table.id_partie != id_partie:
            return

        # 2) si le joueur n'est plus présent, on considère que le traitement
        # est déjà fait (idempotence)
        if (
            id_joueur != table.id_hote
            and id_joueur not in table.joueurs_assis
            and id_joueur not in table.joueurs_prets
        ):
            return

        # 3) retirer le joueur de la table
        # IMPORTANT: opération durable côté repo (SQL) / atomique côté mémoire
        self.tables.quitter_table(id_table=table.id_table, id_joueur=id_joueur)

        # 4) si plus aucun joueur n'est présent, on termine la table.
        #    la table ne sera pas réutilisée pour une nouvelle partie.
        # NB: la règle exacte de terminaison est laissée inchangée ici (comportement existant).
        #     La persistance est maintenant correcte.


    async def lancer_partie(self, id_table: str, id_hote: str) -> ReponsePartieLancee:
        table = self.tables.trouver_par_id(id_table)
        if table is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="table_introuvable",
            )

        if table.id_hote != id_hote:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="seul_l_hote_peut_lancer",
            )

        if not table.tous_les_joueurs_prets():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="joueurs_pas_tous_prets",
            )

        # création de l'id de partie + changement d'état table
        id_partie = self.tables.prochain_id_partie()
        table = self.tables.marquer_partie_lancee(id_table=id_table, id_partie=id_partie)

        # on construit la liste complète des joueurs à partir du repo
        joueurs_evt: List[JoueurPartie] = []

        for id_j in table.liste_joueurs_presents():
            joueur = self.joueurs.trouver_par_id(id_j)
            if joueur is None:
                # données incohérentes, on pourrait raise ici si tu préfères
                continue

            role: Literal["hote", "invite"] = "hote" if id_j == table.id_hote else "invite"

            joueurs_evt.append(
                JoueurPartie(
                    id_joueur=joueur.id_joueur,
                    nom=joueur.nom,
                    alias=joueur.alias,
                    courriel=joueur.courriel,
                    role=role,
                )
            )

        evt = EvenementPartieLancee(
            id_table=table.id_table,
            id_partie=id_partie,
            joueurs=joueurs_evt,
            skin_jeu=table.skin_jeu,
        )
        await self.producteur.publier(self.settings.kafka_topic_evenements_parties, evt)

        return ReponsePartieLancee(id_partie=id_partie)

