# services/cabinet/moteur/config_loader.py
from __future__ import annotations
from typing import Dict, Callable, Any, Deque, List
from collections import deque
import random, copy, importlib
import os

from .etat import Etat, Axe, Economie, Joueur, DeckState, EventDeckState, EtatOpposition
from .regles_interfaces import ReglesInterface

def _charger_skin_module(skin: str):
    # __package__ vaut "services.cabinet.moteur"
    root = __package__.split('.')[0]  # -> "services"
    module_name = f"{root}.cabinet.skins.{skin}"
    print(f"Le skin à charger : {module_name}")
    return importlib.import_module(module_name)

def charger_config_et_regles(skin: str) -> tuple[Dict[str, Any], ReglesInterface]:
    mod = _charger_skin_module(skin)

    get_config = getattr(mod, "get_config", None)
    if not callable(get_config):
        raise ValueError(f"Skin {skin} ne fournit pas get_config()")

    cfg = get_config()

    get_regles = getattr(mod, "get_regles", None)
    if not callable(get_regles):
        raise ValueError(f"Skin {skin} ne fournit pas get_regles()")

    regles_impl: ReglesInterface = get_regles()

    return cfg, regles_impl

def _melanger_deque(items: List[str]) -> Deque[str]:
    tmp = items[:]
    random.shuffle(tmp)
    return deque(tmp)

ALLOWED_CARD_TYPES = {
    "mesure",
    "amendement",
    "procedure",
    "evenement",
    "influence",
    "contre_coup",
    "ministere",
    "relation",
}

def _normaliser_et_valider_skin(cfg: Dict[str, Any]) -> Dict[str, Any]:
    cfg = copy.deepcopy(cfg)

    # --- cartes programme ---
    cartes = cfg.get("cartes", [])
    for c in cartes:
        if "id" not in c:
            raise ValueError("Carte sans 'id' dans la skin")

        c.setdefault("type", "mesure")
        ctype = c["type"]
        if ctype not in ALLOWED_CARD_TYPES:
            raise ValueError(f"Type de carte inconnu: {ctype} pour {c['id']}")

        # cartes de fond : doivent avoir commandes ou effet (pour fallback)
        if ctype in ("mesure", "amendement"):
            if "commandes" not in c and "effet" not in c:
                raise ValueError(f"Carte {c['id']} sans 'commandes' ni 'effet'")

        # validation minimale des commandes si présentes
        for cmd in c.get("commandes", []):
            if "op" not in cmd:
                raise ValueError(f"Commande sans 'op' dans la carte {c['id']}")

    # --- événements monde ---
    events = cfg.get("events", [])
    for e in events:
        if "id" not in e:
            raise ValueError("Event sans 'id' dans la skin")

        e.setdefault("type", "evenement")
        etype = e["type"]
        if etype not in ALLOWED_CARD_TYPES:
            raise ValueError(f"Type d'événement inconnu: {etype} pour {e['id']}")

        if "commandes" not in e and "effet" not in e:
            raise ValueError(f"Event {e['id']} sans 'commandes' ni 'effet'")

        for cmd in e.get("commandes", []):
            if "op" not in cmd:
                raise ValueError(f"Commande sans 'op' dans l'event {e['id']}")

    return cfg

def construire_etat(
    skin: str,
    partie_id: str,
    joueurs: Dict[str, Any],
    seed: int | None = None,
    regles: ReglesInterface | None = None,
) -> Etat:
    """Construit un Etat initial à partir d'un skin (défini par un package Python)."""
    if seed is not None:
        random.seed(seed)

    cfg, regles_impl = charger_config_et_regles(skin)
    cfg = _normaliser_et_valider_skin(cfg)

    axes = {
        a["id"]: Axe(
            id=a["id"],
            valeur=a.get("valeur_init", 5),
            seuil_crise=a.get("seuil_crise", 8),
            poids=a.get("poids", 1.0),
        )
        for a in cfg["axes"]
    }

    eco = Economie(**cfg["economie"])

    # si on force des règles en paramètre, elles écrasent celles du skin
    if regles is not None:
        regles_impl = regles

    cartes_def = {c["id"]: c for c in cfg["cartes"]}
    for e in cfg.get("events", []):
        cartes_def[e["id"]] = e

    deck_ids: list[str] = []
    for c in cfg["cartes"]:
        if c.get("dans_deck_global", True):
            copies = int(c.get("copies", c.get("nb_exemplaires", 1)))
            deck_ids.extend([c["id"]] * max(1, copies))

    deck_global = DeckState(pioche=_melanger_deque(deck_ids), defausse=deque())
    deck_events = EventDeckState(
        pioche=_melanger_deque([e["id"] for e in cfg.get("events", [])]),
        defausse=deque(),
    )
    joueurs_map = {}
    for jid, info in joueurs.items():
        joueurs_map[jid] = Joueur(
            id=jid,
            nom=info.get("nom", ""),
            alias=info.get("alias", ""),
            role=info.get("role", ""),
            capital_politique=cfg.get("capital_init", 0),
        )

    etat = Etat(
        id=partie_id,
        skin=skin,
        tour=1,
        axes=axes,
        eco=eco,
        joueurs=joueurs_map,
        programme=None,
        regles=regles_impl,
        capital_collectif=cfg.get("capital_collectif_init", 0),
        opposition=EtatOpposition(
            capital_politique=cfg.get("capital_opposition_init", 0),
            donnees_skin=cfg.get("opposition_skin_init", {}),
        ),
        analyse_skin=cfg.get("analyse_skin_init", {}),
        cartes_def=cartes_def,
        deck_global=deck_global,
        main_init=cfg.get("main_init", 3),
        deck_events=deck_events,
        sous_phase_order=tuple(
            cfg.get(
                "phases_tour",
                ("monde", "conseil", "vote_programme", "amendements", "execution_programme", "cloture_tour"),
            )
        ),
        sous_phase_signals=cfg.get(
            "phases_signals",
            {
                "monde": "on_start_monde",
                "conseil": "on_conseil",
                "vote_programme": "on_vote_programme",
                "amendements": "on_amendements",
                "execution_programme": "on_execution_programme",
                "cloture_tour": "on_cloture_tour",
            },
        ),
    )
    return etat

