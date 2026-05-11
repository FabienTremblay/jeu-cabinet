# rôle        : vérifie le contrat HTTP de configuration partie du moteur
# usage       : tests pytest avec TestClient FastAPI
# contexte    : POST /parties et Etat.configuration_partie
# statut      : actif
from __future__ import annotations

import services.api_moteur.app as app_module
from services.api_moteur.schemas import RequetePartie
from services.cabinet.moteur.manager import PartieManager


def _desactiver_publication(monkeypatch):
    monkeypatch.setattr(app_module, "publier_evenement", lambda *args, **kwargs: None)
    monkeypatch.setattr(app_module, "publier_evenements_domaine", lambda *args, **kwargs: None)


def test_creer_partie_conserve_configuration_partie(monkeypatch):
    _desactiver_publication(monkeypatch)
    politique = {
        "version": 1,
        "active": True,
        "delai_inactivite_secondes": 1800,
    }

    reponse = app_module.creer_partie(
        RequetePartie(
            partie_id="P-CONFIG-HTTP",
            nom="demo",
            skin_jeu="minimal",
            joueurs={"J1": {"nom": "Alice"}},
            configuration_partie={"politique_timeout_partie": politique},
        ),
        manager=PartieManager(),
        correlation_id="test",
    )

    assert reponse["etat"]["configuration_partie"] == {
        "politique_timeout_partie": politique,
    }


def test_creer_partie_sans_configuration_reste_compatible(monkeypatch):
    _desactiver_publication(monkeypatch)
    reponse = app_module.creer_partie(
        RequetePartie(
            partie_id="P-SANS-CONFIG-HTTP",
            nom="demo",
            skin_jeu="minimal",
            joueurs={"J1": {"nom": "Alice"}},
        ),
        manager=PartieManager(),
        correlation_id="test",
    )

    assert reponse["etat"]["configuration_partie"] == {}
