# projection/regles.py

from .phase import traiter_phase
from .tour import traiter_tour
from .attente import traiter_attente
from .partie import traiter_partie
from .notifications import traiter_notification
from .autres import traiter_autres

REGLES_PROJECTION = {
    "PHASE": traiter_phase,
    "TOUR": traiter_tour,
    "ATTENTE": traiter_attente,
    "PARTIE": traiter_partie,
    "NOTIF": traiter_notification,
    "DECK": traiter_autres,
    "JOUEUR": traiter_autres,
    "AXES": traiter_autres,
    "PROGRAMME": traiter_autres,
    # tout le reste → attention seulement
}
