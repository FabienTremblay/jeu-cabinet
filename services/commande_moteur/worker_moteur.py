# services/commande_moteur/worker_moteur.py
# rôle        : exécute les commandes Kafka à destination du moteur
# usage       : worker cab.commands vers API moteur et synchronisation lobby
# contexte    : création de partie et événements de fin de partie
# statut      : actif
from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

import requests
from kafka import KafkaConsumer, KafkaProducer

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

# événements moteur -> surveillance et, plus tard, synchronisation lobby
KAFKA_TOPIC_EVENTS = os.getenv("KAFKA_TOPIC_EVENTS", "cabinet.parties.evenements")
KAFKA_GROUP_ID_EVENTS = os.getenv("KAFKA_GROUP_ID_EVENTS", "cabinet-lobby-d600")

SURVEILLANCE_INACTIVITE_ACTIF = os.getenv("SURVEILLANCE_INACTIVITE_ACTIF", "1") == "1"
SURVEILLANCE_INACTIVITE_INTERVALLE_SECONDES = float(
    os.getenv("SURVEILLANCE_INACTIVITE_INTERVALLE_SECONDES", "5")
)

API_LOBBY_URL = os.getenv("API_LOBBY_URL", "http://lobby:8080")


@dataclass
class PartieSurveillee:
    id_partie: str
    table_id: Optional[str]
    delai_inactivite_secondes: int
    derniere_activite_at: float
    commande_timeout_produite: bool = False


PARTIES_SURVEILLEES: dict[str, PartieSurveillee] = {}


def maintenant_epoch() -> float:
    return time.time()


def horodatage_iso(ts: float | None = None) -> str:
    return datetime.fromtimestamp(ts if ts is not None else maintenant_epoch(), tz=timezone.utc).isoformat()


