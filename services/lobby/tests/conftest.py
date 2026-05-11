# services/lobby/tests/conftest.py
# rôle        : configure les fixtures de tests du lobby
# usage       : dépôts mémoire, producteur factice et client ASGI de test
# contexte    : tests backend HTTP et service du lobby
# statut      : actif
from __future__ import annotations

import asyncio

import httpx
import pytest

from services.lobby.settings import Settings
from services.lobby.repositories import JoueurRepository, SessionRepository, TableRepository
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


class ClientASGITest:
    def __init__(self, app):
        self._app = app

    def request(self, method: str, path: str, **kwargs):
        async def _request():
            transport = httpx.ASGITransport(app=self._app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://testserver",
            ) as client:
                return await client.request(method, path, **kwargs)

        return asyncio.run(_request())

    def get(self, path: str, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self.request("POST", path, **kwargs)

    def patch(self, path: str, **kwargs):
        return self.request("PATCH", path, **kwargs)


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
def session_repo() -> SessionRepository:
    return SessionRepository()


@pytest.fixture
def producteur() -> ProducteurEvenementsMemoire:
    return ProducteurEvenementsMemoire()


@pytest.fixture
def service_lobby(
    settings: Settings,
    joueur_repo: JoueurRepository,
    table_repo: TableRepository,
    session_repo: SessionRepository,
    producteur: ProducteurEvenementsMemoire,
) -> ServiceLobby:
    return ServiceLobby(
        settings=settings,
        joueurs=joueur_repo,
        tables=table_repo,
        sessions=session_repo,
        producteur=producteur,
    )


@pytest.fixture
def client(service_lobby: ServiceLobby) -> ClientASGITest:
    """Client HTTP de test avec override du service_lobby."""

    async def override_service_lobby() -> ServiceLobby:
        return service_lobby

    app.dependency_overrides[get_service_lobby] = override_service_lobby
    return ClientASGITest(app)
