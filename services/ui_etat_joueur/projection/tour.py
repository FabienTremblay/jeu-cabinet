# services/ui_etat_joueur/projection/tour.py
from __future__ import annotations

from .utils import parse_occurred_at, audience_depuis_recipients


def traiter_tour(depot, evt: dict) -> None:
    aggregate_id = evt.get("aggregate_id")
    data = evt.get("data", {}) or {}
    recipients = evt.get("recipients", ["ALL"])
    audience = audience_depuis_recipients(recipients)
    op_code = evt.get("op_code") or ""

    tour = data.get("tour")
    when = parse_occurred_at(evt.get("occurred_at"))

    if aggregate_id and tour is not None:
        depot.maj_etat_partie_par_partie(
            partie_id=aggregate_id,
            tour=tour,
        )
        depot.maj_marqueur_partie_par_partie(aggregate_id, when)

    message = data.get("ui_message") or (
        f"Début du tour {tour}" if tour is not None else "Changement de tour"
    )

    depot.journal_par_recipients(
        aggregate_id=aggregate_id,
        recipients=recipients,
        message=message,
        event_id=evt.get("event_id"),
        occurred_at=when,
        category=evt.get("category"),
        severity=evt.get("severity"),
        code=f"deroulement.{op_code}" if op_code else "deroulement.tour",
        meta={
            "aggregate_id": aggregate_id,
            "op_family": evt.get("op_family"),
            "op_code": op_code,
            "tour": tour,
        },
        audience=audience,
        op_code=op_code,
        raw=evt,
    )

