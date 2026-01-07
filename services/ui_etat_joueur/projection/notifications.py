# services/ui_etat_joueur/projection/notifications.py
from __future__ import annotations

from .utils import parse_occurred_at, audience_depuis_recipients, normaliser_severity
 


def traiter_notification(depot, evt: dict) -> None:
    aggregate_id = evt.get("aggregate_id")
    data = evt.get("data", {}) or {}
    recipients = evt.get("recipients", ["ALL"])
    audience = audience_depuis_recipients(recipients)
    op_code = evt.get("op_code") or ""

    # Supporte la forme notif.joueur produite par le moteur:
    # data = { op:"notif.joueur", joueur_id, code, payload:{message, refs, ...} }
    payload = data.get("payload") or {}

    message = (
        data.get("message")
        or payload.get("message")
        or (data.get("ui") or {}).get("message")
        or data.get("ui_message")
    )

    # Pas de message exploitable → on ignore, c'est du bruit
    if not message:
        return

    when = parse_occurred_at(evt.get("occurred_at"))
    sev = normaliser_severity(evt.get("severity"))

    # code stable si fourni par le moteur
    code = data.get("code") or payload.get("code")
    refs = payload.get("refs") or data.get("refs") or {}

    depot.journal_par_recipients(
        aggregate_id=aggregate_id,
        recipients=recipients,
        message=message,
        event_id=evt.get("event_id"),
        occurred_at=when,
        category="MESSAGE",
        severity=sev,
        code=code or (f"message.{op_code}" if op_code else "message.notification"),
        meta={
            "aggregate_id": aggregate_id,
            "op_family": evt.get("op_family"),
            "op_code": op_code,
            "refs": refs,
        },
        audience=audience,
        op_code=op_code,
        raw=evt,
    )

