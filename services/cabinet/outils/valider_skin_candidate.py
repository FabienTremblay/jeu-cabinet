from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional

import yaml

from services.cabinet.bre.catalogue_skins import chemin_dossier_catalogue
from services.cabinet.bre.skin_yaml import SkinYaml, charger_skin_yaml


MARQUEUR_A_REMPLACER = "A_REMPLACER_"
FICHIERS_COLLECTIONS = {
    "cartes.yaml": "cartes",
    "evenements.yaml": "evenements",
}
SECTIONS_COLLECTION = {"heriter", "ajouter", "remplacer", "retirer"}
VALIDATIONS_PARENT_FUTURES = [
    "ajouter ne doit pas viser un id déjà hérité du parent",
    "remplacer doit viser un id existant dans le parent",
    "retirer doit viser un id existant dans le parent",
    "les effets référencés doivent être connus",
    "les axes référencés doivent exister",
]


@dataclass(frozen=True)
class ValidationCandidate:
    skin_id: str
    chemin: Path
    erreurs: tuple[str, ...]
    avertissements: tuple[str, ...]

    @property
    def valide(self) -> bool:
        return not self.erreurs


@dataclass(frozen=True)
class OptionsValidation:
    verifier_nom_dossier: bool = False


def chemin_skin_dir(skin_id: str) -> Path:
    dossier_catalogue = chemin_dossier_catalogue(skin_id)
    if dossier_catalogue is not None:
        return dossier_catalogue
    racine = Path(__file__).resolve().parents[3]
    return racine / "services" / "cabinet" / "skins" / skin_id


def valider_skin_candidate(
    dossier_skin: Path,
    *,
    options: OptionsValidation = OptionsValidation(),
) -> ValidationCandidate:
    dossier_skin = Path(dossier_skin)
    erreurs: list[str] = []
    avertissements: list[str] = []

    skin: Optional[SkinYaml] = None
    chemin_skin_yaml = dossier_skin / "skin.yaml"
    try:
        skin = charger_skin_yaml(chemin_skin_yaml)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        erreurs.append(f"skin.yaml invalide: {exc}")

    if skin:
        if _contient_marqueur(skin.donnees):
            erreurs.append("skin.yaml contient un marqueur A_REMPLACER_*")
        if options.verifier_nom_dossier and skin.skin_id != dossier_skin.name:
            erreurs.append(
                f"skin.id ({skin.skin_id}) ne correspond pas au dossier ({dossier_skin.name})"
            )
        if not skin.version:
            avertissements.append("skin.version n’est pas déclarée")

    for fichier, section in FICHIERS_COLLECTIONS.items():
        _valider_collection(dossier_skin / fichier, section, erreurs, avertissements)

    _valider_messages(dossier_skin / "messages.yaml", erreurs, avertissements)

    return ValidationCandidate(
        skin_id=skin.skin_id if skin else dossier_skin.name,
        chemin=dossier_skin,
        erreurs=tuple(erreurs),
        avertissements=tuple(avertissements),
    )


def formater_validation(validation: ValidationCandidate) -> str:
    lignes = [
        f"Validation skin candidate : {validation.skin_id}",
        f"Dossier : {validation.chemin}",
        f"Statut : {'valide' if validation.valide else 'invalide'}",
        "",
        "Erreurs bloquantes :",
    ]
    lignes.extend(_liste(validation.erreurs, "aucune"))
    lignes.append("")
    lignes.append("Avertissements :")
    lignes.extend(_liste(validation.avertissements, "aucun"))
    lignes.append("")
    lignes.append("Validations futures dépendantes du parent :")
    lignes.extend(_liste(VALIDATIONS_PARENT_FUTURES))
    lignes.extend(
        [
            "",
            "Limite actuelle :",
            "Cette commande valide la candidate sans publier la skin.",
            "Elle ne résout pas encore l’héritage avec la skin parente.",
        ]
    )
    return "\n".join(lignes)


def construire_parseur() -> argparse.ArgumentParser:
    parseur = argparse.ArgumentParser(
        prog="valider_skin_candidate",
        description="Valide une skin candidate poweruser sans publication.",
    )
    parseur.add_argument(
        "skin_id",
        nargs="?",
        help="Identifiant d’une skin ou overlay référencé par le catalogue.",
    )
    parseur.add_argument(
        "--skin-dir",
        help="Chemin explicite vers le dossier d’une skin candidate ou brouillon.",
    )
    return parseur


def main(argv: Optional[list[str]] = None) -> int:
    parseur = construire_parseur()
    args = parseur.parse_args(argv)
    if not args.skin_id and not args.skin_dir:
        parseur.error("indiquer un identifiant de skin ou --skin-dir")

    dossier_skin = Path(args.skin_dir) if args.skin_dir else chemin_skin_dir(args.skin_id)
    validation = valider_skin_candidate(
        dossier_skin,
        options=OptionsValidation(verifier_nom_dossier=not bool(args.skin_dir)),
    )
    print(formater_validation(validation))
    return 0 if validation.valide else 1


