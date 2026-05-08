# rôle        : vérifie la traduction des commandes moteur en appels HTTP
# usage       : tests pytest du worker commande_moteur
# contexte    : propagation de configuration vers POST /parties
# statut      : actif
from __future__ import annotations

import pytest

from services.commande_moteur import worker_moteur


class ReponseOk:
    status_code = 200
    text = "{}"

    def json(self):
        return {"ok": True}


class ProducteurMemoire:
    def __init__(self):
        self.messages = []

    def send(self, topic, key, value):
        self.messages.append({"topic": topic, "key": key, "value": value})

    def flush(self, timeout):
        self.flush_timeout = timeout


@pytest.fixture(autouse=True)
def vider_surveillance():
    worker_moteur.PARTIES_SURVEILLEES.clear()
    yield
    worker_moteur.PARTIES_SURVEILLEES.clear()


def test_partie_creer_transmet_configuration_partie(monkeypatch):
    appels = []

    def fake_post(url, json, timeout):
        appels.append({"url": url, "json": json, "timeout": timeout})
        return ReponseOk()

    monkeypatch.setattr(worker_moteur.requests, "post", fake_post)

    politique = {
        "version": 1,
        "active": True,
        "delai_inactivite_secondes": 1200,
    }

    worker_moteur.traiter_partie_creer(
        table_id="T000001",
        meta={"source": "test"},
        commande={
            "op": "partie.creer",
            "id_partie": "P000001",
            "skin_jeu": "minimal",
            "politique_timeout_partie": politique,
            "joueurs": [
                {
                    "id_joueur": "J000001",
                    "nom": "Alice",
                    "alias": "A",
                    "role": "hote",
                    "courriel": "a@example.com",
                }
            ],
        },
    )

    body = appels[0]["json"]
    assert body["configuration_partie"] == {"politique_timeout_partie": politique}
    assert body["joueurs"]["J000001"]["role"] == "hote"


def test_partie_creer_sans_politique_n_envoie_pas_configuration(monkeypatch):
    appels = []

    def fake_post(url, json, timeout):
        appels.append(json)
        return ReponseOk()

    monkeypatch.setattr(worker_moteur.requests, "post", fake_post)

    worker_moteur.traiter_partie_creer(
        table_id="T000001",
        meta={},
        commande={"op": "partie.creer", "id_partie": "P000001", "joueurs": []},
    )

    assert "configuration_partie" not in appels[0]


def test_partie_terminer_appelle_api_moteur_avec_raison_et_idempotence(monkeypatch):
    appels = []

    def fake_post(url, json, headers, timeout):
        appels.append({"url": url, "json": json, "headers": headers, "timeout": timeout})
        return ReponseOk()

    monkeypatch.setattr(worker_moteur.requests, "post", fake_post)

    worker_moteur.traiter_partie_terminer(
        table_id="T000001",
        meta={"idempotency_key": "timeout-inactivite:P000001"},
        commande={
            "op": "partie.terminer",
            "id_partie": "P000001",
            "raison": "TIMEOUT_INACTIVITE",
        },
    )

    assert appels == [
        {
            "url": f"{worker_moteur.API_MOTEUR_URL}/parties/P000001/terminer",
            "json": {"raison": "TIMEOUT_INACTIVITE"},
            "headers": {"Idempotency-Key": "timeout-inactivite:P000001"},
            "timeout": 10,
        }
    ]


def test_traiter_message_partie_terminer_route_vers_execution(monkeypatch):
    appels = []

    def fake_traiter_partie_terminer(**kwargs):
        appels.append(kwargs)

    monkeypatch.setattr(worker_moteur, "traiter_partie_terminer", fake_traiter_partie_terminer)

    payload = {
        "table_id": "T000001",
        "commande": {
            "op": "partie.terminer",
            "id_partie": "P000001",
            "raison": "TIMEOUT_INACTIVITE",
        },
        "meta": {"idempotency_key": "timeout-inactivite:P000001"},
    }

    worker_moteur.traiter_message_commandes("P000001", payload)

    assert appels == [
        {
            "table_id": "T000001",
            "commande": payload["commande"],
            "meta": payload["meta"],
        }
    ]


