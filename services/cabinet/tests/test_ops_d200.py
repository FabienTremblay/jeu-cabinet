import pytest

def test_joueur_defausser_choix_retire_de_la_main_et_met_en_defausse(etat_minimal):
    etat = etat_minimal
    jid = next(iter(etat.joueurs.keys()))
    joueur = etat.joueurs[jid]

    # on prépare une main simple
    joueur.main = ["C1", "C2", "C3"]
    etat.deck_global.defausse.clear()

    etat.appliquer_commandes([
        {
            "op": "joueur.defausser_choix",
            "joueur_id": jid,
            "cartes": ["C2", "C3"],
        }
    ])

    assert joueur.main == ["C1"]
    # les cartes défaussées doivent se trouver dans la défausse globale
    assert "C2" in list(etat.deck_global.defausse)
    assert "C3" in list(etat.deck_global.defausse)

def test_joueur_defausser_hasard_reduit_la_main_et_alimente_defausse(etat_minimal):
    etat = etat_minimal
    jid = next(iter(etat.joueurs.keys()))
    joueur = etat.joueurs[jid]

    joueur.main = ["A", "B", "C", "D"]
    etat.deck_global.defausse.clear()

    etat.appliquer_commandes([
        {"op": "joueur.defausser_hasard", "joueur_id": jid, "nb": 2},
    ])

    # 2 cartes en moins dans la main
    assert len(joueur.main) == 2
    # 2 cartes en plus dans la défausse
    assert len(etat.deck_global.defausse) == 2

def test_joueur_reset_attention(etat_minimal):
    etat = etat_minimal
    jid = next(iter(etat.joueurs.keys()))
    joueur = etat.joueurs[jid]

    # on simule une attention consommée
    joueur.attention_dispo = 0
    attention_max = joueur.attention_max

    etat.appliquer_commandes([
        {"op": "joueur.reset_attention", "joueur_id": jid},
    ])

    assert joueur.attention_dispo == attention_max

def test_joueur_cartes_max_fin_tour_set_cree_attribut(etat_minimal):
    etat = etat_minimal
    jid = next(iter(etat.joueurs.keys()))
    joueur = etat.joueurs[jid]

    assert not hasattr(joueur, "cartes_max_fin_tour")

    etat.appliquer_commandes([
        {"op": "joueur.cartes_max_fin_tour.set", "joueur_id": jid, "valeur": 5},
    ])

    assert getattr(joueur, "cartes_max_fin_tour") == 5