def _valider_collection(
    chemin: Path,
    section_attendue: str,
    erreurs: list[str],
    avertissements: list[str],
) -> None:
    if not chemin.exists():
        return

    donnees = _charger_yaml(chemin, erreurs)
    if donnees is None:
        return

    if _contient_marqueur(donnees):
        erreurs.append(f"{chemin.name} contient un marqueur A_REMPLACER_*")

    for section in donnees.keys():
        if section != section_attendue:
            avertissements.append(f"{chemin.name} contient une section inconnue: {section}")

    bloc = donnees.get(section_attendue, {})
    if not isinstance(bloc, dict):
        erreurs.append(f"Le bloc {section_attendue} de {chemin.name} doit être un objet YAML")
        return

    for section in bloc.keys():
        if section not in SECTIONS_COLLECTION:
            avertissements.append(
                f"{chemin.name} contient une section inconnue dans {section_attendue}: {section}"
            )

    ids_par_operation = {
        "ajouter": _ids_de_collection(bloc.get("ajouter", []), chemin.name, "ajouter", erreurs),
        "remplacer": _ids_de_collection(
            bloc.get("remplacer", []), chemin.name, "remplacer", erreurs
        ),
        "retirer": _ids_de_collection(bloc.get("retirer", []), chemin.name, "retirer", erreurs),
    }

    for operation, ids in ids_par_operation.items():
        for identifiant in _doublons(ids):
            erreurs.append(
                f"{chemin.name}: id dupliqué dans {operation}: {identifiant}"
            )

    _valider_conflits_operations(chemin.name, ids_par_operation, erreurs)


def _valider_messages(
    chemin: Path,
    erreurs: list[str],
    avertissements: list[str],
) -> None:
    if not chemin.exists():
        return

    donnees = _charger_yaml(chemin, erreurs)
    if donnees is None:
        return

    if _contient_marqueur(donnees):
        erreurs.append("messages.yaml contient un marqueur A_REMPLACER_*")

    for section in donnees.keys():
        if section != "messages":
            avertissements.append(f"messages.yaml contient une section inconnue: {section}")

    messages = donnees.get("messages", {})
    if not isinstance(messages, dict):
        erreurs.append("Le bloc messages de messages.yaml doit être un objet YAML")
        return

    for cle in messages.keys():
        if str(cle).strip() == "":
            erreurs.append("messages.yaml contient une clé de message vide")


def _charger_yaml(chemin: Path, erreurs: list[str]) -> Optional[dict[str, Any]]:
    try:
        with chemin.open(encoding="utf-8") as fichier:
            donnees = yaml.safe_load(fichier) or {}
    except (OSError, yaml.YAMLError) as exc:
        erreurs.append(f"{chemin.name} invalide: {exc}")
        return None

    if not isinstance(donnees, dict):
        erreurs.append(f"{chemin.name} doit contenir un objet YAML")
        return None
    return donnees


def _ids_de_collection(
    valeur: Any,
    fichier: str,
    operation: str,
    erreurs: list[str],
) -> tuple[str, ...]:
    if valeur is None:
        return ()
    if not isinstance(valeur, list):
        erreurs.append(f"{fichier}: {operation} doit contenir une liste")
        return ()

    ids: list[str] = []
    for element in valeur:
        if isinstance(element, dict):
            identifiant = element.get("id")
        else:
            identifiant = element
        if identifiant is None or str(identifiant).strip() == "":
            erreurs.append(f"{fichier}: {operation} contient un élément sans id")
            continue
        ids.append(str(identifiant))
    return tuple(ids)


def _valider_conflits_operations(
    fichier: str,
    ids_par_operation: dict[str, tuple[str, ...]],
    erreurs: list[str],
) -> None:
    operations = list(ids_par_operation.keys())
    for index, operation in enumerate(operations):
        ids = set(ids_par_operation[operation])
        for autre_operation in operations[index + 1 :]:
            conflit = ids.intersection(ids_par_operation[autre_operation])
            for identifiant in sorted(conflit):
                erreurs.append(
                    f"{fichier}: id présent dans {operation} et {autre_operation}: {identifiant}"
                )


def _contient_marqueur(valeur: Any) -> bool:
    if isinstance(valeur, dict):
        return any(
            _contient_marqueur(cle) or _contient_marqueur(sous_valeur)
            for cle, sous_valeur in valeur.items()
        )
    if isinstance(valeur, list):
        return any(_contient_marqueur(element) for element in valeur)
    if isinstance(valeur, str):
        return MARQUEUR_A_REMPLACER in valeur
    return False


def _doublons(valeurs: Iterable[str]) -> list[str]:
    vus: set[str] = set()
    doublons: list[str] = []
    for valeur in valeurs:
        if valeur in vus and valeur not in doublons:
            doublons.append(valeur)
        vus.add(valeur)
    return doublons


def _liste(valeurs: Iterable[str], vide: str | None = None) -> list[str]:
    elements = list(valeurs)
    if not elements and vide is not None:
        return [f"- {vide}"]
    return [f"- {valeur}" for valeur in elements]


if __name__ == "__main__":
    raise SystemExit(main())
