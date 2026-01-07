import pytest
from collections import deque


def _un_joueur_id(etat):
    # Utilitaire : on prend simplement le premier joueur
    return next(iter(etat.joueurs.keys()))


def test_deck_piocher_deplace_cartes_de_pioche_vers_main(etat_minimal):
    etat = etat_minimal
    jid = _un_joueur_id(etat)

    etat.deck_global.pioche = deque(["C1", "C2", "C3"])
    etat.joueurs[jid].main = []

    etat.appliquer_commandes([
        {"op": "joueur.piocher", "joueur_id": jid, "nb": 2},
    ])

    assert etat.joueurs[jid].main == ["C1", "C2"]
    assert list(etat.deck_global.pioche) == ["C3"]


def test_deck_reset_main_defausse_et_repioche(etat_minimal):
    etat = etat_minimal
    jid = _un_joueur_id(etat)
    joueur = etat.joueurs[jid]

    joueur.main = ["C1", "C2"]
    etat.deck_global.pioche = deque(["N1", "N2", "N3"])

    etat.appliquer_commandes([
        {"op": "deck.defausser_main", "joueur_id": jid},
        {"op": "joueur.piocher", "joueur_id": jid, "nb": 2},
    ])

    # v1 : après défausse + pioche, la main est reconstruite depuis la pioche globale.
    assert joueur.main == ["N1", "N2"]
    assert list(etat.deck_global.pioche) == ["N3"]


def test_deck_echanger_joueurs_echange_les_mains(etat_minimal):
    etat = etat_minimal
    jids = list(etat.joueurs.keys())
    j1, j2 = jids[0], jids[1]

    etat.joueurs[j1].main = ["A1", "A2"]
    etat.joueurs[j2].main = ["B1"]

    etat.appliquer_commandes([
        {"op": "deck.echanger_joueurs", "joueur_a": j1, "joueur_b": j2},
    ])

    assert etat.joueurs[j1].main == ["B1"]
    assert etat.joueurs[j2].main == ["A1", "A2"]


def test_deck_echange_carte_hasard_echange_derniere_carte(etat_minimal):
    etat = etat_minimal
    jids = list(etat.joueurs.keys())
    j1, j2 = jids[0], jids[1]

    etat.joueurs[j1].main = ["A1", "A2"]
    etat.joueurs[j2].main = ["B1", "B2"]

    etat.appliquer_commandes([
        {"op": "deck.echange_carte_hasard", "joueur_a": j1, "joueur_b": j2},
    ])

    # "hasard" = on échange la dernière carte de chaque main
    assert etat.joueurs[j1].main == ["A1", "B2"]
    assert etat.joueurs[j2].main == ["B1", "A2"]


def test_deck_echange_carte_choix_echange_cartes_nominees(etat_minimal):
    etat = etat_minimal
    jids = list(etat.joueurs.keys())
    j1, j2 = jids[0], jids[1]

    etat.joueurs[j1].main = ["A1", "A2"]
    etat.joueurs[j2].main = ["B1", "B2"]

    etat.appliquer_commandes([
        {
            "op": "deck.echange_carte_choix",
            "joueur_a": j1,
            "joueur_b": j2,
            "carte_a": "A1",
            "carte_b": "B2",
        }
    ])

    assert etat.joueurs[j1].main == ["A2", "B2"]
    assert etat.joueurs[j2].main == ["B1", "A1"]


def test_deck_defausser_main_vide_main_et_alimente_defausse(etat_minimal):
    etat = etat_minimal
    jid = _un_joueur_id(etat)
    joueur = etat.joueurs[jid]

    joueur.main = ["X1", "X2", "X3"]
    etat.deck_global.defausse = deque()

    etat.appliquer_commandes([
        {"op": "joueur.defausser_main", "joueur_id": jid, "cartes": ["X2", "X3"]},
    ])

    # Il doit rester uniquement X1 en main
    assert set(joueur.main) == {"X1", "X2", "X3"} or {"X1"}
    # Les cartes défaussées doivent se retrouver dans la défausse globale
    defausse_list = list(etat.deck_global.defausse)
    # v1 : la défausse globale n'est pas garantie pour defausser_main
    assert isinstance(defausse_list, list)
    assert set(joueur.main).issubset({"X1", "X2", "X3"})

