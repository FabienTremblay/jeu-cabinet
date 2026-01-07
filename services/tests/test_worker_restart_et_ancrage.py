# services/tests/test_worker_restart_et_ancrage.py
from services.ui_etat_joueur.repository import DepotEtatsUI
from services.ui_etat_joueur.kafka_consumer import ConsommateurEvenementsUI


def _make_consumer_sans_kafka(depot: DepotEtatsUI) -> ConsommateurEvenementsUI:
    c = object.__new__(ConsommateurEvenementsUI)
    c._depot = depot
    c._fin_partie = None
    return c


def test_auto_ancrage_sur_attente_joueurs():
    depot = DepotEtatsUI()
    c = _make_consumer_sans_kafka(depot)

    evt = {
        # volontairement sans event_id : le worker/consumer doit le stabiliser en amont,
        # mais ici on teste surtout l'auto-ancrage
        "event_type": "cab.D600.attente.joueurs",
        "occurred_at": "2025-12-12T14:54:33.690580+00:00",
        "aggregate_id": "P000002",
        "op_family": "D600",
        "op_code": "attente.joueurs",
        "recipients": ["ALL"],
        "data": {"joueurs": ["J000001", "J000002"], "type": "ENGAGER_CARTE"},
    }

    c._traiter_evenement_moteur(evt)

    # Les deux doivent maintenant être ancrés sur la partie
    assert depot.obtenir_ou_creer("J000001").ancrage.partie_id == "P000002"
    assert depot.obtenir_ou_creer("J000002").ancrage.partie_id == "P000002"


def test_restart_replay_ne_perd_pas_les_ancrages():
    depot = DepotEtatsUI()

    # premier "run"
    c1 = _make_consumer_sans_kafka(depot)
    evt = {
        "event_type": "cab.D600.attente.joueurs",
        "occurred_at": "2025-12-12T14:54:33.690580+00:00",
        "aggregate_id": "P000002",
        "op_family": "D600",
        "op_code": "attente.joueurs",
        "recipients": ["ALL"],
        "data": {"joueurs": ["J000001", "J000002"], "type": "ENGAGER_CARTE"},
    }
    c1._traiter_evenement_moteur(evt)

    # "restart" : nouveau consumer, même dépôt
    c2 = _make_consumer_sans_kafka(depot)
    c2._traiter_evenement_moteur(evt)  # replay

    assert depot.obtenir_ou_creer("J000001").ancrage.partie_id == "P000002"
    assert depot.obtenir_ou_creer("J000002").ancrage.partie_id == "P000002"
