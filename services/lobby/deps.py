# services/lobby/deps.py
from __future__ import annotations

from functools import lru_cache
import logging

from .ids import GenerateurIds
from .repositories import JoueurRepository, TableRepository
from .repositories_sql import Db, JoueurRepositorySQL, TableRepositorySQL
from .kafka_producteur import (
    ProducteurEvenements,
    ProducteurEvenementsLog,
    ProducteurEvenementsKafka,
)
from .settings import settings

logger = logging.getLogger(__name__)


@lru_cache
def get_generateur_ids() -> GenerateurIds:
    return GenerateurIds(mode=settings.id_mode)


@lru_cache
def get_db() -> Db:
    return Db(dsn=settings.postgres_dsn)


@lru_cache
def get_joueur_repository():
    ids = get_generateur_ids()
    backend = (settings.persistence_backend or "memory").lower().strip()
    if backend == "postgres":
        return JoueurRepositorySQL(db=get_db(), generateur_ids=ids)
    if backend == "memory":
        return JoueurRepository(generateur_ids=ids)
    raise ValueError(f"persistence_backend_invalide: {settings.persistence_backend}")


@lru_cache
def get_table_repository():
    ids = get_generateur_ids()
    backend = (settings.persistence_backend or "memory").lower().strip()
    if backend == "postgres":
        return TableRepositorySQL(db=get_db(), generateur_ids=ids)
    if backend == "memory":
        return TableRepository(generateur_ids=ids)
    raise ValueError(f"persistence_backend_invalide: {settings.persistence_backend}")


@lru_cache
def get_producteur_evenements() -> ProducteurEvenements:
    """
    Retourne un producteur Kafka si disponible.
    - si settings.kafka_actif est False → on force le LOG
    - sinon on tente ProducteurEvenementsKafka, avec fallback LOG en cas d'erreur
    """
    kafka_actif = getattr(settings, "kafka_actif", True)

    if not kafka_actif:
        logger.warning("Kafka désactivé, utilisation de ProducteurEvenementsLog")
        return ProducteurEvenementsLog()

    try:
        prod = ProducteurEvenementsKafka()
        logger.info("ProducteurEvenementsKafka initialisé")
        return prod
    except Exception:
        logger.exception("Kafka indisponible, fallback ProducteurEvenementsLog")
        return ProducteurEvenementsLog()


def get_service_lobby():
    from .services_lobby import ServiceLobby

    return ServiceLobby(
        settings=settings,
        joueurs=get_joueur_repository(),
        tables=get_table_repository(),
        producteur=get_producteur_evenements(),
    )
