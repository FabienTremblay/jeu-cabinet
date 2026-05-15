from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional

import yaml

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


@dataclass(frozen=True)
class ResumeCollectionDeclarative:
    fichier: str
    nom: str
    present: bool
    heriter: Optional[bool] = None
    ajoutes: tuple[str, ...] = ()
    remplaces: tuple[str, ...] = ()
    retires: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResumeMessagesDeclaratifs:
    fichier: str
    present: bool
    cles: tuple[str, ...] = ()


def chemin_skin_yaml(skin_id: str) -> Path:
    racine = Path(__file__).resolve().parents[3]
    return racine / "services" / "cabinet" / "skins" / skin_id / "skin.yaml"


def formater_diagnostic_skin(skin: SkinYaml) -> str:
    diagnostic = diagnostic_heritage_minimal(skin)
    contenus = resumer_contenus_declaratifs(skin.chemin.parent)
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
    lignes.append("")
    lignes.append("Contenus déclaratifs de couche 2 :")
    lignes.extend(_formater_contenus_declaratifs(contenus))
    lignes.extend(
        [
            "",
            "Limite actuelle :",
            "Ce diagnostic lit l’overlay déclaratif.",
            "La fusion complète des familles héritées n’est pas encore implémentée.",
            "La publication résolue de la skin n’est pas encore implémentée.",
        ]
    )
    return "\n".join(lignes)


def resumer_contenus_declaratifs(
    dossier_skin: Path,
) -> list[ResumeCollectionDeclarative | ResumeMessagesDeclaratifs]:
    return [
        _resumer_collection_declarative(dossier_skin, "cartes.yaml", "cartes"),
        _resumer_collection_declarative(dossier_skin, "evenements.yaml", "evenements"),
        _resumer_messages_declaratifs(dossier_skin),
    ]


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
        sortie = formater_diagnostic_skin(skin)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 2

    print(sortie)
    return 0


def _liste(valeurs: Iterable[str]) -> list[str]:
    return [f"- {valeur}" for valeur in valeurs]


def _libelles_familles(familles: Iterable[str]) -> list[str]:
    return [LIBELLES_FAMILLES.get(famille, famille) for famille in familles]


def _charger_yaml_optionnel(chemin: Path) -> dict[str, Any]:
    with chemin.open(encoding="utf-8") as fichier:
        donnees = yaml.safe_load(fichier) or {}
    if not isinstance(donnees, dict):
        raise ValueError(f"Le fichier {chemin.name} doit contenir un objet YAML")
    return donnees


def _resumer_collection_declarative(
    dossier_skin: Path, fichier: str, nom: str
) -> ResumeCollectionDeclarative:
    chemin = dossier_skin / fichier
    if not chemin.exists():
        return ResumeCollectionDeclarative(fichier=fichier, nom=nom, present=False)

    donnees = _charger_yaml_optionnel(chemin)
    section = donnees.get(nom, {})
    if not isinstance(section, dict):
        raise ValueError(f"Le bloc {nom} de {fichier} doit contenir un objet YAML")

    return ResumeCollectionDeclarative(
        fichier=fichier,
        nom=nom,
        present=True,
        heriter=bool(section.get("heriter", False)),
        ajoutes=tuple(_ids_de_collection(section.get("ajouter", []))),
        remplaces=tuple(_ids_de_collection(section.get("remplacer", []))),
        retires=tuple(_ids_de_collection(section.get("retirer", []))),
    )


def _resumer_messages_declaratifs(dossier_skin: Path) -> ResumeMessagesDeclaratifs:
    chemin = dossier_skin / "messages.yaml"
    if not chemin.exists():
        return ResumeMessagesDeclaratifs(fichier="messages.yaml", present=False)

    donnees = _charger_yaml_optionnel(chemin)
    messages = donnees.get("messages", {})
    if not isinstance(messages, dict):
        raise ValueError("Le bloc messages de messages.yaml doit contenir un objet YAML")

    return ResumeMessagesDeclaratifs(
        fichier="messages.yaml",
        present=True,
        cles=tuple(str(cle) for cle in messages.keys()),
    )


def _ids_de_collection(valeur: Any) -> list[str]:
    if valeur is None:
        return []
    if not isinstance(valeur, list):
        raise ValueError(
            "Les blocs ajouter, remplacer et retirer doivent contenir des listes"
        )

    ids: list[str] = []
    for element in valeur:
        if isinstance(element, dict):
            identifiant = element.get("id")
        else:
            identifiant = element
        if identifiant is not None:
            ids.append(str(identifiant))
    return ids


def _formater_contenus_declaratifs(
    contenus: Iterable[ResumeCollectionDeclarative | ResumeMessagesDeclaratifs],
) -> list[str]:
    lignes: list[str] = []
    for contenu in contenus:
        if isinstance(contenu, ResumeCollectionDeclarative):
            lignes.extend(_formater_collection_declarative(contenu))
        else:
            lignes.extend(_formater_messages_declaratifs(contenu))
    return lignes


def _formater_collection_declarative(
    contenu: ResumeCollectionDeclarative,
) -> list[str]:
    if not contenu.present:
        return [f"- {contenu.fichier} : absent"]

    return [
        f"- {contenu.fichier} : présent",
        f"  - hériter : {_booleen(contenu.heriter)}",
        f"  - ajoutés : {_nombre_et_ids(contenu.ajoutes)}",
        f"  - remplacés : {_nombre_et_ids(contenu.remplaces)}",
        f"  - retirés : {_nombre_et_ids(contenu.retires)}",
    ]


def _formater_messages_declaratifs(contenu: ResumeMessagesDeclaratifs) -> list[str]:
    if not contenu.present:
        return [f"- {contenu.fichier} : absent"]

    return [
        f"- {contenu.fichier} : présent",
        f"  - messages personnalisés : {_nombre_et_ids(contenu.cles)}",
    ]


def _booleen(valeur: Optional[bool]) -> str:
    if valeur is None:
        return "(non déclaré)"
    return "true" if valeur else "false"


def _nombre_et_ids(ids: Iterable[str]) -> str:
    valeurs = list(ids)
    if not valeurs:
        return "0"
    return f"{len(valeurs)} ({', '.join(valeurs)})"


if __name__ == "__main__":
    raise SystemExit(main())
