# services/ui_etat_joueur/ui_etat_joueur
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
import os
import logging

from .repository import DepotEtatsUI
from .kafka_consumer import ConsommateurEvenementsUI
from .schemas import SituationJoueurDTO, mapper_etat_to_dto  # à créer comme dans l’esquisse

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

@app.on_event("startup")
def demarrer_consumer_kafka() -> None:
    bootstrap = os.getenv("UI_ETAT_KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    topic_moteur = os.getenv("UI_ETAT_TOPIC_EVENEMENTS_MOTEUR", "cab.events")
    topics_lobby = os.getenv(
        "UI_ETAT_TOPICS_LOBBY",
        "cabinet.joueurs.evenements,cabinet.tables.evenements,cabinet.parties.evenements",
    ).split(",")

    consommateur = ConsommateurEvenementsUI(
        depot=depot,
        bootstrap_servers=bootstrap,
        topic_evenements_moteur=topic_moteur,
        topics_lobby=topics_lobby,
        groupe_id="ui-etat-joueur",
    )

    def _run():
        logger.info("Thread consumer UI-etat-joueur démarré")
        consommateur.start()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ui/joueurs/{joueur_id}/situation", response_model=SituationJoueurDTO)
def lire_situation(joueur_id: str) -> SituationJoueurDTO:
    etat = depot.obtenir_ou_creer(joueur_id)
    return mapper_etat_to_dto(etat)
