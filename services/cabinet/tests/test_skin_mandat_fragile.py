from types import SimpleNamespace

from services.cabinet.bre.regles_bre_proxy import ReglesBreProxy
from services.cabinet.moteur.config_loader import charger_config_et_regles


def test_skin_mandat_fragile_est_chargeable():
    cfg, regles = charger_config_et_regles("mandat_fragile")

    assert cfg["id"] == "mandat_fragile"
    assert cfg["moteur_regles"]["type"] == "bre"
    assert isinstance(regles, ReglesBreProxy)


def test_mandat_fragile_refuse_action_acceptee_par_debut_mandat_bre():
    _, regles_debut = charger_config_et_regles("debut_mandat_bre")
    _, regles_fragile = charger_config_et_regles("mandat_fragile")
    etat = etat_validation(attention=1, capital=1)

    ok_debut, cout_debut = regles_debut.valider_usage_carte(etat, cmd())
    ok_fragile, cout_fragile = regles_fragile.valider_usage_carte(etat, cmd())

    assert ok_debut is True
    assert cout_debut == [
        {"op": "joueur.attention.delta", "joueur_id": "J1", "delta": -1},
        {"op": "joueur.capital.delta", "joueur_id": "J1", "delta": -1},
    ]
    assert ok_fragile is False
    assert cout_fragile == []


def test_mandat_fragile_produit_un_cout_different_par_yaml():
    _, regles_fragile = charger_config_et_regles("mandat_fragile")

    ok, cout = regles_fragile.valider_usage_carte(
        etat_validation(attention=2, capital=1),
        cmd(),
    )

    assert ok is True
    assert cout == [
        {"op": "joueur.attention.delta", "joueur_id": "J1", "delta": -2},
        {"op": "joueur.capital.delta", "joueur_id": "J1", "delta": -1},
    ]


def test_mandat_fragile_n_exige_pas_de_changement_ui_ni_java():
    _, regles = charger_config_et_regles("mandat_fragile")

    assert isinstance(regles, ReglesBreProxy)
    assert regles.regles_cartes is not None
    assert regles.regles_cartes.regles[0]["id"] == "engager_carte_cout_mandat_fragile"


def etat_validation(attention: int, capital: int):
    return SimpleNamespace(
        phase="tour",
        sous_phase="conseil",
        tour=1,
        joueurs={
            "J1": SimpleNamespace(
                id="J1",
                attention_dispo=attention,
                capital_politique=capital,
                main=["MES_PLAN_SOCIAL"],
            )
        },
        cartes_def={
            "MES_PLAN_SOCIAL": {
                "id": "MES_PLAN_SOCIAL",
                "type": "mesure",
                "cout_attention": 1,
                "cout_cp": 1,
            }
        },
    )


def cmd():
    return {
        "op": "programme.engager_carte",
        "joueur_id": "J1",
        "carte_id": "MES_PLAN_SOCIAL",
    }
