# services/lobby/schemas.py
from __future__ import annotations

from typing import Literal, List, Optional
from pydantic import BaseModel, EmailStr

from .domaine import Table, StatutTable


# --- joueurs ---


class DemandeInscription(BaseModel):
    nom: str
    alias: str
    courriel: EmailStr
    mot_de_passe: str


class ReponseInscription(BaseModel):
    id_joueur: str
    nom: str
    alias: str
    courriel: EmailStr


class DemandeConnexion(BaseModel):
    courriel: EmailStr
    mot_de_passe: str


class ReponseConnexion(BaseModel):
    id_joueur: str
    nom: str
    alias: str
    courriel: EmailStr
    jeton_session: str
    # contexte optionnel de reprise (si le joueur est déjà dans une table/partie active)
    id_table: Optional[str] = None
    id_partie: Optional[str] = None
    statut_table: Optional[str] = None
    skin_jeu: Optional[str] = None


class ReponseContexteReprise(BaseModel):
    """
    Contexte minimal permettant au front de reprendre une partie si le joueur
    est déjà impliqué dans une table active.
    """
    id_joueur: str
    id_table: Optional[str] = None
    id_partie: Optional[str] = None
    statut_table: Optional[str] = None
    skin_jeu: Optional[str] = None


class JoueurPublic(BaseModel):
    id_joueur: str
    nom: str
    alias: str
    courriel: EmailStr


# --- tables ---


class DemandeCreationTable(BaseModel):
    id_hote: str
    nom_table: str
    nb_sieges: int
    mot_de_passe_table: str | None = None
    skin_jeu: str | None = None


class ReponseTable(BaseModel):
    id_table: str
    nom_table: str
    nb_sieges: int
    id_hote: str
    statut: str
    skin_jeu: str | None = None

    @classmethod
    def from_table(cls, table: Table) -> "ReponseTable":
        """Convertit une entité Table du domaine en DTO de réponse API."""
        statut = table.statut.value if isinstance(table.statut, StatutTable) else str(table.statut)
        return cls(
            id_table=table.id_table,
            nom_table=table.nom_table,
            nb_sieges=table.nb_sieges,
            id_hote=table.id_hote,
            statut=statut,
            skin_jeu=table.skin_jeu,
        )


class DemandePriseSiege(BaseModel):
    """
    Demande pour prendre un siège à une table.
    Utilisée par l'API: POST /api/tables/{id_table}/joueurs
    """

    id_joueur: str
    role: Literal["hote", "invite"] = "invite"


class ReponseJoueurSiege(BaseModel):
    id_table: str
    id_joueur: str
    role: Literal["hote", "invite"]
    statut_table: str


class ReponseListeTables(BaseModel):
    tables: list[ReponseTable]


class DemandeJoueurPret(BaseModel):
    id_joueur: str


class DemandeLancerPartie(BaseModel):
    id_hote: str


class ReponsePartieLancee(BaseModel):
    id_partie: str

class ReponseJoueur(BaseModel):
    id_joueur: str
    nom: str
    alias: Optional[str] = None
    courriel: EmailStr


class ReponseListeJoueursLobby(BaseModel):
    joueurs: List[ReponseJoueur]


class ReponseJoueurTable(BaseModel):
    id_joueur: str
    nom: str
    alias: Optional[str] = None
    courriel: EmailStr
    role: Literal["hote", "invite"]
    pret: bool


class ReponseListeJoueursTable(BaseModel):
    id_table: str
    joueurs: List[ReponseJoueurTable]

# --- skins ---

class SkinInfo(BaseModel):
    id_skin: str
    nom: str
    description: Optional[str] = None

class ReponseListeSkins(BaseModel):
    skins: List[SkinInfo]


