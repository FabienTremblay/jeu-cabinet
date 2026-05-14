from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Optional

from services.cabinet.bre.skin_yaml import (
    SkinYaml,
    charger_skin_yaml,
    diagnostic_heritage_minimal,
)


LIBELLES_FAMILLES = {
    "cartes": "cartes",
    "evenements": "événements",
    "regles": "règles",
    "phases": "phases",
    "procedures": "procédures",
}


def chemin_skin_yaml(skin_id: str) -> Path:
    racine = Path(__file__).resolve().parents[3]
    return racine / "services" / "cabinet" / "skins" / skin_id / "skin.yaml"


def formater_diagnostic_skin(skin: SkinYaml) -> str:
    diagnostic = diagnostic_heritage_minimal(skin)
    lignes = [
        f"Skin : {diagnostic['skin_id']}",
        f"Nom : {skin.nom or '(non déclaré)'}",
        f"Version : {skin.version or '(non déclarée)'}",
        f"Difficulté : {skin.difficulte or '(non déclarée)'}",
        f"Hérite de : {diagnostic['herite_de'] or '(aucune skin parente déclarée)'}",
        "",
        "Champs déclarés :",
    ]
    lignes.extend(_liste(diagnostic["declares"]))
    lignes.append("")
    lignes.append("Familles héritées :")
    lignes.extend(_liste(_libelles_familles(diagnostic["herite"])))
    lignes.extend(
        [
            "",
            "Limite actuelle :",
            "Ce diagnostic lit l’overlay déclaratif.",
            "La fusion complète des familles héritées n’est pas encore implémentée.",
        ]
    )
    return "\n".join(lignes)


def charger_depuis_arguments(args: argparse.Namespace) -> SkinYaml:
    chemin = Path(args.skin_yaml) if args.skin_yaml else chemin_skin_yaml(args.skin_id)
    if not chemin.exists():
        raise FileNotFoundError(f"skin.yaml introuvable: {chemin}")
    return charger_skin_yaml(chemin)


def construire_parseur() -> argparse.ArgumentParser:
    parseur = argparse.ArgumentParser(
        prog="diagnostiquer_skin",
        description="Affiche le diagnostic minimal d’une skin poweruser déclarée par skin.yaml.",
    )
    parseur.add_argument(
        "skin_id",
        nargs="?",
        help="Identifiant d’une skin sous services/cabinet/skins/",
    )
    parseur.add_argument(
        "--skin-yaml",
        help="Chemin explicite vers un fichier skin.yaml.",
    )
    return parseur


def main(argv: Optional[list[str]] = None) -> int:
    parseur = construire_parseur()
    args = parseur.parse_args(argv)
    if not args.skin_id and not args.skin_yaml:
        parseur.error("indiquer un identifiant de skin ou --skin-yaml")

    try:
        skin = charger_depuis_arguments(args)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 2

    print(formater_diagnostic_skin(skin))
    return 0


def _liste(valeurs: Iterable[str]) -> list[str]:
    return [f"- {valeur}" for valeur in valeurs]


def _libelles_familles(familles: Iterable[str]) -> list[str]:
    return [LIBELLES_FAMILLES.get(famille, famille) for famille in familles]


if __name__ == "__main__":
    raise SystemExit(main())