def test_traiter_message_partie_creer_enregistre_surveillance(monkeypatch):
    monkeypatch.setattr(worker_moteur, "traiter_partie_creer", lambda **kwargs: None)

    worker_moteur.traiter_message_commandes(
        "T000001",
        {
            "table_id": "T000001",
            "commande": {
                "op": "partie.creer",
                "id_partie": "P000001",
                "politique_timeout_partie": {
                    "version": 1,
                    "active": True,
                    "delai_inactivite_secondes": 60,
                },
            },
            "meta": {},
        },
    )

    partie = worker_moteur.PARTIES_SURVEILLEES["P000001"]
    assert partie.table_id == "T000001"
    assert partie.delai_inactivite_secondes == 60
    assert partie.commande_timeout_produite is False


def test_partie_sans_politique_effective_est_ignoree():
    worker_moteur.enregistrer_surveillance_partie(
        table_id="T000001",
        commande={"op": "partie.creer", "id_partie": "P000001"},
        maintenant=100.0,
    )

    assert worker_moteur.PARTIES_SURVEILLEES == {}


def test_politique_inactive_est_ignoree():
    worker_moteur.enregistrer_surveillance_partie(
        table_id="T000001",
        commande={
            "op": "partie.creer",
            "id_partie": "P000001",
            "politique_timeout_partie": {
                "version": 1,
                "active": False,
                "delai_inactivite_secondes": 60,
            },
        },
        maintenant=100.0,
    )

    assert worker_moteur.PARTIES_SURVEILLEES == {}


def test_evenement_cab_events_met_a_jour_derniere_activite():
    worker_moteur.enregistrer_surveillance_partie(
        table_id="T000001",
        commande={
            "op": "partie.creer",
            "id_partie": "P000001",
            "politique_timeout_partie": {
                "version": 1,
                "active": True,
                "delai_inactivite_secondes": 60,
            },
        },
        maintenant=100.0,
    )

    worker_moteur.mettre_a_jour_activite_depuis_evenement(
        {
            "aggregate_id": "P000001",
            "op_code": "joueur.action",
            "occurred_at": "1970-01-01T00:03:20+00:00",
        }
    )

    assert worker_moteur.PARTIES_SURVEILLEES["P000001"].derniere_activite_at == 200.0


def test_evenement_partie_terminer_arrete_surveillance():
    worker_moteur.enregistrer_surveillance_partie(
        table_id="T000001",
        commande={
            "op": "partie.creer",
            "id_partie": "P000001",
            "politique_timeout_partie": {
                "version": 1,
                "active": True,
                "delai_inactivite_secondes": 60,
            },
        },
        maintenant=100.0,
    )

    worker_moteur.mettre_a_jour_activite_depuis_evenement(
        {
            "aggregate_id": "P000001",
            "op_code": "partie.terminer",
            "occurred_at": "1970-01-01T00:01:10+00:00",
        }
    )

    assert worker_moteur.PARTIES_SURVEILLEES == {}


def test_timeout_produit_commande_partie_terminer_une_seule_fois():
    producteur = ProducteurMemoire()
    worker_moteur.enregistrer_surveillance_partie(
        table_id="T000001",
        commande={
            "op": "partie.creer",
            "id_partie": "P000001",
            "politique_timeout_partie": {
                "version": 1,
                "active": True,
                "delai_inactivite_secondes": 60,
            },
        },
        maintenant=100.0,
    )

    worker_moteur.verifier_timeouts_inactivite(producteur, maintenant=160.0)
    worker_moteur.verifier_timeouts_inactivite(producteur, maintenant=220.0)

    assert len(producteur.messages) == 1
    message = producteur.messages[0]
    assert message["topic"] == worker_moteur.KAFKA_TOPIC_COMMANDS
    assert message["key"] == "P000001"
    assert message["value"]["commande"] == {
        "op": "partie.terminer",
        "id_partie": "P000001",
        "raison": "TIMEOUT_INACTIVITE",
        "idempotency_key": "timeout-inactivite:P000001",
    }
    assert message["value"]["meta"]["idempotency_key"] == "timeout-inactivite:P000001"
    assert worker_moteur.PARTIES_SURVEILLEES["P000001"].commande_timeout_produite is True


def test_timeout_non_depasse_ne_produit_pas_commande():
    producteur = ProducteurMemoire()
    worker_moteur.enregistrer_surveillance_partie(
        table_id="T000001",
        commande={
            "op": "partie.creer",
            "id_partie": "P000001",
            "politique_timeout_partie": {
                "version": 1,
                "active": True,
                "delai_inactivite_secondes": 60,
            },
        },
        maintenant=100.0,
    )

    worker_moteur.verifier_timeouts_inactivite(producteur, maintenant=159.0)

    assert producteur.messages == []
