# services/tests/test_projection_attente_et_notif.py
import datetime as dt

from services.ui_etat_joueur.repository import DepotEtatsUI
from services.ui_etat_joueur.projection.attente import traiter_attente
from services.ui_etat_joueur.projection.notifications import traiter_notification


def test_projection_attente_joueurs_produit_entree_action():
    depot = DepotEtatsUI()

    evt = {
        "event_id": "E-ATT-1",
        "event_type": "cab.D600.attente.joueurs",
        "occurred_at": "2025-12-12T14:54:33.690580+00:00",
        "aggregate_id": "P000002",
        "op_family": "D600",
        "op_code": "attente.joueurs",
        "category": "DEROULEMENT",  # sera forcé ACTION par la projection attente
        "severity": "info",
        "recipients": ["ALL"],
        "data": {
            "op": "attente.joueurs",
            "type": "ENGAGER_CARTE",
            "joueurs": ["J000001", "J000002"],
            "procedure": {
                "code": "ENGAGER_PROGRAMME",
                "titre": "Confection du programme du cabinet",
                "ui": {"ecran": "programme"},
            },
        },
    }

    traiter_attente(depot, evt)

    # Chaque joueur a une entrée (ciblée joueur par joueur dans ta projection)
    e1 = depot.obtenir_ou_creer("J000001").journal_recent[-1]
    e2 = depot.obtenir_ou_creer("J000002").journal_recent[-1]

    assert e1.category == "ACTION"
    assert e1.severity == "info"
    assert e1.code == "action.attente.ouverte"
    assert e1.meta["type_attente"] == "ENGAGER_CARTE"
    assert e1.meta["procedure_code"] == "ENGAGER_PROGRAMME"
    assert e1.audience["scope"] == "joueur"
    assert e1.audience["joueur_id"] == "J000001"

    assert e2.code == "action.attente.ouverte"
    assert e2.audience["scope"] == "joueur"
    assert e2.audience["joueur_id"] == "J000002"


def test_projection_notif_joueur_est_ciblee():
    depot = DepotEtatsUI()

    evt = {
        "event_id": "E-NOTIF-1",
        "event_type": "cab.D600.notif.joueur",
        "occurred_at": "2025-12-12T14:55:00.000000+00:00",
        "aggregate_id": "P000002",
        "op_family": "D600",
        "op_code": "notif.joueur",
        "category": "DEROULEMENT",
        "severity": "warn",
        "recipients": ["J000002"],
        "data": {
            "op": "notif.joueur",
            "message": "Action refusée.",
        },
    }

    traiter_notification(depot, evt)

    assert len(depot.obtenir_ou_creer("J000002").journal_recent) == 1
    assert len(depot.obtenir_ou_creer("J000001").journal_recent) == 0

    e = depot.obtenir_ou_creer("J000002").journal_recent[0]
    assert e.category in ("MESSAGE", "ACTION")  # selon ton choix final
    assert e.severity == "warn"
    assert e.message
