# rôle        : vérifie l'API HTTP de terminaison de partie du moteur
# usage       : tests pytest directs de l'endpoint FastAPI
# contexte    : POST /parties/{partie_id}/terminer et événement domaine D600
# statut      : actif
from __future__ import annotations

import services.api_moteur.app as app_module
from services.api_moteur.schemas import RequeteTerminerPartie
from services.cabinet.moteur.manager import PartieManager


def test_terminer_partie_publie_evenement_domaine_timeout(monkeypatch):
    evenements_publies = []

    monkeypatch.setattr(app_module, "publier_evenements_domaine", lambda evenements, **kwargs: evenements_publies.extend(evenements))

    manager = PartieManager()
    manager.creer("minimal", "P-TIMEOUT-HTTP", {"J1": {"nom": "Alice"}})

    reponse = app_module.terminer_partie(
        "P-TIMEOUT-HTTP",
        RequeteTerminerPartie(raison="TIMEOUT_INACTIVITE"),
        manager=manager,
        correlation_id="test",
        idempotency_key="timeout-inactivite:P-TIMEOUT-HTTP",
    )

    assert reponse["etat"]["termine"] is True
    assert reponse["etat"]["raison_fin"] == "TIMEOUT_INACTIVITE"
    evt = next(e for e in evenements_publies if e.op_code == "partie.terminer")
    assert evt.event_type == "cab.D600.partie.terminer"
    assert evt.data["raison"] == "TIMEOUT_INACTIVITE"


def test_terminer_partie_deja_terminee_ne_republie_pas(monkeypatch):
    lots_publies = []

    monkeypatch.setattr(app_module, "publier_evenements_domaine", lambda evenements, **kwargs: lots_publies.append(list(evenements)))

    manager = PartieManager()
    manager.creer("minimal", "P-IDEMPOTENT-HTTP", {"J1": {"nom": "Alice"}})

    app_module.terminer_partie(
        "P-IDEMPOTENT-HTTP",
        RequeteTerminerPartie(raison="TIMEOUT_INACTIVITE"),
        manager=manager,
        correlation_id="test",
        idempotency_key="timeout-inactivite:P-IDEMPOTENT-HTTP",
    )
    app_module.terminer_partie(
        "P-IDEMPOTENT-HTTP",
        RequeteTerminerPartie(raison="TIMEOUT_INACTIVITE"),
        manager=manager,
        correlation_id="test",
        idempotency_key="timeout-inactivite:P-IDEMPOTENT-HTTP",
    )

    assert any(e.op_code == "partie.terminer" for e in lots_publies[0])
    assert lots_publies[1] == []
