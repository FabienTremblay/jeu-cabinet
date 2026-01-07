# services/commande_moteur/worker_moteur.py
from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional

import requests
from kafka import KafkaConsumer

# ---------------------------------------------------------------------
# config / logging
# ---------------------------------------------------------------------

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

# commandes -> moteur
KAFKA_TOPIC_COMMANDS = os.getenv("KAFKA_TOPIC_COMMANDS", "cab.commands")
KAFKA_GROUP_ID_COMMANDS = os.getenv("KAFKA_GROUP_ID_COMMANDS", "cabinet-moteur-commands")

API_MOTEUR_URL = os.getenv("API_MOTEUR_URL", "http://api-moteur:8080")

# événements -> lobby (fin de partie)
KAFKA_TOPIC_EVENTS = os.getenv("KAFKA_TOPIC_EVENTS", "cabinet.parties.evenements")
KAFKA_GROUP_ID_EVENTS = os.getenv("KAFKA_GROUP_ID_EVENTS", "cabinet-lobby-d600")

API_LOBBY_URL = os.getenv("API_LOBBY_URL", "http://lobby:8080")


# ---------------------------------------------------------------------
# Kafka Consumers
# ---------------------------------------------------------------------

def creer_consommateur(topic: str, group_id: str) -> KafkaConsumer:
    """Crée un consumer Kafka simple."""
    logger.info(
        "Initialisation consumer Kafka topic=%s group=%s bootstrap=%s",
        topic, group_id, KAFKA_BOOTSTRAP
    )

    return KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=group_id,
        enable_auto_commit=True,
        auto_offset_reset="earliest",
        key_deserializer=lambda m: m.decode("utf-8") if m else None,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )


# ---------------------------------------------------------------------
# Commandes → API moteur
# ---------------------------------------------------------------------

def traiter_message_commandes(cle: Optional[str], payload: dict[str, Any]) -> None:
    commande = payload.get("commande") or {}
    op = commande.get("op")
    table_id = payload.get("table_id")
    meta = payload.get("meta") or {}

    logger.info(
        "Commande Kafka reçue op=%s table_id=%s key=%s meta=%s",
        op, table_id, cle, meta,
    )

    if op == "partie.creer":
        traiter_partie_creer(table_id=table_id, commande=commande, meta=meta)
    else:
        logger.warning("Commande non gérée (op=%s) -> ignorée", op)


def traiter_partie_creer(
    *,
    table_id: Optional[str],
    commande: dict[str, Any],
    meta: dict[str, Any],
) -> None:

    id_partie = commande.get("id_partie")
    joueurs_liste = commande.get("joueurs") or []
    skin_jeu = commande.get("skin_jeu")
    nom = commande.get("nom") or f"Partie {id_partie or table_id}"

    url = f"{API_MOTEUR_URL}/parties"

    options = {
        "id_table": table_id,
        "meta": meta,
        "origine": "kafka",
    }

    # transformer en dict {id_joueur: info}
    joueurs_dict = {}
    for j in joueurs_liste:
        jid = j.get("id_joueur")
        if not jid:
            continue
        joueurs_dict[jid] = {
            "nom": j.get("nom") or "",
            "alias": j.get("alias") or j.get("nom") or "",
            "role": j.get("role") or "joueur",
            "courriel": j.get("courriel") or "",
        }

    body = {
        "partie_id": id_partie,
        "nom": nom,
        "joueurs": joueurs_dict,
        "options": options,
    }
    if skin_jeu is not None:
        body["skin_jeu"] = skin_jeu

    logger.info("POST moteur %s body=%r", url, body)

    try:
        r = requests.post(url, json=body, timeout=10)
    except Exception:
        logger.exception("Erreur réseau lors de l'appel à API moteur")
        return

    if r.status_code // 100 != 2:
        logger.error(
            "Échec création partie (HTTP %s): %s",
            r.status_code, r.text
        )
    else:
        try:
            donnees = r.json()
        except Exception:
            donnees = r.text
        logger.info("Partie créée avec succès: %r", donnees)


# ---------------------------------------------------------------------
# Événements → API Lobby (libération joueurs et fin de partie)
# ---------------------------------------------------------------------

def traiter_message_events(cle: Optional[str], payload: dict[str, Any]) -> None:
    """
    Écoute des événements du moteur pour synchroniser la fin de partie dans le Lobby.

    On ne suppose PAS que le moteur connaisse la table.
    On se base sur:
      - aggregate_id = id de la partie
      - data.joueur_id = joueur qui quitte définitivement
    """

    op_code = payload.get("op_code")
    if op_code != "partie.joueur_quitte_definitivement":
        # on ne traite que ce cas précis pour l’instant
        return

    partie_id = payload.get("aggregate_id")
    data = payload.get("data") or {}
    joueur_id = data.get("joueur_id")

    if not partie_id or not joueur_id:
        logger.warning(
            "Événement D600 incomplet (partie_id=%r, joueur_id=%r) -> ignoré",
            partie_id,
            joueur_id,
        )
        return

    logger.info(
        "D600 reçu: partie.joueur_quitte_definitivement partie_id=%s joueur_id=%s",
        partie_id,
        joueur_id,
    )
    appeler_lobby_quitte(partie_id=partie_id, joueur_id=joueur_id)


def appeler_lobby_quitte(partie_id: str, joueur_id: str) -> None:
    """
    Appelle le lobby pour libérer un joueur d'une partie.
    Le lobby se charge lui-même de retrouver la table associée à la partie.
    """
    url = f"{API_LOBBY_URL}/api/parties/{partie_id}/joueurs/quitter"
    body = {"id_joueur": joueur_id}

    logger.info(
        "POST Lobby libération joueur: url=%s body=%r",
        url,
        body,
    )

    try:
        r = requests.post(url, json=body, timeout=10)
    except Exception:
        logger.exception("Erreur réseau lors de l'appel à l'API Lobby")
        return

    if r.status_code // 100 != 2:
        logger.error(
            "Erreur côté Lobby (HTTP %s) pour partie=%s joueur=%s : %s",
            r.status_code,
            partie_id,
            joueur_id,
            r.text,
        )
    else:
        logger.info(
            "Synchronisation Lobby OK: partie=%s joueur=%s libéré",
            partie_id,
            joueur_id,
        )


# ---------------------------------------------------------------------
# boucle principale combinée
# ---------------------------------------------------------------------

def main() -> None:
    cons_cmd = creer_consommateur(KAFKA_TOPIC_COMMANDS, KAFKA_GROUP_ID_COMMANDS)
    cons_evt = creer_consommateur(KAFKA_TOPIC_EVENTS, KAFKA_GROUP_ID_EVENTS)

    logger.info("Worker moteur/lobby prêt :")
    logger.info(" - écoute commandes sur %s", KAFKA_TOPIC_COMMANDS)
    logger.info(" - écoute événements sur %s", KAFKA_TOPIC_EVENTS)

    try:
        while True:
            # commandes
            records_cmd = cons_cmd.poll(timeout_ms=1000)
            for _, msgs in records_cmd.items():
                for rec in msgs:
                    try:
                        traiter_message_commandes(rec.key, rec.value)
                    except Exception:
                        logger.exception("Erreur traitement commande")

            # événements D600
            records_evt = cons_evt.poll(timeout_ms=1000)
            for _, msgs in records_evt.items():
                for rec in msgs:
                    try:
                        traiter_message_events(rec.key, rec.value)
                    except Exception:
                        logger.exception("Erreur traitement événement")
    finally:
        cons_cmd.close()
        cons_evt.close()

if __name__ == "__main__":
    main()

