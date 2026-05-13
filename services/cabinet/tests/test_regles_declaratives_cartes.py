from pathlib import Path
from types import SimpleNamespace

from services.cabinet.bre.regles_bre_proxy import ReglesBreProxy
from services.cabinet.bre.regles_declaratives_cartes import ReglesDeclarativesCartes


CHEMIN_REGLES = (
    Path(__file__).parents[1]
    / "skins"
    / "debut_mandat_bre"
    / "regles"
    / "validation_cartes.yaml"
)


def test_regle_yaml_est_lue():
    regles = ReglesDeclarativesCartes.depuis_fichier(CHEMIN_REGLES)

    assert regles.donnees["version"] == 1
    assert regles.regles[0]["op"] == "programme.engager_carte"


def test_carte_valide_est_acceptee():
    resultat = ReglesDeclarativesCartes.depuis_fichier(CHEMIN_REGLES).valider(
        etat_min=etat_min(attention=2, capital=3, cout_attention=1, cout_cp=1),
        cmd=cmd(),
    )

    assert resultat is not None
    assert resultat.ok is True
    assert resultat.cmd_cout == [
        {"op": "joueur.attention.delta", "joueur_id": "J1", "delta": -1},
        {"op": "joueur.capital.delta", "joueur_id": "J1", "delta": -1},
    ]


def test_attention_insuffisante_refuse_action():
    resultat = ReglesDeclarativesCartes.depuis_fichier(CHEMIN_REGLES).valider(
        etat_min=etat_min(attention=0, capital=3, cout_attention=1, cout_cp=1),
        cmd=cmd(),
    )

    assert resultat is not None
    assert resultat.ok is False
    assert resultat.raisons == ["attention_insuffisante"]


def test_capital_politique_insuffisant_refuse_action():
    resultat = ReglesDeclarativesCartes.depuis_fichier(CHEMIN_REGLES).valider(
        etat_min=etat_min(attention=2, capital=0, cout_attention=1, cout_cp=1),
        cmd=cmd(),
    )

    assert resultat is not None
    assert resultat.ok is False
    assert resultat.raisons == ["capital_politique_insuffisant"]


def test_modification_declarative_du_cout_change_le_resultat(tmp_path):
    chemin = tmp_path / "validation_cartes.yaml"
    chemin.write_text(
        """
version: 1
validation_cartes:
  - id: engager_carte_cout_attention_renforce
    op: programme.engager_carte
    conditions:
      - champ: joueur.attention_dispo
        operateur: ">="
        valeur: 3
      - champ: joueur.capital_politique
        operateur: ">="
        valeur: carte.cout_cp
    cout:
      - op: joueur.attention.delta
        delta: -3
      - op: joueur.capital.delta
        delta: -carte.cout_cp
""",
        encoding="utf-8",
    )

    regles = ReglesDeclarativesCartes.depuis_fichier(chemin)

    resultat = regles.valider(
        etat_min=etat_min(attention=2, capital=3, cout_attention=1, cout_cp=1),
        cmd=cmd(),
    )

    assert resultat is not None
    assert resultat.ok is False
    assert resultat.raisons == ["attention_insuffisante"]

    resultat_ok = regles.valider(
        etat_min=etat_min(attention=3, capital=3, cout_attention=1, cout_cp=1),
        cmd=cmd(),
    )

    assert resultat_ok is not None
    assert resultat_ok.ok is True
    assert resultat_ok.cmd_cout[0] == {
        "op": "joueur.attention.delta",
        "joueur_id": "J1",
        "delta": -3,
    }


def test_proxy_utilise_les_regles_yaml_sans_appeler_http(monkeypatch):
    appels_http = []

    def fake_post_json(self, path, payload):
        appels_http.append((path, payload))
        return {"ok": True, "cmd_cout": []}

    monkeypatch.setattr(ReglesBreProxy, "_post_json", fake_post_json)
    proxy = ReglesBreProxy(
        rules_url="http://rules-service:8081",
        skin="debut_mandat_bre",
        version_regles="v1",
        validation_cartes_path=str(CHEMIN_REGLES),
    )

    ok, cout = proxy.valider_usage_carte(
        SimpleNamespace(
            phase="tour",
            sous_phase="conseil",
            tour=1,
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
        ),
        cmd(),
    )

    assert ok is True
    assert cout[0]["op"] == "joueur.attention.delta"
    assert appels_http == []


def etat_min(attention: int, capital: int, cout_attention: int, cout_cp: int):
    return {
        "phase": "tour",
        "sous_phase": "conseil",
        "tour": 1,
        "joueurs": {
            "J1": {
                "id": "J1",
                "attention_dispo": attention,
                "capital_politique": capital,
                "main": ["MES_PLAN_SOCIAL"],
            }
        },
        "cartes_def": {
            "MES_PLAN_SOCIAL": {
                "id": "MES_PLAN_SOCIAL",
                "type": "mesure",
                "cout_attention": cout_attention,
                "cout_cp": cout_cp,
            }
        },
    }


def cmd():
    return {
        "op": "programme.engager_carte",
        "joueur_id": "J1",
        "carte_id": "MES_PLAN_SOCIAL",
    }
