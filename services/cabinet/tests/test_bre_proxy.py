import pytest
from types import SimpleNamespace

from services.cabinet.bre.regles_bre_proxy import ReglesBreProxy, BreIndisponible


def test_regle_sous_phase_appelle_bre(monkeypatch):
    appels = []

    def fake_post_json(self, path, payload):
        appels.append((path, payload))
        return {"commands": [{"op": "signal.programme_ouvert"}]}

    monkeypatch.setattr(ReglesBreProxy, "_post_json", fake_post_json)

    proxy = ReglesBreProxy(
        rules_url="http://rules-service:8081",
        skin="debut_mandat_bre",
        version_regles="v1",
        timeout_s=1.0,
    )

    etat = SimpleNamespace(
        joueurs={
            "J1": SimpleNamespace(
                id="J1",
                attention_dispo=2,
                capital_politique=3,
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
    commandes = proxy.regle_sous_phase(etat, "signal.init_tour")

    assert commandes == [{"op": "signal.programme_ouvert"}]
    assert appels[0][0] == "/rules/eval/sous-phase"
    assert appels[0][1]["analyse_skin"] == {
        "skin": "debut_mandat_bre",
        "version": "v1",
    }
    assert appels[0][1]["joueurs"]["J1"]["attention_dispo"] == 2
    assert appels[0][1]["etat_min"]["cartes_def"]["MES_PLAN_SOCIAL"]["cout_cp"] == 1
    assert "version_regles" not in appels[0][1]


def test_bre_indisponible(monkeypatch):
    def fake_post_json(self, path, payload):
        raise BreIndisponible("Timeout")

    monkeypatch.setattr(ReglesBreProxy, "_post_json", fake_post_json)

    proxy = ReglesBreProxy(
        rules_url="http://rules-service:8081",
        skin="debut_mandat_bre",
        version_regles="v1",
        timeout_s=0.1,  # Timeout court pour déclencher l'erreur
    )

    with pytest.raises(BreIndisponible):
        proxy.regle_sous_phase(object(), "signal.init_tour")
