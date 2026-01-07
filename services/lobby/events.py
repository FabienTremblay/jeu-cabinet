# services/lobby/events.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, List, Optional

from pydantic import BaseModel, EmailStr


def maintenant_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Evenement(BaseModel):
    """Événement de base envoyé sur Kafka (ou journal)."""
    type: str
    horodatage: str = maintenant_iso()


# --- Événements liés aux joueurs -------------------------------------------------


class EvenementJoueurCree(Evenement):
    type: Literal["JoueurCree"] = "JoueurCree"
    id_joueur: str
    nom: str
    alias: Optional[str] = None
    courriel: EmailStr


class EvenementJoueurIntroduit(Evenement):
    type: Literal["JoueurIntroduit"] = "JoueurIntroduit"
    id_joueur: str
    origine: str


class EvenementJoueurConnecte(Evenement):
    type: Literal["JoueurConnecte"] = "JoueurConnecte"
    id_joueur: str
    origine: str


# --- Événements liés aux tables / parties ---------------------------------------


class EvenementTableCree(Evenement):
    type: Literal["TableCree"] = "TableCree"
    id_table: str
    nom_table: str
    nb_sieges: int
    id_hote: str
    skin_jeu: Optional[str] = None


class EvenementJoueurARejointTable(Evenement):
    type: Literal["JoueurARejointTable"] = "JoueurARejointTable"
    id_table: str
    id_joueur: str
    role: Literal["hote", "invite"]


class EvenementJoueurPret(Evenement):
    type: Literal["JoueurPret"] = "JoueurPret"
    id_table: str
    id_joueur: str

class JoueurPartie(BaseModel):
    """Snapshot minimal du joueur envoyé au moteur quand la partie démarre."""
    id_joueur: str
    nom: str
    alias: str
    courriel: EmailStr
    role: Literal["hote", "invite"]

class EvenementPartieLancee(Evenement):
    type: Literal["PartieLancee"] = "PartieLancee"
    id_table: str
    id_partie: str
    joueurs: List[JoueurPartie]
    skin_jeu: Optional[str] = None


