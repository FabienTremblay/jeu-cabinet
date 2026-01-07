# services/ui_etat_joueur/schemas.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from .domaine import (
    ActionDisponible,
    AncrageJoueur,
    EntreeJournal,
    EtatJoueurUI,
    EtatPartieResume,
    MarqueursMaj,
)


class AncrageDTO(BaseModel):
    type: Literal["lobby", "table", "partie"]
    table_id: Optional[str] = None
    partie_id: Optional[str] = None


class EtatPartieDTO(BaseModel):
    phase: Optional[str] = None
    sous_phase: Optional[str] = None
    tour: Optional[int] = None


class ActionDisponibleDTO(BaseModel):
    code: str
    label: str
    payload: Dict[str, Any] = {}
    requires_confirmation: bool = False


class EntreeJournalDTO(BaseModel):
    event_id: Optional[str] = None
    occurred_at: datetime
    category: Optional[str] = None
    severity: Optional[str] = None
    message: str
    # champs optionnels (ajoutés sans briser v1)
    code: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    audience: Optional[Dict[str, Any]] = None


class MarqueursMajDTO(BaseModel):
    partie: Optional[datetime] = None
    actions: Optional[datetime] = None
    info_axes: Optional[datetime] = None
    info_cartes: Optional[datetime] = None


class SituationJoueurDTO(BaseModel):
    version: int = 1
    joueur_id: str
    ancrage: AncrageDTO
    etat_partie: EtatPartieDTO
    actions_disponibles: List[ActionDisponibleDTO]
    journal_recent: List[EntreeJournalDTO]
    marqueurs: MarqueursMajDTO


def _map_ancrage(a: AncrageJoueur) -> AncrageDTO:
    return AncrageDTO(type=a.type, table_id=a.table_id, partie_id=a.partie_id)


def _map_etat_partie(ep: EtatPartieResume) -> EtatPartieDTO:
    return EtatPartieDTO(phase=ep.phase, sous_phase=ep.sous_phase, tour=ep.tour)


def _map_action(a: ActionDisponible) -> ActionDisponibleDTO:
    return ActionDisponibleDTO(
        code=a.code,
        label=a.label,
        payload=dict(a.payload),
        requires_confirmation=a.requires_confirmation,
    )


def _map_entree_journal(e: EntreeJournal) -> EntreeJournalDTO:
    return EntreeJournalDTO(
        event_id=e.event_id,
        occurred_at=e.occurred_at,
        category=e.category,
        severity=e.severity,
        message=e.message,
        code=e.code,
        meta=dict(e.meta),
        audience=dict(e.audience) if e.audience is not None else None,
    )


def _map_marqueurs(m: MarqueursMaj) -> MarqueursMajDTO:
    return MarqueursMajDTO(
        partie=m.partie,
        actions=m.actions,
        info_axes=m.info_axes,
        info_cartes=m.info_cartes,
    )


def mapper_etat_to_dto(etat: EtatJoueurUI) -> SituationJoueurDTO:
    return SituationJoueurDTO(
        joueur_id=etat.joueur_id,
        ancrage=_map_ancrage(etat.ancrage),
        etat_partie=_map_etat_partie(etat.etat_partie),
        actions_disponibles=[_map_action(a) for a in etat.actions_disponibles],
        journal_recent=[_map_entree_journal(e) for e in etat.journal_recent],
        marqueurs=_map_marqueurs(etat.marqueurs),
    )

