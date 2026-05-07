# services/lobby/settings.py
# rôle        : centralise la configuration du service lobby
# usage       : chargement des variables d'environnement LOBBY_*
# contexte    : Kafka, persistance, ids et politique de timeout
# statut      : actif
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration du service lobby."""

    # identité service
    nom_service: str = "lobby"

    # kafka
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_evenements_joueurs: str = "cabinet.joueurs.evenements"
    kafka_topic_evenements_tables: str = "cabinet.tables.evenements"
    kafka_topic_evenements_parties: str = "cabinet.parties.evenements"

    # politique par défaut appliquée à chaque nouvelle table.
    # La partie recevra une copie effective au lancement.
    timeout_partie_actif: bool = True
    timeout_partie_delai_inactivite_secondes: int = 3600

    # persistance
    # - memory : comportement actuel (tests/essais rapides)
    # - postgres : persistance durable
    persistence_backend: str = "memory"  # memory | postgres
    postgres_dsn: str = "postgresql://jeu:Jeu-postgres@postgres:5432/jeu"

    # génération des ids
    # - sequentiel : J000001 etc (parfait pour essais et scripts)
    # - uuid : ids non collisionnels (parfait pour prod + kafka)
    id_mode: str = "sequentiel"  # sequentiel | uuid

    # optionnel : désactiver kafka
    kafka_actif: bool = True

    class Config:
        env_prefix = "LOBBY_"
        case_sensitive = False


settings = Settings()
