# services/ui_etat_joueur/projection/partie.py
from __future__ import annotations

from .utils import parse_occurred_at, audience_depuis_recipients


def traiter_partie(depot, evt: dict) -> None:
    aggregate_id = evt.get("aggregate_id")
    data = evt.get("data", {}) or {}
    recipients = evt.get("recipients", ["ALL"])
    audience = audience_depuis_recipients(recipients)
    op_code = evt.get("op_code") or data.get("op") or ""
    when = parse_occurred_at(evt.get("occurred_at"))

    if op_code == "partie.terminer":
        raison = data.get("raison", "Partie terminée")
        if aggregate_id:
            depot.maj_etat_partie_par_partie(
                partie_id=aggregate_id,
                phase="TERMINEE",
            )
            depot.maj_marqueur_partie_par_partie(aggregate_id, when)

        message = data.get("ui_message") or f"Partie terminée : {raison}"
        depot.journal_par_recipients(
            aggregate_id=aggregate_id,
            recipients=recipients if recipients else ["ALL"],
            message=message,
            event_id=evt.get("event_id"),
            occurred_at=when,
            category="SYSTEME",
            severity="info",
            code="system.partie.terminee",
            meta={
                "aggregate_id": aggregate_id,
                "op_family": evt.get("op_family"),
                "op_code": op_code,
                "raison": raison,
            },
            audience=audience,
            op_code=op_code,
            raw=evt,
        )
    else:
        # Autres événements de partie : pour l'instant, pas de journal,
        # mais on peut garder le marqueur "partie" à jour.
        if aggregate_id:
            depot.maj_marqueur_partie_par_partie(aggregate_id, when)

