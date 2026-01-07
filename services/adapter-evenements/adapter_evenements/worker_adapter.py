from __future__ import annotations

import logging
from datetime import datetime, timezone
import os

from .kafka_consumer import creer_consumer
from .kafka_producer import Producer

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


TOPIC_ENTREE = os.getenv("ADAPTER_TOPIC_ENTREE", "cabinet.parties.evenements")
TOPIC_SORTIE = os.getenv("ADAPTER_TOPIC_SORTIE", "cab.commands")



def transformer_evenement_en_commande(evt: dict) -> dict:
    """
    Transforme un événement de lobby (PartieLancee) en commande pour le moteur.

    - conserve les infos riches sur les joueurs (nom, alias, courriel, role)
    - fournit au moteur une structure simple / attendue :
        commande["joueurs"] = [ {id_joueur, role, ...}, ... ]
    """

    type_evt = evt.get("type")
    if type_evt != "PartieLancee":
        # Pour l’instant on ne sait traiter que ce type-là sur ce topic
        logger.warning("Événement ignoré type=%s payload=%r", type_evt, evt)
        return {
            "table_id": evt.get("id_table"),
            "commande": {
                "op": "noop",
            },
            "meta": {
                "source": "adapter-evenements",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "evenement_type": type_evt,
            },
        }

    table_id = evt["id_table"]
    id_partie = evt["id_partie"]
    joueurs_src = evt.get("joueurs", [])
    skin_jeu = evt.get("skin_jeu")

    # On reconstruit une *liste* d’objets joueur pour le moteur.
    # Format minimal : { id_joueur, role }
    # Infos riches (nom, alias, courriel) sont gardées sans que le moteur en dépende.
    joueurs_commande: list[dict] = []
    for j in joueurs_src:
        # j vient du lobby -> JoueurPartie (id_joueur, nom, alias, courriel, role)
        jid = j.get("id_joueur")
        if not jid:
            logger.warning("Joueur sans id_joueur dans evt=%r", j)
            continue

        role = j.get("role") or "joueur"

        joueur_cmd = {
            "id_joueur": jid,
            "role": role,
            # infos supplémentaires, non obligatoires côté moteur
            "nom": j.get("nom"),
            "alias": j.get("alias"),
            "courriel": j.get("courriel"),
        }
        joueurs_commande.append(joueur_cmd)

    commande = {
        "op": "partie.creer",
        "id_partie": id_partie,
        "joueurs": joueurs_commande,
        "skin_jeu": skin_jeu,
    }

    enveloppe = {
        "table_id": table_id,
        "commande": commande,
        "meta": {
            "source": "adapter-evenements",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evenement_type": type_evt,
            "correlation_id": evt.get("correlation_id"),
        },
    }

    logger.debug("Commande construite pour moteur: %r", enveloppe)
    return enveloppe


def main():
    logger.info(f"Adapter → démarrage (écoute {TOPIC_ENTREE}, publie {TOPIC_SORTIE})")

    cons = None
    while cons is None:
        try:
            cons = creer_consumer(TOPIC_ENTREE)
        except NoBrokersAvailable:
            logger.warning("Kafka pas encore disponible, nouvel essai dans 3s…")
            time.sleep(3)

    prod = Producer()

    for msg in cons:
        logger.info("Adapter ← event reçu topic=%s key=%s", msg.topic, msg.key)
        evt = msg.value
        commande = transformer_evenement_en_commande(evt)
        prod.publier(TOPIC_SORTIE, key=evt["id_table"], message=commande)


if __name__ == "__main__":
    main()

