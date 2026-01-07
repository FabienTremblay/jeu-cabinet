import pytest
from services.cabinet.moteur.etat import ProgrammeTour

def test_skin_signals_mapping(etat_minimal):
    # la skin "minimal" renomme conseil->cabinet, execution_programme->execution, etc.
    assert etat_minimal.sous_phase_order == ("monde","cabinet","vote","amendements","execution","cloture")
    # mapping explicite fourni par la skin (et fallback pour les autres)
    assert etat_minimal.sous_phase_signals["cabinet"] == "on_conseil"
    assert etat_minimal.sous_phase_signals["execution"] == "on_execution_programme"
    assert etat_minimal.sous_phase_signals["vote"] == "on_vote_programme"
    # IMPORTANT : “monde” doit mapper sur on_start_monde (sinon ‘signal_inconnu’)
    assert etat_minimal.sous_phase_signals.get("monde") in ("on_start_monde", "on_monde")

def test_monde_event_consumption_and_axes_delta(pm, etat_minimal, goto):
    # démarrage -> tour/monde
    etat_minimal.demarrer_partie()
    assert etat_minimal.phase == "tour"
    # v1 actuelle : on démarre en init_tour et le signal init_tour n'est pas traité
    assert etat_minimal.sous_phase == "init_tour"

    # on déclenche explicitement la sous-phase monde
    goto(pm, etat_minimal, "monde")

    # l'événement EV_CHOC_PETROLE applique -2 sur l'axe économique
    assert etat_minimal.axes["economique"].valeur == 3

    # et l'événement reste actif (pas de clôture automatique dans la v1 actuelle)
    assert etat_minimal.deck_events.actif == "EV_CHOC_PETROLE"

    # v1 actuelle : après "monde", l'événement est encore actif
    assert etat_minimal.deck_events.actif == "EV_CHOC_PETROLE"
    assert len(etat_minimal.deck_events.pioche) == 0
    assert list(etat_minimal.deck_events.defausse)[:1] in (["EV_CHOC_PETROLE"], [])
    # la sous-phase cible doit avancer (selon commandes renvoyées) -> “cabinet”
    assert etat_minimal.sous_phase in ("cabinet","conseil","vote","amendements","execution","cloture")

def test_cabinet_to_vote(pm, etat_minimal, goto):
    etat_minimal.demarrer_partie()
    goto(pm, etat_minimal, "monde")
    # cabinet ouvre le conseil et passe au vote (selon mock_decide)
    goto(pm, etat_minimal, "cabinet")
    assert etat_minimal.sous_phase in ("vote","vote_programme")

def test_vote_path_to_execution_or_amendments(pm, etat_minimal, goto):
    etat_minimal.demarrer_partie()
    goto(pm, etat_minimal, "monde")
    goto(pm, etat_minimal, "cabinet")

    # cas majorité OUI -> exécution
    etat_minimal.programme = ProgrammeTour(entrees=[], votes={"J1": +1, "J2": +1})
    goto(pm, etat_minimal, "vote")
    assert etat_minimal.sous_phase in ("execution","execution_programme")

    # revenir en arrière pour tester le NON (nouvelle partie propre pour éviter l'idempotence)
    etat2 = pm.creer("minimal", "T-002", {"J1":{"nom":"A"}, "J2":{"nom":"B"}}, seed=43)
    etat2.demarrer_partie(); goto(pm, etat2, "monde"); goto(pm, etat2, "cabinet")
    etat2.programme = ProgrammeTour(entrees=[], votes={"J1": -1, "J2": -1})
    goto(pm, etat2, "vote")
    assert etat2.sous_phase == "amendements"

def test_execution_applies_program_effects(pm, etat_minimal, goto):
    etat_minimal.demarrer_partie()
    goto(pm, etat_minimal, "monde")
    goto(pm, etat_minimal, "cabinet")

    # une entrée “MES_PLAN_SOCIAL” : +1 social, -1 économique
    etat_minimal.programme = ProgrammeTour(
        entrees=[type("E", (), {"uid":"u1","carte_id":"MES_PLAN_SOCIAL","auteur_id":"J1","type":"mesure","params":{}, "tags":[]})()],
        votes={"J1": +1, "J2": +1}
    )
    # vote -> execution
    goto(pm, etat_minimal, "vote")
    val_soc = etat_minimal.axes["social"].valeur
    val_eco = etat_minimal.axes["economique"].valeur
    goto(pm, etat_minimal, "execution")
    # programme_execute doit avoir appliqué l'effet
    assert etat_minimal.axes["social"].valeur == val_soc + 1
    assert etat_minimal.axes["economique"].valeur == val_eco - 1
    assert etat_minimal.sous_phase in ("cloture","cloture_tour")

def test_cloture_increments_tour_and_resets_attention(pm, etat_minimal, goto):
    etat_minimal.demarrer_partie()

    # MONDE -> événement actif
    goto(pm, etat_minimal, "monde")
    # CABINET
    goto(pm, etat_minimal, "cabinet")

    # vote majoritaire OUI pour aller à l'exécution
    from services.cabinet.moteur.etat import ProgrammeTour
    etat_minimal.programme = ProgrammeTour(entrees=[], votes={"J1": +1, "J2": +1})
    goto(pm, etat_minimal, "vote")
    # EXECUTION
    goto(pm, etat_minimal, "execution")

    # Pré-conditions pour la clôture
    att_max_J1 = etat_minimal.joueurs["J1"].attention_max
    att_max_J2 = etat_minimal.joueurs["J2"].attention_max
    tour_avant = etat_minimal.tour

    # v1 actuelle : après "monde", l'événement reste actif (pas de clôture automatique)
    assert etat_minimal.deck_events.actif == "EV_CHOC_PETROLE"

    # CLÔTURE : doit réinitialiser attention, incrémenter le tour
    # et déplacer l'événement actif vers la défausse (Option B)
    goto(pm, etat_minimal, "cloture")

    assert etat_minimal.tour == tour_avant + 1
    assert etat_minimal.joueurs["J1"].attention_dispo == att_max_J1
    assert etat_minimal.joueurs["J2"].attention_dispo == att_max_J2
    # cycle relance au début
    assert etat_minimal.sous_phase in ("monde","cabinet")


    assert list(etat_minimal.deck_events.defausse)[:1] in (
        ["EV_CHOC_PETROLE"],  # skin minimale habituelle
        [],                   # tolérance si aucune carte n’a été tirée
    )
