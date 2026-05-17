# rôle        : vérifie le contrat HTTP de configuration partie du moteur
# usage       : tests pytest avec TestClient FastAPI
# contexte    : POST /parties et Etat.configuration_partie
# statut      : actif
from __future__ import annotations

from fastapi import HTTPException

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


def test_creer_partie_refuse_une_skin_non_chargeable(monkeypatch):
    _desactiver_publication(monkeypatch)

    try:
        app_module.creer_partie(
            RequetePartie(
                partie_id="P-SKIN-NON-CHARGEABLE",
                nom="demo",
                skin_jeu="exemple_mandat_climat_overlay",
                joueurs={"J1": {"nom": "Alice"}},
            ),
            manager=PartieManager(),
            correlation_id="test",
        )
    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail["code"] == "SKIN_NON_CHARGEABLE"
    else:
        raise AssertionError("creation acceptee pour une skin non chargeable")


def test_creer_partie_refuse_une_skin_absente_du_catalogue(monkeypatch):
    _desactiver_publication(monkeypatch)

    try:
        app_module.creer_partie(
            RequetePartie(
                partie_id="P-SKIN-INCONNUE",
                nom="demo",
                skin_jeu="skin_absente",
                joueurs={"J1": {"nom": "Alice"}},
            ),
            manager=PartieManager(),
            correlation_id="test",
        )
    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail["code"] == "SKIN_INCONNUE"
    else:
        raise AssertionError("creation acceptee pour une skin absente")
