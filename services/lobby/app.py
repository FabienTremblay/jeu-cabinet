# services/lobby/app.py
# rôle        : expose l'API HTTP du service lobby
# usage       : routes FastAPI pour joueurs, tables, parties et skins
# contexte    : façade HTTP du lobby et synchronisation fin de partie
# statut      : actif
from __future__ import annotations

import os

import logging
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    DemandeInscription,
    DemandeConnexion,
    DemandeCreationTable,
    DemandeConfigurationTable,
    DemandePriseSiege,
    DemandeJoueurPret,
    DemandeLancerPartie,
    DemandeTerminerPartie,
    ReponseConnexion,
    ReponseInscription,
    ReponseJoueur,
    ReponseListeJoueursLobby,
    ReponseJoueurTable,
    ReponseJoueurSiege,
    ReponseListeJoueursTable,
    ReponseTable,
    ReponseListeTables,
    ReponsePartieLancee,
    ReponseListeSkins,
    ReponseContexteReprise,
)


from .services_lobby import ServiceLobby
from .deps import get_service_lobby
from .domaine import StatutTable

logger = logging.getLogger(__name__)

app = FastAPI(title="Service Lobby")
# En dev, on autorise le front React
raw_origins = os.getenv(
    "CORS_ORIGINS",
    # Fallback sur les adresses de développement.
    ",".join([
        "http://localhost:5173",
        "http://ui-web.cabinet.localhost",
        "http://ui-etat.cabinet.localhost",
        "http://192.168.2.11:5173",
        "http://192.168.2.11:8000",
    ])
)

origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,   # on ne gère pas (encore) de cookies côté front
    allow_methods=["*"],       # GET, POST, OPTIONS, etc.
    allow_headers=["*"],       # Content-Type, Authorization, etc.
)
logger.info("CORS origins autorisées: %s", origins)


@app.get("/health")
async def health():
    return {"statut": "ok"}


# ---------------------------------------------------------------------------
# Joueurs
# ---------------------------------------------------------------------------


@app.post("/api/joueurs", response_model=ReponseInscription)
async def inscription(
    demande: DemandeInscription,
    service: ServiceLobby = Depends(get_service_lobby),
):
    # Le service lève déjà des HTTPException si besoin
    return await service.inscrire_joueur(demande)


@app.post("/api/sessions", response_model=ReponseConnexion)
async def connexion(
    demande: DemandeConnexion,
    service: ServiceLobby = Depends(get_service_lobby),
):
    return await service.connecter_joueur(demande)

@app.get("/api/joueurs/lobby", response_model=ReponseListeJoueursLobby)
async def lister_joueurs_lobby(
    service: ServiceLobby = Depends(get_service_lobby),
):
    joueurs = await service.lister_joueurs_lobby()
    return ReponseListeJoueursLobby(joueurs=joueurs)

@app.get("/api/joueurs/{id_joueur}/contexte", response_model=ReponseContexteReprise)
async def contexte_reprise(
    id_joueur: str,
    service: ServiceLobby = Depends(get_service_lobby),
):
    return await service.contexte_reprise(id_joueur=id_joueur)


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------


@app.post("/api/tables", response_model=ReponseTable)
async def creer_table(
    demande: DemandeCreationTable,
    service: ServiceLobby = Depends(get_service_lobby),
):
    return await service.creer_table(demande)


@app.get("/api/tables", response_model=ReponseListeTables)
async def lister_tables(
    statut: str | None = Query(default=None),
    service: ServiceLobby = Depends(get_service_lobby),
):
    statut_enum: StatutTable | None = None
    if statut is not None:
        try:
            statut_enum = StatutTable(statut)
        except ValueError:
            raise HTTPException(status_code=400, detail="statut_invalide")

    tables = await service.lister_tables(statut_enum)
    return ReponseListeTables(tables=tables)

@app.get("/api/tables/{id_table}/joueurs", response_model=ReponseListeJoueursTable)
async def lister_joueurs_table(
    id_table: str,
    service: ServiceLobby = Depends(get_service_lobby),
):
    joueurs = await service.lister_joueurs_table(id_table=id_table)
    return ReponseListeJoueursTable(id_table=id_table, joueurs=joueurs)


@app.patch("/api/tables/{id_table}/configuration", response_model=ReponseTable)
async def modifier_configuration_table(
    id_table: str,
    demande: DemandeConfigurationTable,
    service: ServiceLobby = Depends(get_service_lobby),
):
    return await service.modifier_configuration_table(id_table, demande)


@app.post("/api/tables/{id_table}/joueurs", response_model=ReponseJoueurSiege)
async def joindre_table(
    id_table: str,
    demande: DemandePriseSiege,
    service: ServiceLobby = Depends(get_service_lobby),
):
    return await service.prendre_siege(id_table, demande)


@app.post("/api/tables/{id_table}/joueurs/pret", response_model=ReponseTable)
async def joueur_pret(
    id_table: str,
    demande: DemandeJoueurPret,
    service: ServiceLobby = Depends(get_service_lobby),
):
    return await service.marquer_joueur_pret(id_table, demande.id_joueur)

@app.post("/api/parties/{id_partie}/joueurs/quitter", response_model=ReponseTable)
async def quitter_partie(
    id_partie: str,
    demande: DemandeJoueurPret,  # contient id_joueur
    service: ServiceLobby = Depends(get_service_lobby),
):
    return await service.quitter_partie(id_partie=id_partie, id_joueur=demande.id_joueur)

@app.post("/api/parties/{id_partie}/terminer", response_model=ReponseTable)
async def terminer_partie(
    id_partie: str,
    demande: DemandeTerminerPartie | None = None,
    service: ServiceLobby = Depends(get_service_lobby),
):
    """
    Marque comme terminée la table associée à une partie moteur.
    Typiquement appelée par un worker qui consomme cab.D600.partie.terminer.
    """
    raison = demande.raison if demande is not None else None
    return await service.terminer_partie(id_partie=id_partie, raison=raison)

@app.post("/api/tables/{id_table}/joueurs/quitter", response_model=ReponseTable)
async def quitter_table(
    id_table: str,
    demande: DemandeJoueurPret,
    service: ServiceLobby = Depends(get_service_lobby),
):
    """
    Permet à un joueur de quitter sa table (retour au lobby).

    On réutilise DemandeJoueurPret qui ne contient que id_joueur.
    """
    return await service.quitter_table(id_table, demande.id_joueur)


@app.post("/api/tables/{id_table}/terminer", response_model=ReponseTable)
async def terminer_table(
    id_table: str,
    service: ServiceLobby = Depends(get_service_lobby),
):
    """
    Marque une table comme terminée côté lobby.
    Typiquement appelée par un worker de fin de partie.
    """
    return await service.terminer_table(id_table)



@app.post("/api/tables/{id_table}/lancer", response_model=ReponsePartieLancee)
async def lancer_partie(
    id_table: str,
    demande: DemandeLancerPartie,
    service: ServiceLobby = Depends(get_service_lobby),
):
    return await service.lancer_partie(id_table, demande.id_hote)

# ---------------------------------------------------------------------------
# Skins
# ---------------------------------------------------------------------------

@app.get("/api/skins", response_model=ReponseListeSkins)
async def lister_skins(
    service: ServiceLobby = Depends(get_service_lobby),
):
    return await service.lister_skins()
