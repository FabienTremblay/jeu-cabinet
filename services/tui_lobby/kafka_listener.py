import json
import threading
from uuid import uuid4
from kafka import KafkaConsumer
from .config import ConfigTuiLobby


class EcouteurEvenements:
    def __init__(
        self,
        config: ConfigTuiLobby,
        filtre_joueur_id: str | None = None,
        filtre_table_id: str | None = None
    ):
        self.cfg = config
        self.filtre_joueur_id = filtre_joueur_id
        self.filtre_table_id = filtre_table_id
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def demarrer(self, callback_evenement):
        def boucle():
            consumer = KafkaConsumer(
                # événements du lobby
                self.cfg.kafka_topic_joueurs,
                self.cfg.kafka_topic_tables,
                self.cfg.kafka_topic_parties,
                # événements du moteur / domaine
                self.cfg.kafka_topic_moteur,
                bootstrap_servers=self.cfg.kafka_bootstrap,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                group_id=f"tui-{self.cfg.joueur_alias}-{uuid4().hex[:8]}",
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            )

            try:
                for msg in consumer:
                    if self._stop.is_set():
                        break

                    evt = msg.value

                    evt_id_joueur = evt.get("id_joueur")
                    evt_id_table = evt.get("id_table")

                    # si on filtre sur le joueur, on ne rejette que si l'id est présent
                    if (
                        self.filtre_joueur_id
                        and evt_id_joueur is not None
                        and evt_id_joueur != self.filtre_joueur_id
                    ):
                        continue

                    if (
                        self.filtre_table_id
                        and evt_id_table is not None
                        and evt_id_table != self.filtre_table_id
                    ):
                        continue

                    callback_evenement(evt)
            finally:
                consumer.close()

        self._thread = threading.Thread(target=boucle, daemon=True)
        self._thread.start()

    def arreter(self):
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

