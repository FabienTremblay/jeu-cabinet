import pytest


def test_axes_delta_clamp(etat_minimal):
    etat = etat_minimal
    etat.axes["social"].valeur = 9

    etat.appliquer_commandes([
        {"op": "axes.delta", "axe": "social", "delta": 5},
    ])

    # On passe par Axe.delta() + clamp 0..10
    assert etat.axes["social"].valeur == 10


def test_axes_set_clamp(etat_minimal):
    etat = etat_minimal

    etat.appliquer_commandes([
        {"op": "axes.set", "axe": "social", "valeur": 15},
    ])

    # clamp appliqué via Axe.clamp()
    assert etat.axes["social"].valeur == 10


def test_axes_poids_set_float(etat_minimal):
    etat = etat_minimal

    etat.appliquer_commandes([
        {"op": "axes.poids.set", "axe": "social", "poids": 2.5},
    ])

    assert etat.axes["social"].poids == pytest.approx(2.5)


def test_eco_delta_recettes_postes(etat_minimal):
    etat = etat_minimal

    # Contrat v1 refactorisé :
    # eco.delta_recettes agit sur etat.eco.recettes[nom_poste].valeur via la clé "postes".
    # Si le poste n'existe pas, il est créé à 0 par le noyau.
    poste = etat.eco.recettes.get("impot_part")
    if poste is None:
        etat.eco.recettes["impot_part"] = PosteBudgetaire(nom="impot_part", valeur=0.0)
        poste = etat.eco.recettes["impot_part"]
    depart = poste.valeur

    etat.appliquer_commandes([
        {"op": "eco.delta_recettes", "postes": {"impot_part": 100}},
    ])

    assert etat.eco.recettes["impot_part"].valeur == depart + 100


def test_eco_delta_depenses_cumule_postes(etat_minimal):
    etat = etat_minimal

    # Contrat v1 refactorisé :
    # eco.delta_depenses agit sur etat.eco.depenses[nom_poste].valeur via la clé "postes".
    poste = etat.eco.depenses.get("sante")
    if poste is None:
        etat.eco.depenses["sante"] = PosteBudgetaire(nom="sante", valeur=0.0)
        poste = etat.eco.depenses["sante"]
    depart = poste.valeur

    etat.appliquer_commandes([
        {"op": "eco.delta_depenses", "postes": {"sante": 5}},
        {"op": "eco.delta_depenses", "postes": {"sante": 7}},
    ])

    assert etat.eco.depenses["sante"].valeur == depart + 12


def test_eco_delta_dette(etat_minimal):
    etat = etat_minimal
    dette_depart = etat.eco.dette

    etat.appliquer_commandes([
        {"op": "eco.delta_dette", "montant": 50},
    ])

    assert etat.eco.dette == dette_depart + 50


def test_eco_set_taux_selection(etat_minimal):
    etat = etat_minimal

    etat.appliquer_commandes([
        {
            "op": "eco.set_taux",
            "taux": {
                "taux_impot_part": 0.42,
                "taux_interet": 0.03,
            },
        },
    ])

    assert etat.eco.taux_impot_part == pytest.approx(0.42)
    assert etat.eco.taux_interet == pytest.approx(0.03)

def test_eco_delta_recettes_cumule_multiple_postes(etat_minimal):
    etat = etat_minimal
    poste = etat.eco.recettes.get("impot_part")
    if poste is None:
        etat.eco.recettes["impot_part"] = PosteBudgetaire(nom="impot_part", valeur=0.0)
        poste = etat.eco.recettes["impot_part"]
    depart = poste.valeur

    etat.appliquer_commandes([
        {"op": "eco.delta_recettes", "postes": {"impot_part": 10}},
        {"op": "eco.delta_recettes", "postes": {"impot_part": -3}},
    ])

    assert etat.eco.recettes["impot_part"].valeur == depart + 7

