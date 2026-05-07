# services/api_moteur/schemas.py
# rôle        : définit les DTO HTTP de l'API moteur
# usage       : validation des requêtes et réponses FastAPI
# contexte    : création de partie, actions et état moteur
# statut      : actif
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

class ReponseEtat(BaseModel):
    partie_id: str
    etat: Dict[str, Any] = Field(json_schema_extra={"additionalProperties": True})

class PolitiqueTimeoutPartie(BaseModel):
    version: int = 1
    active: bool = True
    delai_inactivite_secondes: int = Field(default=3600, ge=1)

class ConfigurationPartie(BaseModel):
    politique_timeout_partie: Optional[PolitiqueTimeoutPartie] = None

class RequetePartie(BaseModel):
    partie_id: Optional[str] = None
    nom: str                                # ex.: "demo" (skin/config de base)
    joueurs: Dict[str, Any] = Field(json_schema_extra={"additionalProperties": True})
    seed: Optional[int] = None              # optionnel, pour tests/reproductibilité
    skin_jeu: Optional[str] = "minimal"
    configuration_partie: ConfigurationPartie = Field(default_factory=ConfigurationPartie)
    options: Dict[str, Any] = Field(
        default_factory=dict,
        json_schema_extra={"additionalProperties": True},
    )

class RequeteJoueur(BaseModel):
    joueur_id: str
    pseudo: str

class RequeteAction(BaseModel):
    acteur: str
    type_action: str
    donnees: Dict[str, Any] = Field(
        default_factory=dict,
        json_schema_extra={"additionalProperties": True},
    )

class RequeteDecision(BaseModel):
    table: str
    contexte: Dict[str, Any]

class Erreur(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
