from collections import deque


def test_evt_piocher_met_evenement_actif_sans_toucher_au_deck_global(etat_minimal):
    etat = etat_minimal

    # deck d'événements isolé
    etat.deck_events.pioche = deque(["E1", "E2"])
    etat.deck_events.defausse = deque()
    etat.deck_events.actif = None

    # on prépare explicitement un deck_global pour s'assurer qu'il n'est pas touché
    etat.deck_global.pioche = deque(["C1"])
    etat.deck_global.defausse = deque(["CDEF"])

    etat.appliquer_commandes([
        {"op": "evt.piocher"},
    ])

    # v1 refactor : evt.piocher exécute immédiatement (via evt.executer) puis clôture.
    # donc l'actif est libéré et l'event courant nettoyé.
    assert etat.deck_events.actif is None
    assert getattr(etat, "event_courant", None) is None
    # l'événement E1 doit avoir été déplacé en défausse
    assert list(etat.deck_events.defausse)[:1] == ["E1"]
    # et il doit rester E2 à piocher
    assert list(etat.deck_events.pioche) == ["E2"]

    # deck_global ne doit pas avoir été modifié
    assert list(etat.deck_global.pioche) == ["C1"]
    assert list(etat.deck_global.defausse) == ["CDEF"]


def test_evt_executer_utilise_les_commandes_de_la_carte(etat_minimal):
    etat = etat_minimal

    # on prépare un deck d'événements minimal
    etat.deck_events.pioche = deque(["EV_TEST"])
    etat.deck_events.defausse = deque()
    etat.deck_events.actif = None

    # on pose une définition de carte basée sur "commandes"
    etat.cartes_def["EV_TEST"] = {
        "commandes": [
            {"op": "axes.delta", "axe": "economique", "delta": +2},
        ]
    }

    val_avant = etat.axes["economique"].valeur

    etat.appliquer_commandes([
        {"op": "evt.piocher"},
    ])

    # evt.piocher a exécuté la carte via evt.executer interne
    assert etat.axes["economique"].valeur == val_avant + 2


def test_evt_executer_fallback_effet_delta_axes(etat_minimal):
    etat = etat_minimal

    # deck d'événements avec une carte legacy sans "commandes"
    etat.deck_events.pioche = deque(["EV_LEGACY"])
    etat.deck_events.defausse = deque()
    etat.deck_events.actif = None

    etat.cartes_def["EV_LEGACY"] = {
        "effet": {
            "delta_axes": {
                "economique": -1,
                "social": +1,
            }
        }
    }

    val_eco_avant = etat.axes["economique"].valeur
    val_soc_avant = etat.axes["social"].valeur

    etat.appliquer_commandes([
        {"op": "evt.piocher"},
    ])

    # fallback "effet.delta_axes" -> commandes axes.delta
    assert etat.axes["economique"].valeur == val_eco_avant - 1
    assert etat.axes["social"].valeur == val_soc_avant + 1


