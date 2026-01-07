# services/api_moteur/schemas.py
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

class ReponseEtat(BaseModel):
    partie_id: str
    etat: Dict[str, Any]

class RequetePartie(BaseModel):
    partie_id: Optional[str] = None
    nom: str                                # ex.: "demo" (skin/config de base)
    joueurs: Dict[str, Any]
    seed: Optional[int] = None              # optionnel, pour tests/reproductibilité
    skin_jeu: Optional[str] = "minimal"
    options: Dict[str, Any] = Field(default_factory=dict)

class RequeteJoueur(BaseModel):
    joueur_id: str
    pseudo: str

class RequeteAction(BaseModel):
    acteur: str
    type_action: str
    donnees: Dict[str, Any] = Field(default_factory=dict)

class RequeteDecision(BaseModel):
    table: str
    contexte: Dict[str, Any]

class Erreur(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None

