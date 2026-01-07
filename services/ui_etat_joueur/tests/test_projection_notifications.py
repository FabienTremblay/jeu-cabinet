# services/ui_etat_joueur/tests/test_projection_notifications.py
from __future__ import annotations

from datetime import datetime, timezone

from services.ui_etat_joueur.projection.notifications import traiter_notification


class DepotSpy:
    def __init__(self) -> None:
        self.calls = []

    def journal_par_recipients(
        self,
        aggregate_id,
        recipients,
        message,
        event_id,
        occurred_at,
        category,
        severity,
        code,
        meta,
        audience,
        op_code,
        raw,
    ):
        self.calls.append(
            {
                "aggregate_id": aggregate_id,
                "recipients": recipients,
                "message": message,
                "event_id": event_id,
                "occurred_at": occurred_at,
                "category": category,
                "severity": severity,
                "code": code,
                "meta": meta,
                "audience": audience,
                "op_code": op_code,
                "raw": raw,
            }
        )


def test_notif_joueur_warning_devient_warn_et_cible_joueur():
    depot = DepotSpy()

    evt = {
        "event_id": "E-001",
        "aggregate_id": "P000001",
        "event_type": "evenement.domaine",
        "op_family": "D600",
        "op_code": "notif.joueur",
        "severity": "warning",  # moteur
        "occurred_at": "2025-12-16T15:00:00Z",
        "recipients": ["J000001"],
        "data": {
            "op": "notif.joueur",
            "joueur_id": "J000001",
            "code": "ATTENTION_INSUFFISANTE",
            "payload": {
                "message": "Vous n’avez pas assez d’attention.",
                "refs": {"op": "programme.engager_carte", "carte_id": "MES-004"},
                "requis": 2,
                "disponible": 1,
            },
        },
    }

    traiter_notification(depot, evt)

    assert len(depot.calls) == 1
    call = depot.calls[0]

    assert call["aggregate_id"] == "P000001"
    assert call["recipients"] == ["J000001"]
    assert call["message"] == "Vous n’avez pas assez d’attention."
    assert call["category"] == "MESSAGE"
    assert call["severity"] == "warn"  # warning -> warn (UI)
    assert call["audience"] == {"scope": "joueur", "joueur_id": "J000001"}
    assert call["code"] == "ATTENTION_INSUFFISANTE"
    assert call["meta"]["refs"]["carte_id"] == "MES-004"


def test_notif_joueur_critical_devient_error():
    depot = DepotSpy()

    evt = {
        "event_id": "E-002",
        "aggregate_id": "P000001",
        "event_type": "evenement.domaine",
        "op_family": "D600",
        "op_code": "notif.joueur",
        "severity": "critical",  # moteur
        "occurred_at": "2025-12-16T15:00:01Z",
        "recipients": ["J000001"],
        "data": {
            "op": "notif.joueur",
            "joueur_id": "J000001",
            "code": "INVARIANT_BRISE",
            "payload": {"message": "Erreur interne (invariant brisé)."},
        },
    }

    traiter_notification(depot, evt)

    assert len(depot.calls) == 1
    assert depot.calls[0]["severity"] == "error"  # critical -> error (UI)


def test_notif_ignore_si_message_absent():
    depot = DepotSpy()

    evt = {
        "event_id": "E-003",
        "aggregate_id": "P000001",
        "event_type": "evenement.domaine",
        "op_family": "D600",
        "op_code": "notif.joueur",
        "severity": "warning",
        "occurred_at": "2025-12-16T15:00:02Z",
        "recipients": ["J000001"],
        "data": {"op": "notif.joueur", "joueur_id": "J000001", "code": "X"},
    }

    traiter_notification(depot, evt)

    assert depot.calls == []
