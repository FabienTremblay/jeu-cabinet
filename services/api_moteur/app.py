# services/api_moteur/app.py

from fastapi import FastAPI, APIRouter, Depends, Header, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from collections import deque
from typing import Optional
import uuid
import os
import logging

from .deps import get_manager
from .schemas import *
from .events import publier_evenement, publier_evenements_domaine, _evt_to_payload

from .rules_client import evaluer_decision


logger = logging.getLogger(__name__)

app = FastAPI(title="API Moteur - Conseil des ministres", version="1.0.0")
api = APIRouter(prefix="/moteur/v1") 
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

def corr_id(x_correlation_id: Optional[str] = Header(None)) -> str:
    return x_correlation_id or str(uuid.uuid4())

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/version")
def version():
    return {"name": "api-moteur", "version": "1.0.0"}

@app.post("/parties", response_model=ReponseEtat)
def creer_partie(req: RequetePartie, manager=Depends(get_manager), correlation_id: str = Depends(corr_id)):
    # validations simples
    if not isinstance(req.joueurs, dict) or len(req.joueurs) < 1:
        raise HTTPException(status_code=422, detail={"code": "JOUEURS_REQUIS", "message": "Au moins un joueur requis."})
    for jid, info in req.joueurs.items():
        if not str(jid).strip():
            raise HTTPException(
                status_code=422,
                detail={"code": "JOUEUR_INVALIDE", "message": "Id joueur vide."},
            )

        if isinstance(info, str):
            pseudo = info
        elif isinstance(info, dict):
            pseudo = (info.get("alias") or info.get("nom") or "").strip()
        else:
            pseudo = str(info).strip()

        if not pseudo:
            raise HTTPException(
                status_code=422,
                detail={"code": "JOUEUR_INVALIDE", "message": "Pseudo / nom joueur manquant."},
                )
    options = req.options or {}
    partie_id = (
           req.partie_id
        or str(uuid.uuid4())
    )

    etat = manager.creer(
        skin=req.skin_jeu,
        partie_id=partie_id,
        joueurs=req.joueurs,
        seed=req.seed,
    )
    # 1) ancien événement simple
    publier_evenement(
        "event.partie.creee",
        {
            "partie_id": partie_id,
            "nom": req.nom,
            "joueurs": req.joueurs,
            "seed": req.seed,
        },
        partition_key=partie_id,
    )
    manager.demarrer_partie(partie_id)
    # 2) nouveaux événements de domaine (si Etat en a émis dans _on_mise_en_place/demarrer_partie)
    try:
        evenements = etat.vider_evenements()
    except AttributeError:
        evenements = []
    publier_evenements_domaine(evenements, partition_key=partie_id, correlation_id=correlation_id)

    # réponse API
    etat_dict = jsonable_encoder(etat, custom_encoder={deque: list})
    return {"partie_id": partie_id, "etat": etat_dict}


@app.get("/parties/{partie_id}/etat", response_model=ReponseEtat)
def lire_etat(partie_id: str, manager=Depends(get_manager), correlation_id: str = Depends(corr_id)):
    etat = manager.get(partie_id)
    if etat is None:
        raise HTTPException(status_code=404, detail={"code": "PARTIE_ABSENTE"})
    return {"partie_id": partie_id, "etat": jsonable_encoder(etat, custom_encoder={deque: list})}

@app.post("/parties/{partie_id}/joueurs", response_model=ReponseEtat)
def ajouter_joueur(partie_id: str, req: RequeteJoueur, manager=Depends(get_manager), correlation_id: str = Depends(corr_id)):
    etat = manager.ajouter_joueur(partie_id, req.joueur_id, req.pseudo)
    publier_evenement("event.joueur.ajoute", {"partie_id": partie_id, "joueur_id": req.joueur_id})
    evenements = getattr(etat, "vider_evenements", lambda: [])()
    publier_evenements_domaine(evenements, partition_key=partie_id, correlation_id=correlation_id)

    return {"partie_id": partie_id, "etat": jsonable_encoder(etat, custom_encoder={deque: list})}

@app.post("/parties/{partie_id}/actions", response_model=ReponseEtat, status_code=202)
def soumettre_action(partie_id: str, req: RequeteAction, manager=Depends(get_manager), correlation_id: str = Depends(corr_id), idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")):
    # à toi d’implémenter l’idempotence côté manager si besoin
    etat, evt = manager.appliquer_action(partie_id, req.acteur, req.type_action, req.donnees)

    evt_payload = _evt_to_payload(evt)
    publier_evenement("event.action.appliquee", {"partie_id": partie_id, "evt": evt_payload})
    evenements = getattr(etat, "vider_evenements", lambda: [])()
    publier_evenements_domaine(evenements, partition_key=partie_id, correlation_id=correlation_id)

    return {"partie_id": partie_id, "etat": jsonable_encoder(etat, custom_encoder={deque: list})}


app.include_router(api)

