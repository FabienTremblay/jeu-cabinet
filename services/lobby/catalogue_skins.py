from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class EntreeCatalogueSkin:
    skin_id: str
    nom: str
    type: str
    statut: str
    chargeable: bool
    source: dict[str, Any]
    description: str


def chemin_catalogue() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidat = parent / "donnees" / "cabinet" / "skins" / "catalogue.yaml"
        if candidat.exists():
            return candidat
    return Path("/app/donnees/cabinet/skins/catalogue.yaml")


def charger_catalogue() -> dict[str, EntreeCatalogueSkin]:
    chemin = chemin_catalogue()
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
            nom=str(entree.get("nom") or skin_id),
            type=str(entree.get("type", "")),
            statut=str(entree.get("statut", "")),
            chargeable=bool(entree.get("chargeable", False)),
            source=_source(entree),
            description=str(entree.get("description", "")),
        )
    return catalogue


def lister_entrees_chargeables() -> list[EntreeCatalogueSkin]:
    return [entree for entree in charger_catalogue().values() if entree.chargeable]


def trouver_entree_catalogue(skin_id: str) -> EntreeCatalogueSkin | None:
    return charger_catalogue().get(skin_id)


def _source(entree: dict[str, Any]) -> dict[str, Any]:
    source = entree.get("source", {})
    if not isinstance(source, dict):
        raise ValueError("La source d’une entrée catalogue doit être un objet YAML")
    return dict(source)