def horodatage_vers_epoch(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    try:
        texte = value.replace("Z", "+00:00")
        return datetime.fromisoformat(texte).timestamp()
    except ValueError:
        return None


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


def creer_producteur_commandes() -> KafkaProducer:
    logger.info(
        "Initialisation producer Kafka topic=%s bootstrap=%s",
        KAFKA_TOPIC_COMMANDS,
        KAFKA_BOOTSTRAP,
    )
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: (k or "").encode("utf-8"),
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
        enregistrer_surveillance_partie(table_id=table_id, commande=commande)
        traiter_partie_creer(table_id=table_id, commande=commande, meta=meta)
    elif op == "partie.terminer":
        traiter_partie_terminer(table_id=table_id, commande=commande, meta=meta)
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
    politique_timeout_partie = commande.get("politique_timeout_partie")
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
    if politique_timeout_partie is not None:
        body["configuration_partie"] = {
            "politique_timeout_partie": politique_timeout_partie,
        }

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


def traiter_partie_terminer(
    *,
    table_id: Optional[str],
    commande: dict[str, Any],
    meta: dict[str, Any],
) -> None:
    id_partie = commande.get("id_partie")
    if not id_partie:
        logger.warning("Commande partie.terminer sans id_partie -> ignorée")
        return

    raison = commande.get("raison") or "FIN_INCONNUE"
    idempotency_key = (
        commande.get("idempotency_key")
        or meta.get("idempotency_key")
        or f"partie-terminer:{id_partie}:{raison}"
    )

    url = f"{API_MOTEUR_URL}/parties/{id_partie}/terminer"
    body = {"raison": raison}
    headers = {"Idempotency-Key": idempotency_key}

    logger.info(
        "POST moteur terminaison %s body=%r table_id=%s idempotency_key=%s",
        url,
        body,
        table_id,
        idempotency_key,
    )

    try:
        r = requests.post(url, json=body, headers=headers, timeout=10)
    except Exception:
        logger.exception("Erreur réseau lors de l'appel terminaison à API moteur")
        return

    if r.status_code // 100 != 2:
        logger.error(
            "Échec terminaison partie=%s (HTTP %s): %s",
            id_partie,
            r.status_code,
            r.text,
        )
        return

    try:
        donnees = r.json()
    except Exception:
        donnees = r.text
    PARTIES_SURVEILLEES.pop(id_partie, None)
    logger.info("Partie terminée avec succès: %r", donnees)


# ---------------------------------------------------------------------
# Surveillance d'inactivité
# ---------------------------------------------------------------------

def extraire_politique_timeout(commande: dict[str, Any]) -> Optional[dict[str, Any]]:
    politique = commande.get("politique_timeout_partie")
    if politique is not None:
        return politique

    configuration = commande.get("configuration_partie") or {}
    if isinstance(configuration, dict):
        politique = configuration.get("politique_timeout_partie")
        if isinstance(politique, dict):
            return politique
    return None


def enregistrer_surveillance_partie(
    *,
    table_id: Optional[str],
    commande: dict[str, Any],
    maintenant: float | None = None,
) -> None:
    id_partie = commande.get("id_partie")
    if not id_partie:
        logger.warning("partie.creer sans id_partie: surveillance ignorée")
        return

    politique = extraire_politique_timeout(commande)
    if not politique:
        logger.info("Partie %s sans politique de timeout effective: surveillance ignorée", id_partie)
        return

    if politique.get("active") is not True:
        logger.info("Politique de timeout inactive pour partie=%s: surveillance ignorée", id_partie)
        return

    try:
        delai = int(politique["delai_inactivite_secondes"])
    except (KeyError, TypeError, ValueError):
        logger.warning("Politique de timeout invalide pour partie=%s: %r", id_partie, politique)
        return

    if delai <= 0:
        logger.warning("Délai de timeout invalide pour partie=%s: %r", id_partie, delai)
        return

    PARTIES_SURVEILLEES[id_partie] = PartieSurveillee(
        id_partie=id_partie,
        table_id=table_id,
        delai_inactivite_secondes=delai,
        derniere_activite_at=maintenant if maintenant is not None else maintenant_epoch(),
    )
    logger.info("Surveillance inactivité active partie=%s delai=%ss", id_partie, delai)


def extraire_partie_id_evenement(payload: dict[str, Any]) -> Optional[str]:
    partie_id = payload.get("aggregate_id")
    if partie_id:
        return str(partie_id)

    data = payload.get("data") or {}
    if isinstance(data, dict) and data.get("partie_id"):
        return str(data["partie_id"])

    evenement_payload = payload.get("payload") or {}
    if isinstance(evenement_payload, dict) and evenement_payload.get("partie_id"):
        return str(evenement_payload["partie_id"])

    return None


def mettre_a_jour_activite_depuis_evenement(payload: dict[str, Any], maintenant: float | None = None) -> None:
    partie_id = extraire_partie_id_evenement(payload)
    if not partie_id:
        return

    op_code = payload.get("op_code")
    if op_code == "partie.terminer":
        PARTIES_SURVEILLEES.pop(partie_id, None)
        logger.info("Partie terminée détectée sur cab.events: surveillance arrêtée partie=%s", partie_id)
        return

    partie = PARTIES_SURVEILLEES.get(partie_id)
    if partie is None:
        return

    ts = (
        horodatage_vers_epoch(payload.get("occurred_at"))
        or horodatage_vers_epoch(payload.get("timestamp"))
        or maintenant
        or maintenant_epoch()
    )
    partie.derniere_activite_at = max(partie.derniere_activite_at, ts)
    logger.debug("Activité partie=%s mise à jour à %s", partie_id, horodatage_iso(partie.derniere_activite_at))


def construire_commande_timeout(partie: PartieSurveillee, maintenant: float) -> dict[str, Any]:
    idempotency_key = f"timeout-inactivite:{partie.id_partie}"
    return {
        "table_id": partie.table_id,
        "commande": {
            "op": "partie.terminer",
            "id_partie": partie.id_partie,
            "raison": "TIMEOUT_INACTIVITE",
            "idempotency_key": idempotency_key,
        },
        "meta": {
            "source": "commande_moteur.surveillance_inactivite",
            "timestamp": horodatage_iso(maintenant),
            "idempotency_key": idempotency_key,
            "derniere_activite_at": horodatage_iso(partie.derniere_activite_at),
            "delai_inactivite_secondes": partie.delai_inactivite_secondes,
        },
    }


def publier_commande_timeout(producteur: KafkaProducer, partie: PartieSurveillee, maintenant: float) -> None:
    enveloppe = construire_commande_timeout(partie, maintenant)
    producteur.send(KAFKA_TOPIC_COMMANDS, key=partie.id_partie, value=enveloppe)
    producteur.flush(1.0)
    partie.commande_timeout_produite = True
    logger.warning(
        "Commande partie.terminer produite pour inactivité partie=%s delai=%ss",
        partie.id_partie,
        partie.delai_inactivite_secondes,
    )


def verifier_timeouts_inactivite(producteur: KafkaProducer, maintenant: float | None = None) -> None:
    if not SURVEILLANCE_INACTIVITE_ACTIF:
        return

    ts = maintenant if maintenant is not None else maintenant_epoch()
    for partie in list(PARTIES_SURVEILLEES.values()):
        if partie.commande_timeout_produite:
            continue

        inactive_depuis = ts - partie.derniere_activite_at
        if inactive_depuis >= partie.delai_inactivite_secondes:
            publier_commande_timeout(producteur, partie, ts)


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
    mettre_a_jour_activite_depuis_evenement(payload)

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
    prod_cmd = creer_producteur_commandes()

    logger.info("Worker moteur/lobby prêt :")
    logger.info(" - écoute commandes sur %s", KAFKA_TOPIC_COMMANDS)
    logger.info(" - écoute événements sur %s", KAFKA_TOPIC_EVENTS)

    prochaine_verification_timeout = maintenant_epoch()

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

            maintenant = maintenant_epoch()
            if maintenant >= prochaine_verification_timeout:
                try:
                    verifier_timeouts_inactivite(prod_cmd, maintenant=maintenant)
                except Exception:
                    logger.exception("Erreur vérification timeout inactivité")
                prochaine_verification_timeout = maintenant + SURVEILLANCE_INACTIVITE_INTERVALLE_SECONDES
    finally:
        cons_cmd.close()
        cons_evt.close()
        prod_cmd.close()

if __name__ == "__main__":
    main()
