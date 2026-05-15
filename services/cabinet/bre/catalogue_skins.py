from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass(frozen=True)
class EntreeCatalogueSkin:
    skin_id: str
    type: str
    statut: str
    chargeable: bool
    source: dict[str, Any]
    description: str


def racine_depot() -> Path:
    return Path(__file__).resolve().parents[3]


def chemin_catalogue() -> Path:
    return racine_depot() / "donnees" / "cabinet" / "skins" / "catalogue.yaml"


def charger_catalogue(chemin: Optional[Path] = None) -> dict[str, EntreeCatalogueSkin]:
    chemin = chemin or chemin_catalogue()
    if not chemin.exists():
        return {}

    with chemin.open(encoding="utf-8") as fichier:
        donnees = yaml.safe_load(fichier) or {}

    if not isinstance(donnees, dict):
        raise ValueError("Le catalogue des skins doit contenir un objet YAML")

    skins = donnees.get("skins", [])
    if not isinstance(skins, list):
        raise ValueError("Le catalogue des skins doit contenir une liste skins")

    catalogue: dict[str, EntreeCatalogueSkin] = {}
    for entree in skins:
        if not isinstance(entree, dict):
            raise ValueError("Chaque entrée du catalogue doit être un objet YAML")
        skin_id = entree.get("id")
        if not skin_id:
            raise ValueError("Chaque entrée du catalogue doit déclarer id")
        catalogue[str(skin_id)] = EntreeCatalogueSkin(
            skin_id=str(skin_id),
            type=str(entree.get("type", "")),
            statut=str(entree.get("statut", "")),
            chargeable=bool(entree.get("chargeable", False)),
            source=_source(entree),
            description=str(entree.get("description", "")),
        )
    return catalogue


def trouver_entree_catalogue(skin_id: str) -> Optional[EntreeCatalogueSkin]:
    return charger_catalogue().get(skin_id)


def chemin_dossier_catalogue(skin_id: str) -> Optional[Path]:
    entree = trouver_entree_catalogue(skin_id)
    if not entree:
        return None
    if entree.source.get("type") != "dossier":
        return None
    chemin = entree.source.get("chemin")
    if not chemin:
        return None
    return racine_depot() / str(chemin)


def _source(entree: dict[str, Any]) -> dict[str, Any]:
    source = entree.get("source", {})
    if not isinstance(source, dict):
        raise ValueError("La source d’une entrée catalogue doit être un objet YAML")
    return dict(source)
