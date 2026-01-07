# services/lobby/kafka_producteur.py
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Protocol

from kafka import KafkaProducer

logger = logging.getLogger(__name__)


class Evenement(Protocol):
    """Contrat minimal pour nos événements de domaine (Pydantic BaseModel)."""

    def json(self) -> str:
        ...


class ProducteurEvenements(Protocol):
    """Contrat minimal pour publier des événements de domaine."""

    async def publier(self, topic: str, evenement: Evenement) -> None:
        ...


@dataclass
class ProducteurEvenementsKafka(ProducteurEvenements):
    """
    Producteur Kafka réel pour les événements du lobby.

    - utilise LOBBY_KAFKA_BOOTSTRAP_SERVERS (docker-compose) ou kafka:9092 par défaut
    - sérialise les événements en JSON via evenement.json()
    """

    bootstrap_servers: str = field(
        default_factory=lambda: os.getenv("LOBBY_KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    )
    _producer: KafkaProducer = field(init=False, repr=False)

    def __post_init__(self) -> None:
        logger.info("Initialisation ProducteurEvenementsKafka vers %s", self.bootstrap_servers)
        # value_serializer → on envoie des str JSON, encodées en UTF-8
        self._producer = KafkaProducer(
            bootstrap_servers=[self.bootstrap_servers],
            value_serializer=lambda v: v.encode("utf-8"),
        )

    async def publier(self, topic: str, evenement: Evenement) -> None:
        payload = evenement.json()
        logger.debug("Publication événement Kafka topic=%s payload=%s", topic, payload)

        # kafka-python est synchrone, mais send() est très rapide et non bloquant en temps normal.
        # Pour le moment on fait simple : fire-and-forget, sans attendre l'ack.
        try:
            self._producer.send(topic, payload)
        except Exception:
            logger.exception("Erreur lors de l'envoi de l'événement sur Kafka (topic=%s)", topic)
            # On ne remonte pas l'exception pour ne pas casser la requête HTTP,
            # mais tu pourrais décider le contraire plus tard.


@dataclass
class ProducteurEvenementsLog(ProducteurEvenements):
    """
    Implémentation de développement : ne publie pas sur Kafka,
    mais écrit simplement l’événement dans les logs.
    """

    async def publier(self, topic: str, evenement: Evenement) -> None:
        message = f"Événement publié sur [EVT LOG] topic={topic} payload={evenement.json()}"
        logger.warning(message)

