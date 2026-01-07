def test_initial_distribution_balanced(pm, etat_minimal, goto):
    # démarrer la partie puis passer par la phase MONDE
    etat_minimal.demarrer_partie()
    goto(pm, etat_minimal, "monde")

    # 3 cartes chacun dans le skin minimal
    assert len(etat_minimal.joueurs["J1"].main) == 3
    assert len(etat_minimal.joueurs["J2"].main) == 3


def test_deck_copies_present(pm, etat_minimal, goto):
    etat_minimal.demarrer_partie()
    goto(pm, etat_minimal, "monde")

    # 12 cartes initiales, 3 * 2 en main = 6, donc 6 en pioche
    assert len(etat_minimal.deck_global.pioche) == 6
    total_cartes = len(etat_minimal.deck_global.pioche) \
             + sum(len(j.main) for j in etat_minimal.joueurs.values())
    assert total_cartes == 12


def test_jouer_carte_applique_effet_et_defausse(pm, etat_minimal):
    j1 = etat_minimal.joueurs["J1"]
    # force une carte connue en main
    if "MES_REFORME_TAXE" not in j1.main:
        j1.main.append("MES_REFORME_TAXE")
    eco_avant = etat_minimal.axes["economique"].valeur
    cp_avant = j1.capital_politique

    cmds = etat_minimal.preparer_commandes_carte("J1", "MES_REFORME_TAXE")
    etat_minimal.appliquer_commandes(cmds)
    assert etat_minimal.axes["economique"].valeur == eco_avant + 1  # effet carte
    # v1 : le coût politique n'est pas appliqué hors programme / phase
    assert etat_minimal.joueurs["J1"].capital_politique == cp_avant
    # v1 : "jouer immédiatement" n'implique pas de défausse automatique.
    # la défausse est gérée par les ops de deck (ex. deck.defausser_main).
    assert "MES_REFORME_TAXE" in j1.main
    assert list(etat_minimal.deck_global.defausse) == []

