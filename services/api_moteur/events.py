# services/api_moteur/events.py
from __future__ import annotations

import os, json, uuid, logging, time
from typing import Any, Dict, Optional
from datetime import datetime, timezone

from .settings import settings

from ..cabinet.moteur.events import EvenementDomaine  # import domaine

logger = logging.getLogger("events")

DISABLE_KAFKA = os.getenv("DISABLE_KAFKA", "0") == "1"
_topic = settings.topic_evenements

_producer = None

def _ensure_topic():
    try:
        from kafka.admin import KafkaAdminClient, NewTopic
        admin = KafkaAdminClient(bootstrap_servers=settings.kafka_bootstrap, client_id="api-moteur-admin")
        topics = admin.list_topics()
        if _topic not in topics:
            admin.create_topics([NewTopic(name=_topic, num_partitions=3, replication_factor=1)])
            logger.info("Topic créé: %s", _topic)
        admin.close()
    except Exception as e:
        # non bloquant s’il est déjà créé ou si l’ACL empêche la création auto
        logger.info("Vérif/création du topic ignorée (%s)", e)

def _get_producer():
    global _producer
    if _producer is not None:
        return _producer
    if DISABLE_KAFKA:
        return None

    from kafka import KafkaProducer
    # petit retry pour le temps que le broker devienne prêt
    for i in range(10):
        try:
            _ensure_topic()
            _producer = KafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: (k or "").encode("utf-8"),
                acks="all",
                linger_ms=5,
            )
            logger.info("KafkaProducer prêt (%s)", settings.kafka_bootstrap)
            return _producer
        except Exception as e:
            logger.warning("Kafka indisponible (tentative %s/10): %s", i + 1, e)
            time.sleep(1 + i * 0.2)
    logger.error("Kafka restera désactivé pour cette exécution.")
    return None


class KafkaEventPublisher:
    def __init__(self, producer, topic: str = "cab.events") -> None:
        self._producer = producer
        self._topic = topic

    def publier(self, evt: EvenementDomaine,
                correlation_id: str | None = None,
                causation_id: str | None = None,
                source: str = "moteur") -> None:

        envelope = {
            "event_id": str(uuid.uuid4()),
            "event_type": evt.event_type,
            "event_version": 1,
            "occurred_at": evt.occurred_at.isoformat(),

            "aggregate_type": evt.aggregate_type,
            "aggregate_id": evt.aggregate_id,

            "process_code": evt.process_code,
            "process_instance_id": evt.process_instance_id,

            "op_family": evt.op_family,
            "op_code": evt.op_code,
            "category": evt.category,
            "requires_action": evt.requires_action,
            "recipients": evt.recipients,
            "severity": evt.severity,

            "correlation_id": correlation_id,
            "causation_id": causation_id,
            "source": source,

            "metadata": evt.metadata,
            "data": evt.data,
        }

        prod = self._producer or _get_producer()
        if not prod:
            logger.info("[NO-KAFKA-DOMAIN] %s", envelope)
            return

        try:
            prod.send(self._topic, key=evt.aggregate_id, value=envelope)
            prod.flush(1.0)
        except Exception as e:
            logger.exception("Échec publication Kafka (domain): %s", e)


def publier_evenement(type_evt: str, payload: Dict[str, Any], partition_key: Optional[str] = None, correlation_id: Optional[str] = None):
    evt = {
        "id": str(uuid.uuid4()),
        "type": type_evt,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id,
        "payload": payload,
        "schema_version": 1,
    }

    prod = _get_producer()
    if not prod:
        logger.info("[NO-KAFKA] %s", evt)
        return

    try:
        prod.send(_topic, key=partition_key, value=evt)
        # flush léger pour dev ; en prod, on laissera le buffer travailler
        prod.flush(1.0)
        logger.info("Événement publié → %s (key=%s)", _topic, partition_key)
    except Exception as e:
        logger.exception("Échec publication Kafka: %s", e)

def publier_evenements_domaine(
    evenements: list[EvenementDomaine],
    partition_key: Optional[str] = None,
    correlation_id: Optional[str] = None,
    causation_id: Optional[str] = None,
) -> None:
    """
    Publie une liste d'EvenementDomaine sur le topic cab.events.
    """
    if not evenements:
        return

    prod = _get_producer()
    if not prod:
        for evt in evenements:
            logger.info("[NO-KAFKA-DOMAIN] %s", evt)
        return

    publisher = KafkaEventPublisher(producer=prod, topic=_topic)

    for evt in evenements:
        publisher.publier(
            evt,
            correlation_id=correlation_id,
            causation_id=causation_id,
            source="api-moteur",
        )

def _evt_to_payload(evt: Any) -> dict:
    """
    Convertit un événement domaine en dict JSON-sérialisable pour les événements 'simples'.
    À ajuster selon la vraie structure de tes événements.
    """
    if evt is None:
        return {}

    # Si ton événement a une méthode to_dict()
    to_dict = getattr(evt, "to_dict", None)
    if callable(to_dict):
        return to_dict()

    # Fallback générique pour dataclasses / objets simples
    # (si tu utilises dataclasses.asdict quelque part, c'est l'endroit idéal)
    data = {}
    for attr in ("type", "code", "categorie", "op_code", "op_family", "data", "metadata"):
        if hasattr(evt, attr):
            value = getattr(evt, attr)
            # idéalement, tu garantis déjà que data/metadata sont JSON-compatibles
            data[attr] = value
    return data

