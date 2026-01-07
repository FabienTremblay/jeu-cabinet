def test_two_parallel_games_isolation(pm):
    e1 = pm.creer("minimal", "G-100", {"J1":{"nom":"A"},"J2":{"nom":"B"}}, seed=1)
    e2 = pm.creer("minimal", "G-200", {"X": {"nom": "C"}, "Y": {"nom": "D"}}, seed=2)

    # démarre et exécute une sous-phase dans chaque partie
    e1.demarrer_partie(); e2.demarrer_partie()
    e1._run_subphase("monde")
    e2._run_subphase("monde")

    # états isolés (ids, pioche event décalée indépendamment)
    assert e1.id != e2.id
    assert e1.historiques != e2.historiques or e1.axes != e2.axes

def test_custom_labels_skin_flow(pm):
    # la skin "minimal" emploie "cabinet" / "execution" / "vote"
    e = pm.creer("minimal", "G-300", {"J1":{"nom":"A"},"J2":{"nom":"B"}}, seed=3)

    # demarrer_partie exécute déjà la sous-phase "monde" et passe au conseil
    e.demarrer_partie()
    assert e.phase == "tour"
    # selon le vocabulaire de la skin, la 2e sous-phase s'appelle "cabinet" ou "conseil"
    assert e.sous_phase in ("init_tour", "cabinet", "conseil")

    # on enchaîne ensuite sur la sous-phase "cabinet"
    e._run_subphase("cabinet")

    # prépare un vote majoritaire
    from services.cabinet.moteur.etat import ProgrammeTour
    e.programme = ProgrammeTour(entrees=[], votes={"J1": +1, "J2": +1})

    # puis la sous-phase "vote"
    e._run_subphase("vote")

    # et enfin l'exécution du programme
    assert e.sous_phase in ("execution", "execution_programme")

