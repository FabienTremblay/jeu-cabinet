# services/cabinet/skins/minimal/config.py

SKIN_CONFIG = {
    "axes": [
        {"id": "politique",  "valeur_init": 4, "seuil_crise": -8, "poids": 1.0},
        {"id": "economique", "valeur_init": 5, "seuil_crise": -9, "poids": 1.3},
        {"id": "social",     "valeur_init": 5, "seuil_crise": -8, "poids": 1.1},
    ],

    # nouvelle structure "economie" compatible avec Economie(**cfg["economie"])
    "economie": {
        #
        # 1) Recettes : chaque poste a une valeur et des poids d’impact sur les axes
        #
        "recettes": {
            # impôt des particuliers
            "impot_part": {
                "valeur": 1_000 * 0.18,  # ancien base_part * taux_impot_part
                "poids_axes": {
                    "economique": +1,
                    "social": -1,
                },
                # méta pour les règles / hooks de skin
                "taux": 0.18,
                "base": 1_000,
            },
            # impôt des entreprises
            "impot_ent": {
                "valeur": 1_200 * 0.22,  # ancien base_ent * taux_impot_ent
                "poids_axes": {
                    "economique": +1,
                    "politique": +1,
                },
                "taux": 0.22,
                "base": 1_200,
            },
            # redevances sur ressources
            "redevances": {
                "valeur": 400 * 0.06,  # ancien base_ressources * taux_redevances
                "poids_axes": {
                    "economique": +1,
                },
                "taux": 0.06,
                "base": 400,
            },
        },

        #
        # 2) Dépenses : mêmes principes
        #
        "depenses": {
            "sante": {
                "valeur": 600,
                "poids_axes": {
                    "social": +1,
                    "politique": +0,  # neutre dans le minimal
                },
            },
            "education": {
                "valeur": 500,
                "poids_axes": {
                    "social": +1,
                    "economique": +1,
                },
            },
            "defense": {
                "valeur": 300,
                "poids_axes": {
                    "politique": +1,
                    "economique": -1,
                },
            },
        },

        #
        # 3) Efficience : efficacité par thème/poste
        #
        "efficience": {
            # on reste simple : un seul niveau global santé/éducation/défense
            "sante": {
                "valeur": 0.90,
            },
            "education": {
                "valeur": 0.90,
            },
            "defense": {
                "valeur": 0.90,
            },
        },

        #
        # 4) Dette & taux d’intérêt
        #
        "dette": 10_000,
        "taux_interet": 0.03,

        #
        # 5) Champs conservés pour compat / hooks éventuels
        #    (ton Economie les acceptera comme attributs libres)
        #
        "taux_impot_part": 0.18,
        "taux_impot_ent": 0.22,
        "taux_redevances": 0.06,
        "base_part": 1_000,
        "base_ent": 1_200,
        "base_ressources": 400,
        "depenses_postes": {"sante": 600, "education": 500, "defense": 300},
        "capacite_max": 2,
        "efficience_globale": 0.9,
    },

    "capital_init": 2,
    "capital_collectif_init": 0,

    "cartes": [
        {
            "id": "MES_REFORME_TAXE",
            "nom": "Réforme de la taxe",
            "cout_cp": 1,
            "commandes": [
                {"op": "axes.delta", "axe": "economique", "delta": +1},
            ],
            "copies": 4,
        },
        {
            "id": "MES_PLAN_SOCIAL",
            "nom": "Plan social",
            "cout_cp": 1,
            "commandes": [
                {"op": "axes.delta", "axe": "social", "delta": +1},
                {"op": "axes.delta", "axe": "economique", "delta": -1},
            ],
            "copies": 4,
        },
        {
            "id": "MES_DISCIPLINE",
            "nom": "Discipline budgétaire",
            "cout_cp": 0,
            "commandes": [
                {"op": "axes.delta", "axe": "economique", "delta": +1},
                {"op": "axes.delta", "axe": "social", "delta": -1},
            ],
            "copies": 4,
        },
    ],

    "events": [
        {
            "id": "EV_CHOC_PETROLE",
            "nom": "Choc pétrolier",
            "commandes": [
                {"op": "axes.delta", "axe": "economique", "delta": -2},
            ],
        },
    ],

    "main_init": 3,
    "phases_tour": ["monde", "cabinet", "vote", "amendements", "execution", "cloture"],
    "phases_signals": {
        "monde": "on_start_monde",
        "cabinet": "on_conseil",
        "vote": "on_vote_programme",
        "amendements": "on_amendements",
        "execution": "on_execution_programme",
        "cloture": "on_cloture_tour",
    },
}


