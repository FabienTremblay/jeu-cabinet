# services/cabinet/tests/test_events_domaine.py

from services.cabinet.moteur.events import make_evt_from_op
from services.cabinet.moteur.etat import Etat, ProgrammeTour
from services.cabinet.moteur.manager import PartieManager

def test_make_evt_from_op_axes_delta():
    cmd = {"op": "axes.delta", "axe": "social", "delta": 1}
    evt = make_evt_from_op("P1", cmd["op"], cmd)

    assert evt.aggregate_type == "partie"
    assert evt.aggregate_id == "P1"

    assert evt.op_code == "axes.delta"
    assert evt.op_family == "D100"
    assert evt.category == "AXES"
    assert evt.event_type == "cab.D100.axes.delta"

    assert evt.data == cmd
    assert evt.recipients == ["ALL"]
    assert evt.requires_action is False


def test_make_evt_from_op_joueur_vote_set():
    cmd = {"op": "joueur.vote.set", "joueur_id": "J1", "valeur": 1}
    evt = make_evt_from_op("P1", cmd["op"], cmd)

    assert evt.op_family == "D200"
    assert evt.category == "JOUEUR"
    assert evt.event_type == "cab.D200.joueur.vote.set"
    assert evt.data["joueur_id"] == "J1"
    assert evt.data["valeur"] == 1

from services.cabinet.moteur.etat import Etat, Axe, Economie, Joueur

from services.cabinet.moteur.events import EvenementDomaine

def test_appliquer_commandes_genere_evenements_domaine(etat_minimal):
    etat = etat_minimal
    commandes = [
        {"op": "axes.delta", "axe": "social", "delta": 1},
        {"op": "joueur.vote.set", "joueur_id": "J1", "valeur": 1},
    ]

    etat.appliquer_commandes(commandes)
    evenements = etat.vider_evenements()


    # 1) on a un événement "core" par commande.
    # Des événements secondaires (ex: notif.joueur, journal) peuvent s'ajouter.
    assert all(isinstance(e, EvenementDomaine) for e in evenements)
    evenements_core = [e for e in evenements if e.op_code in {"axes.delta", "joueur.vote.set"}]
    assert len(evenements_core) == 2

    codes = {e.op_code for e in evenements_core}
    assert codes == {"axes.delta", "joueur.vote.set"}

    # 2) mapping cohérent
    evt_axes = next(e for e in evenements_core if e.op_code == "axes.delta")
    assert evt_axes.op_family == "D100"
    assert evt_axes.category == "AXES"
    assert evt_axes.event_type == "cab.D100.axes.delta"
    assert evt_axes.data == commandes[0]

    evt_vote = next(e for e in evenements_core if e.op_code == "joueur.vote.set")
    assert evt_vote.op_family == "D200"
    assert evt_vote.category == "JOUEUR"
    assert evt_vote.event_type == "cab.D200.joueur.vote.set"
    assert evt_vote.data == commandes[1]

    # 3) le tampon est bien vidé
    assert etat.vider_evenements() == []

def test_demarrer_partie_emet_phase_set(etat_minimal):
    etat = etat_minimal
    assert etat.phase == "mise_en_place"

    etat.demarrer_partie()
    evenements = etat.vider_evenements()

    # on s’attend à au moins un événement phase.set
    evt = next(e for e in evenements if e.op_code == "phase.set")
    assert evt.op_family == "D600"
    assert evt.category == "DEROULEMENT"
    assert evt.event_type == "cab.D600.phase.set"
    assert evt.data["phase"] == "tour"
    # v1 : la sous-phase initiale n'est pas garantie (souvent None / init_tour selon intégration).
    # le contrat durable est "phase=tour".
    assert evt.data.get("sous_phase") in (None, "init_tour", "monde")

def test_enregistrer_vote_programme_emet_evt_vote(etat_minimal):
    etat = etat_minimal
    etat.programme = None  # ou ProgrammeTour() si besoin

    etat.programme = ProgrammeTour(entrees=[], votes={})
    etat.appliquer_commandes([{
        "op": "programme.vote.set",
        "joueur_id": "J1",
        "valeur": +1,
    }])
    evenements = etat.vider_evenements()

    evt = next(e for e in evenements if e.op_code == "programme.vote.set")
    assert evt.op_family == "D500"
    assert evt.category == "PROGRAMME"
    assert evt.event_type == "cab.D500.programme.vote.set"
    assert evt.data["joueur_id"] == "J1"
    assert evt.data["valeur"] in (1, True)  # selon comment tu l’as encodé

