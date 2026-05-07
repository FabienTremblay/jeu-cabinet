# rôle        : vérifie la traduction des commandes moteur en appels HTTP
# usage       : tests pytest du worker commande_moteur
# contexte    : propagation de configuration vers POST /parties
# statut      : actif
from __future__ import annotations

from services.commande_moteur import worker_moteur


class ReponseOk:
    status_code = 200
    text = "{}"

    def json(self):
        return {"ok": True}


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
