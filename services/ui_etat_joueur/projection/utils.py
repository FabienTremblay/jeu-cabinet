# services/ui_etat_joueur/projection/utils.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Literal


def parse_occurred_at(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        # compat ISO8601, y compris suffixe Z
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except Exception:
        return datetime.now(timezone.utc)

def normaliser_severity(val: Optional[str]) -> Literal["info", "warn", "error"]:
    """
    Normalise la sévérité en contrat UI (info|warn|error), sans compat.

    Entrées possibles:
    - moteur (EvenementDomaine): info|warning|critical
    - UI / legacy: warn|error|info
    - (ancien) success -> devient info
    """
    v = (val or "").strip().lower()
    if v in {"warning"}:
        return "warn"
    if v in {"critical"}:
        return "error"
    if v in {"warn", "error", "info"}:
        return v  # déjà conforme UI
    if v in {"success", "ok", "passed"}:
        return "info"
    return "info"



def audience_depuis_recipients(recipients: list[str] | None) -> Dict[str, Any]:
    """
    Convertit la liste recipients du moteur en audience structurée.
    - ["ALL"] → {"scope":"all"}
    - ["J000001"] → {"scope":"joueur","joueur_id":"J000001"}
    - ["J1","J2"] → {"scope":"liste","joueurs":["J1","J2"]}
    """
    r = recipients or []
    if r == ["ALL"]:
        return {"scope": "all"}
    if len(r) == 1:
        return {"scope": "joueur", "joueur_id": r[0]}
    return {"scope": "liste", "joueurs": list(r)}


def meta_propre(meta: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Garantit un dict JSON sérialisable et évite d'injecter des structures trop grosses.
    Utilise ceci pour filtrer/trim si nécessaire.
    """
    return dict(meta or {})
