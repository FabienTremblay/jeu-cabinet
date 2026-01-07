from __future__ import annotations

from enum import Enum
from typing import Literal, List
from pydantic import BaseModel, EmailStr, Field


class Joueur(BaseModel):
    """Entité joueur telle que conservée côté lobby."""

    id_joueur: str
    nom: str
    alias: str
    courriel: EmailStr
    mot_de_passe_hache: str


class SessionJoueur(BaseModel):
    """Session d'un joueur connecté au lobby."""

    id_joueur: str
    jeton_session: str
    expire_le: float  # timestamp epoch pour garder simple ici


class StatutTable(str, Enum):
    """Statut d'une table de jeu dans le lobby."""

    OUVERTE = "ouverte"
    EN_PREPARATION = "en_preparation"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"


class JoueurSiege(BaseModel):
    """Petit objet de retour quand un joueur prend un siège."""

    id_joueur: str
    role: Literal["hote", "invite"]


class Table(BaseModel):
    """Table de jeu dans le lobby."""

    id_table: str
    nom_table: str
    nb_sieges: int
    id_hote: str
    mot_de_passe_table: str | None = None
    skin_jeu: str | None = None
    id_partie: str | None = None
    joueurs_assis: List[str] = Field(default_factory=list)
    joueurs_prets: List[str] = Field(default_factory=list)
    statut: StatutTable = StatutTable.OUVERTE

    # ------------------------------------------------------------------
    # logique métier minimale côté domaine
    # ------------------------------------------------------------------

    def prendre_siege(self, id_joueur: str, role: Literal["hote", "invite"]) -> JoueurSiege:
        """
        Ajoute un joueur à la liste des joueurs assis, avec quelques validations.
        Retourne un JoueurSiege pour que le service puisse construire sa réponse.
        """
        if id_joueur in self.joueurs_assis or id_joueur == self.id_hote and id_joueur in self.joueurs_assis:
            raise ValueError("joueur_deja_assis")

        # capacité = nombre total de joueurs (hôte inclus)
        if len(self.liste_joueurs_presents()) >= self.nb_sieges:
            raise ValueError("plus_de_place_disponible")

        if role == "hote" and id_joueur != self.id_hote:
            raise ValueError("hote_incoherent")

        # on considère que les invités sont dans joueurs_assis
        # l'hôte peut aussi y figurer si on le fait s'asseoir explicitement
        self.joueurs_assis.append(id_joueur)

        # la table reste "ouverte" tant qu'il reste de la place
        # on passe en préparation seulement quand elle est complète
        if len(self.liste_joueurs_presents()) >= self.nb_sieges:
            self.statut = StatutTable.EN_PREPARATION
        else:
            self.statut = StatutTable.OUVERTE

        return JoueurSiege(id_joueur=id_joueur, role=role)

    def marquer_joueur_pret(self, id_joueur: str) -> None:
        """
        Marque un joueur comme prêt.
        On considère que l'hôte fait aussi partie des joueurs 'présents'.
        """
        # joueur présent = hôte ou joueur assis
        if id_joueur != self.id_hote and id_joueur not in self.joueurs_assis:
            raise ValueError("joueur_non_assis")

        if id_joueur not in self.joueurs_prets:
            self.joueurs_prets.append(id_joueur)

    def liste_joueurs_presents(self) -> List[str]:
        """
        Retourne la liste des joueurs impliqués à la table
        (hôte + joueurs assis, sans doublons).
        """
        ids = list(self.joueurs_assis)
        if self.id_hote not in ids:
            ids.insert(0, self.id_hote)
        return ids

    def tous_les_joueurs_prets(self) -> bool:
        """
        Vérifie si tous les joueurs présents (hôte + assis) sont marqués prêts.
        """
        joueurs_presents = set(self.liste_joueurs_presents())
        if not joueurs_presents:
            return False
        return joueurs_presents.issubset(set(self.joueurs_prets))

    # ------------------------------------------------------------------
    # gestion des sièges et fin de partie
    # ------------------------------------------------------------------

    def retirer_joueur(self, id_joueur: str) -> None:
        """
        Retire un joueur de la table (assis/prêt).

        Cette méthode ne modifie pas l'attribut id_hote : on considère
        que la gestion d'un éventuel changement d'hôte se fait ailleurs.
        """
        if id_joueur in self.joueurs_assis:
            self.joueurs_assis.remove(id_joueur)

        if id_joueur in self.joueurs_prets:
            self.joueurs_prets.remove(id_joueur)

    def vider_joueurs(self) -> None:
        """
        Vide tous les joueurs assis et prêts de la table.

        Utile lorsqu'on dissout complètement la table en fin de partie.
        """
        self.joueurs_assis.clear()
        self.joueurs_prets.clear()

    def terminer_partie(self) -> None:
        """
        Marque la table comme terminée côté lobby.

        Le simple fait de passer au statut TERMINEE suffit à ce que
        le lobby ne considère plus cette table comme « active » dans
        les méthodes qui filtrent sur les statuts (ouverte, en préparation,
        en cours). La libération fine des sièges est optionnelle et peut
        être obtenue en appelant aussi vider_joueurs().
        """
        self.statut = StatutTable.TERMINEE


