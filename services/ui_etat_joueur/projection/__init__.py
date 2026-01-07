# services/ui_etat_joueur/projection/__init__.py
from __future__ import annotations

from .attente import traiter_attente
from .autres import traiter_autres
from .notifications import traiter_notification
from .partie import traiter_partie
from .phase import traiter_phase
from .tour import traiter_tour


def appliquer_projection_evenement_domaine(depot, evt: dict) -> None:
    """
    Route un EvenementDomaine vers le bon module de projection.

    evt est supposé contenir au minimum :
      - event_id
      - event_type
      - category
      - op_code
      - aggregate_id
      - recipients
      - occurred_at
      - data
    """
    category = evt.get("category")
    op_code = evt.get("op_code") or ""
    if not category:
        traiter_autres(depot, evt)
        return

    if category == "DEROULEMENT":
        if op_code.startswith("phase."):
            traiter_phase(depot, evt)
        elif op_code.startswith("tour."):
            traiter_tour(depot, evt)
        elif op_code.startswith("attente."):
            traiter_attente(depot, evt)
        elif op_code.startswith("partie."):
            traiter_partie(depot, evt)
        elif op_code.startswith("notif.") or op_code.startswith("journal"):
            traiter_notification(depot, evt)
        else:
            traiter_autres(depot, evt)
    else:
        # toutes les autres catégories : marqueurs uniquement
        traiter_autres(depot, evt)

