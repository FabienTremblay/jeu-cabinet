from __future__ import annotations
from kafka import KafkaConsumer
import json
import os


def creer_consumer(topic: str) -> KafkaConsumer:
    bootstrap = os.getenv("ADAPTER_KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    group_id = os.getenv("ADAPTER_CONSUMER_GROUP", "adapter-evenements")

    return KafkaConsumer(
        topic,
        bootstrap_servers=[bootstrap],
        group_id=group_id,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        key_deserializer=lambda v: v.decode("utf-8") if v else None,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

