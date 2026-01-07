# services/ui_etat_joueur/app.py
from __future__ import annotations

import logging
import os
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .repository import DepotEtatsUI
from .kafka_consumer import ConsommateurEvenementsUI
from .schemas import SituationJoueurDTO, mapper_etat_to_dto

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

depot = DepotEtatsUI()
app = FastAPI(title="Service UI - Etat joueur", version="0.1.0")

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

def demarrer_consumer_kafka() -> None:
    bootstrap = os.getenv("UI_ETAT_KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    group_id = os.getenv("UI_ETAT_KAFKA_GROUP_ID", "cabinet-ui-etat-v1")
    topic_moteur = os.getenv("UI_ETAT_TOPIC_EVENEMENTS_MOTEUR", "cab.events")
    topics_lobby_raw = os.getenv(
        "UI_ETAT_TOPICS_LOBBY",
        "cabinet.joueurs.evenements,cabinet.tables.evenements,cabinet.parties.evenements",
    )
    topics_lobby = [t.strip() for t in topics_lobby_raw.split(",") if t.strip()]

    logger.info("UI-etat: bootstrap_servers=%s", bootstrap)

    consommateur = ConsommateurEvenementsUI(
        depot=depot,
        bootstrap_servers=bootstrap,
        group_id=group_id,
        topic_moteur=topic_moteur,
        topics_lobby=topics_lobby,
    )

    def _run_consommation() -> None:
        consommateur.boucle()

    thread = threading.Thread(target=_run_consommation, daemon=True)
    thread.start()
    logger.info("Thread consumer UI-etat-joueur démarré")

    # démarrer la boucle de fermeture
    def _run_fermeture() -> None:
        consommateur._boucle_fermeture()

    t2 = threading.Thread(target=_run_fermeture, daemon=True)
    t2.start()
    logger.info("Thread boucle de fermeture UI-etat-joueur démarré")


@app.on_event("startup")
def on_startup() -> None:
    demarrer_consumer_kafka()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ui/joueurs/{joueur_id}/situation", response_model=SituationJoueurDTO)
def lire_situation(joueur_id: str) -> SituationJoueurDTO:
    etat = depot.obtenir_ou_creer(joueur_id)
    return mapper_etat_to_dto(etat)

