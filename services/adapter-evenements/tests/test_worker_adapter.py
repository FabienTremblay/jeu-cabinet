# rôle        : vérifie l'adaptation des événements lobby en commandes moteur
# usage       : tests pytest du worker adapter-evenements
# contexte    : propagation Kafka de la politique de timeout
# statut      : actif
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from adapter_evenements.worker_adapter import transformer_evenement_en_commande


def test_partie_lancee_copie_politique_timeout_dans_commande():
    politique = {
        "version": 1,
        "active": False,
        "delai_inactivite_secondes": 900,
    }

    enveloppe = transformer_evenement_en_commande(
        {
            "type": "PartieLancee",
            "id_table": "T000001",
            "id_partie": "P000001",
            "skin_jeu": "minimal",
            "politique_timeout_partie": politique,
            "joueurs": [
                {
                    "id_joueur": "J000001",
                    "nom": "Alice",
                    "alias": "A",
                    "courriel": "a@example.com",
                    "role": "hote",
                }
            ],
        }
    )

    commande = enveloppe["commande"]
    assert commande["op"] == "partie.creer"
    assert commande["politique_timeout_partie"] == politique


def test_partie_lancee_sans_politique_reste_compatible():
    enveloppe = transformer_evenement_en_commande(
        {
            "type": "PartieLancee",
            "id_table": "T000001",
            "id_partie": "P000001",
            "joueurs": [],
        }
    )

    assert "politique_timeout_partie" not in enveloppe["commande"]
