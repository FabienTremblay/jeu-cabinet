from types import SimpleNamespace

from services.cabinet.bre.etat_bre_adapter import EtatBreAdapter
from services.cabinet.bre.regles_bre_proxy import ReglesBreProxy
from services.cabinet.moteur.config_loader import charger_config_et_regles


def test_skin_debut_mandat_bre_est_chargeable():
    cfg, regles = charger_config_et_regles("debut_mandat_bre")

    assert cfg["id"] == "debut_mandat_bre"
    assert cfg["moteur_regles"]["type"] == "bre"
    assert cfg["moteur_regles"]["version_regles"] == "v1"
    assert isinstance(regles, ReglesBreProxy)


def test_etat_bre_adapter_utilise_les_champs_reels_du_joueur():
    etat = SimpleNamespace(
        phase="active",
        sous_phase="conseil",
        tour=1,
        id_joueur_courant="J1",
        joueurs={
            "J1": SimpleNamespace(
                id="J1",
                role="ministre",
                attention_dispo=2,
                capital_politique=3,
            )
        },
        attente=None,
    )

    facts = EtatBreAdapter.to_facts(etat)

    joueur = facts["etat"]["joueurs"][0]
    assert joueur["id"] == "J1"
    assert joueur["attention_dispo"] == 2
    assert joueur["capital_politique"] == 3
