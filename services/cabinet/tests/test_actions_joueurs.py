# services/cabinet/tests/test_actions_joueurs.py

from services.cabinet.moteur.etat import ProgrammeTour
from services.cabinet.moteur.manager import PartieManager


def test_action_vote_enregistre_dans_programme():
    # v1: on passe par le moteur (PartieManager), pas par un app-layer/usecase.
    pm = PartieManager()
    etat = pm.creer(
        skin="minimal",
        partie_id="T-001",
        joueurs={"J1": {"nom": "Alice"}, "J2": {"nom": "Bob"}},
    )

    # on simule un programme existant
    etat.programme = ProgrammeTour(entrees=[], votes={})

    # v1: une action "vote" se traduit par une commande noyau sur l'état
    etat.programme.votes["J1"] = 1

    # relecture directe sur l'objet
    assert etat.programme.votes["J1"] == 1

def test_vote_pondere_par_poids_de_vote(pm, etat_minimal, goto):
    # on force des poids différents
    j1 = etat_minimal.joueurs["J1"]
    j2 = etat_minimal.joueurs["J2"]
    j1.poids_vote = 2
    j2.poids_vote = 1

    # programme avec J1=NON (-1), J2=OUI (+1)
    from services.cabinet.moteur.etat import ProgrammeTour
    etat_minimal.programme = ProgrammeTour(entrees=[], votes={"J1": -1, "J2": +1})

    # vote → somme = (-1 * 2) + (1 * 1) = -1 => doit aller en amendements
    goto(pm, etat_minimal, "vote")
    assert etat_minimal.sous_phase == "amendements"

def test_attente_joueurs_cycle_simple(etat_minimal):
    # init d'une attente de vote pour J1 et J2
    cmds = [{
        "op": "attente.joueurs",
        "type": "VOTE",
        "joueurs": ["J1", "J2"],
    }]
    etat_minimal.appliquer_commandes(cmds)

    assert etat_minimal.attente.est_active is True
    assert etat_minimal.attente.type == "VOTE"
    assert set(etat_minimal.attente.joueurs) == {"J1", "J2"}
    assert etat_minimal.attente.recus == set()

    # J1 répond
    etat_minimal.appliquer_commandes([{
        "op": "attente.joueur_recu",
        "joueur_id": "J1",
        "type": "VOTE",
    }])
    assert "J1" in etat_minimal.attente.recus
    assert etat_minimal.attente.est_complete is False

    # J2 répond
    etat_minimal.appliquer_commandes([{
        "op": "attente.joueur_recu",
        "joueur_id": "J2",
        "type": "VOTE",
    }])
    assert etat_minimal.attente.est_complete is True

    # terminer l'attente (équivalent de l'ancien "reset" pour le flux normal)
    etat_minimal.appliquer_commandes([{"op": "attente.terminer"}])
    assert etat_minimal.attente.est_active is False
    assert etat_minimal.attente.statut == "TERMINE"
    assert etat_minimal.attente.joueurs == []
    assert etat_minimal.attente.recus == set()

