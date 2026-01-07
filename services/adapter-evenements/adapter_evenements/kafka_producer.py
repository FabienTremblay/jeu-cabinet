from __future__ import annotations
from kafka import KafkaProducer
import json
import logging
import os

logger = logging.getLogger(__name__)


class Producer:
    def __init__(self):
        bootstrap = os.getenv("ADAPTER_KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        logger.info("Adapter: KafkaProducer vers %s", bootstrap)

        self._producer = KafkaProducer(
            bootstrap_servers=[bootstrap],
            key_serializer=lambda v: v.encode("utf-8"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    def publier(self, topic: str, key: str, message: dict):
        logger.info("Adapter → Kafka topic=%s key=%s", topic, key)
        self._producer.send(topic, key=key, value=message)

