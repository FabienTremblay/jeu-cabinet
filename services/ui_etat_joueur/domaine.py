# services/ui_etat_joueur/domaine.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional


TypeAncrage = Literal["lobby", "table", "partie"]


@dataclass
class AncrageJoueur:
    type: TypeAncrage = "lobby"
    table_id: Optional[str] = None
    partie_id: Optional[str] = None


@dataclass
class EtatPartieResume:
    phase: Optional[str] = None
    sous_phase: Optional[str] = None
    tour: Optional[int] = None


@dataclass
class ActionDisponible:
    code: str
    label: str
    payload: Dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False


@dataclass
class EntreeJournal:
    event_id: Optional[str]
    occurred_at: datetime
    category: Optional[str]
    severity: Optional[str]
    message: str
    # champs optionnels (ajoutés sans briser v1)
    code: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)
    audience: Optional[Dict[str, Any]] = None
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MarqueursMaj:
    """
    Marqueurs de dernière mise à jour par "section" de la vue.

    - partie : début / fin de partie, changement de phase / tour
    - actions : début / fin d'une attente (intervention joueur)
    - info_axes : modifications de capital, axes, analyses, etc.
    - info_cartes : pioches, défausses, cartes jouées, etc.
    """
    partie: Optional[datetime] = None
    actions: Optional[datetime] = None
    info_axes: Optional[datetime] = None
    info_cartes: Optional[datetime] = None


@dataclass
class EtatJoueurUI:
    joueur_id: str
    ancrage: AncrageJoueur = field(default_factory=AncrageJoueur)
    etat_partie: EtatPartieResume = field(default_factory=EtatPartieResume)
    actions_disponibles: List[ActionDisponible] = field(default_factory=list)
    journal_recent: List[EntreeJournal] = field(default_factory=list)
    marqueurs: MarqueursMaj = field(default_factory=MarqueursMaj)

    def ajouter_journal(
        self,
        message: str,
        event_id: Optional[str] = None,
        occurred_at: Optional[datetime] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        code: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        audience: Optional[Dict[str, Any]] = None,
        raw: Optional[Dict[str, Any]] = None,
        max_items: int = 50,
    ) -> None:

        # Normaliser occurred_at : toujours "aware" UTC.
        # But: éviter TypeError lors du tri (naive vs aware).
        when = occurred_at or datetime.now(timezone.utc)
        if when.tzinfo is None or when.tzinfo.utcoffset(when) is None:
            # On interprète les datetimes naïfs comme UTC.
            when = when.replace(tzinfo=timezone.utc)

        entree = EntreeJournal(
            event_id=event_id,
            occurred_at=when,
            category=category,
            severity=severity,
            message=message,
            code=code,
            meta=meta or {},
            audience=audience,
            raw=raw or {},
        )
        self.journal_recent.append(entree)

        # garantie d'ordre chronologique ascendant (contrat UI)
        self.journal_recent.sort(key=lambda e: e.occurred_at)

        # taille limitée (contrat UI)
        if len(self.journal_recent) > max_items:
            self.journal_recent = self.journal_recent[-max_items:]

    def reset_actions(self) -> None:
        self.actions_disponibles.clear()

    def set_actions(self, actions: List[ActionDisponible]) -> None:
        self.actions_disponibles = list(actions)

