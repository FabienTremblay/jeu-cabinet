from dataclasses import dataclass
import os

@dataclass
class ConfigTuiLobby:
    base_url_lobby: str
    base_url_moteur: str
    kafka_bootstrap: str
    kafka_topic_joueurs: str
    kafka_topic_tables: str
    kafka_topic_parties: str
    kafka_topic_moteur: str
    joueur_alias: str
    joueur_email: str | None = None
    lobby_prefix: str = "/api"


def charger_config() -> ConfigTuiLobby:
    prefix_env = os.getenv("TUI_LOBBY_PREFIX", None)

    if prefix_env is None or prefix_env.strip() == "":
        # défaut : /api
        prefix = "/api"
    else:
        prefix = prefix_env.rstrip("/")
        if not prefix.startswith("/"):
            prefix = "/" + prefix

    return ConfigTuiLobby(
        base_url_lobby=os.getenv(
            "TUI_LOBBY_URL",
            "http://lobby.cabinet.localhost"
        ).rstrip("/"),
        base_url_moteur=os.getenv(
            "TUI_MOTEUR_URL",
            "http://api.cabinet.localhost"
        ).rstrip("/"),
        kafka_bootstrap=os.getenv("TUI_KAFKA_BOOTSTRAP", "kafka:9092"),
        kafka_topic_joueurs=os.getenv(
            "TUI_TOPIC_JOUEURS",
            "cabinet.joueurs.evenements"
        ),
        kafka_topic_tables=os.getenv(
            "TUI_TOPIC_TABLES",
            "cabinet.tables.evenements"
        ),
        kafka_topic_parties=os.getenv(
            "TUI_TOPIC_PARTIES",
            "cabinet.parties.evenements"
        ),
        # topic des événements de jeu / domaine (moteur)
        kafka_topic_moteur=os.getenv(
            "TUI_TOPIC_MOTEUR",
            "cab.events"
        ),
        joueur_alias=os.getenv("TUI_JOUEUR_ALIAS", "joueur1"),
        joueur_email=os.getenv("TUI_JOUEUR_EMAIL"),
        lobby_prefix=prefix,
    )

