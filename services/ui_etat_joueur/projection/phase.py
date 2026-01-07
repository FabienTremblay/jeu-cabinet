# services/ui_etat_joueur/projection/phase.py
from __future__ import annotations

from .utils import parse_occurred_at, audience_depuis_recipients


def traiter_phase(depot, evt: dict) -> None:
    aggregate_id = evt.get("aggregate_id")
    data = evt.get("data", {}) or {}
    recipients = evt.get("recipients", ["ALL"])
    audience = audience_depuis_recipients(recipients)
    op_code = evt.get("op_code") or ""

    phase = data.get("phase")
    sous_phase = data.get("sous_phase")
    tour = data.get("tour")
    when = parse_occurred_at(evt.get("occurred_at"))

    if aggregate_id:
        depot.maj_etat_partie_par_partie(
            partie_id=aggregate_id,
            phase=phase,
            sous_phase=sous_phase,
            tour=tour,
        )
        depot.maj_marqueur_partie_par_partie(aggregate_id, when)

    # On garde un message pour le joueur : changement de phase = événement fort
    message = data.get("ui_message")
    if not message:
        if phase and sous_phase:
            message = f"Phase {phase} / {sous_phase}"
        elif phase:
            message = f"Phase {phase}"
        else:
            message = "Changement de phase"

    depot.journal_par_recipients(
        aggregate_id=aggregate_id,
        recipients=recipients,
        message=message,
        event_id=evt.get("event_id"),
        occurred_at=when,
        category=evt.get("category"),
        severity=evt.get("severity"),
        code=f"deroulement.{op_code}" if op_code else "deroulement.phase",
        meta={
            "aggregate_id": aggregate_id,
            "op_family": evt.get("op_family"),
            "op_code": op_code,
            "phase": phase,
            "sous_phase": sous_phase,
            "tour": tour,
        },
        audience=audience,
        op_code=op_code,
        raw=evt,
    )

