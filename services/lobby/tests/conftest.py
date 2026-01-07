# services/lobby/tests/conftest.py
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from services.lobby.settings import Settings
from services.lobby.repositories import JoueurRepository, TableRepository
from services.lobby.services_lobby import ServiceLobby
from services.lobby.kafka_producteur import ProducteurEvenements
from services.lobby.events import Evenement
from services.lobby.app import app
from services.lobby.deps import get_service_lobby


class ProducteurEvenementsMemoire(ProducteurEvenements):
    """Producteur d'événements de test qui garde tout en mémoire."""

    def __init__(self) -> None:
        self.evenements: list[tuple[str, Evenement]] = []

    async def publier(self, topic: str, evenement: Evenement) -> None:
        self.evenements.append((topic, evenement))


@pytest.fixture
def settings() -> Settings:
    # On peut surcharger des valeurs au besoin
    return Settings()


@pytest.fixture
def joueur_repo() -> JoueurRepository:
    return JoueurRepository()


@pytest.fixture
def table_repo() -> TableRepository:
    return TableRepository()


@pytest.fixture
def producteur() -> ProducteurEvenementsMemoire:
    return ProducteurEvenementsMemoire()


@pytest.fixture
def service_lobby(
    settings: Settings,
    joueur_repo: JoueurRepository,
    table_repo: TableRepository,
    producteur: ProducteurEvenementsMemoire,
) -> ServiceLobby:
    return ServiceLobby(
        settings=settings,
        joueurs=joueur_repo,
        tables=table_repo,
        producteur=producteur,
    )


@pytest.fixture
def client(service_lobby: ServiceLobby) -> TestClient:
    """Client HTTP de test avec override du service_lobby."""

    def override_service_lobby() -> ServiceLobby:
        return service_lobby

    app.dependency_overrides[get_service_lobby] = override_service_lobby
    client = TestClient(app)
    return client
