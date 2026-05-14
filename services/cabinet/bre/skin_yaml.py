from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


FAMILLES_HERITEES_MINIMALES = ["cartes", "evenements", "regles", "phases", "procedures"]


@dataclass(frozen=True)
class SkinYaml:
    chemin: Path
    skin_id: str
    herite_de: Optional[str]
    nom: Optional[str]
    version: Optional[str]
    difficulte: Optional[str]
    donnees: Dict[str, Any]

    @property
    def declares(self) -> List[str]:
        return _chemins_declares(self.donnees)


def charger_skin_yaml(chemin: str | Path, *, overlay: bool = True) -> SkinYaml:
    chemin = Path(chemin)
    with chemin.open("r", encoding="utf-8") as fh:
        donnees = yaml.safe_load(fh) or {}

    if not isinstance(donnees, dict):
        raise ValueError("Le fichier skin.yaml doit contenir un objet YAML")

    bloc_skin = donnees.get("skin")
    if not isinstance(bloc_skin, dict):
        raise ValueError("Le fichier skin.yaml doit contenir un bloc skin")

    skin_id = bloc_skin.get("id")
    if not skin_id:
        raise ValueError("Le fichier skin.yaml doit déclarer skin.id")

    herite_de = bloc_skin.get("herite_de")
    if overlay and not herite_de:
        raise ValueError("Une skin overlay doit déclarer skin.herite_de")

    return SkinYaml(
        chemin=chemin,
        skin_id=str(skin_id),
        herite_de=str(herite_de) if herite_de else None,
        nom=_texte_optionnel(bloc_skin.get("nom")),
        version=_texte_optionnel(bloc_skin.get("version")),
        difficulte=_texte_optionnel(bloc_skin.get("difficulte")),
        donnees=donnees,
    )


def diagnostic_heritage_minimal(
    skin_yaml: SkinYaml,
    *,
    familles_heritees: Optional[List[str]] = None,
) -> Dict[str, Any]:
    return {
        "skin_id": skin_yaml.skin_id,
        "herite_de": skin_yaml.herite_de,
        "declares": skin_yaml.declares,
        "herite": list(familles_heritees or FAMILLES_HERITEES_MINIMALES),
    }


def _texte_optionnel(valeur: Any) -> Optional[str]:
    if valeur is None:
        return None
    return str(valeur)


def _chemins_declares(donnees: Dict[str, Any]) -> List[str]:
    chemins: List[str] = []

    def visiter(prefixe: str, valeur: Any) -> None:
        if isinstance(valeur, dict):
            for cle, sous_valeur in valeur.items():
                prochain = f"{prefixe}.{cle}" if prefixe else str(cle)
                visiter(prochain, sous_valeur)
            return
        chemins.append(prefixe)

    visiter("", donnees)
    return chemins
