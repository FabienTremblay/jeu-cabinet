# services/ui_etat_joueur/projection/autres.py
from __future__ import annotations

from .utils import parse_occurred_at


def traiter_autres(depot, evt: dict) -> None:
    """
    Traite les catégories non DEROULEMENT.

    Ici, on applique ton principe :
    - l'événement sert au marquage ("quelque chose a changé dans cette section"),
    - mais on ne pollue pas le journal du joueur avec des détails techniques.
    """
    aggregate_id = evt.get("aggregate_id")
    category = evt.get("category") or "AUTRE"
    when = parse_occurred_at(evt.get("occurred_at"))

    if not aggregate_id:
        return

    # AXES / ANALYSE → info_axes
    if category in {"AXES", "ANALYSE"}:
        depot.maj_marqueur_info_axes_par_partie(aggregate_id, when)

    # JOUEUR / DECK / PROGRAMME / MONDE → info_cartes
    elif category in {"JOUEUR", "DECK", "PROGRAMME", "MONDE"}:
        depot.maj_marqueur_info_cartes_par_partie(aggregate_id, when)

    # autres catégories (si tu en ajoutes) : pour l'instant, pas de journal
    else:
        # on pourrait décider de marquer info_axes ou info_cartes par défaut,
        # mais pour l’instant on ne fait rien.
        return

