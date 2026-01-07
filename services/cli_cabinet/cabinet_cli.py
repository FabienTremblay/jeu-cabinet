# services/cli_cabinet/cabinet_cli.py

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from .clients import LobbyClient
from .settings import settings


client = LobbyClient()


# ----------------------------------------------------------------------
# commandes existantes
# ----------------------------------------------------------------------
def cmd_health(args: argparse.Namespace) -> None:
    try:
        data = client.health()
        print(f"Lobby OK @ {settings.lobby_base_url} -> {data}")
    except Exception as exc:  # noqa: BLE001
        print(f"Erreur de communication avec le lobby: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_inscrire(args: argparse.Namespace) -> None:
    try:
        result = client.inscrire_joueur(
            pseudo=args.pseudo,
            email=args.email,
            nom=args.nom,
            mot_de_passe=args.mot_de_passe,
            alias=args.alias,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Échec de l'inscription: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Inscription réussie:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_auth(args: argparse.Namespace) -> None:
    try:
        result = client.authentifier_joueur(
            courriel=args.email,
            mot_de_passe=args.mot_de_passe,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Échec de l'authentification: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Authentification réussie:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


# ----------------------------------------------------------------------
# nouvelles commandes : ACC.111 / ACC.115
# ----------------------------------------------------------------------
def cmd_tables(args: argparse.Namespace) -> None:
    """Lister les tables du lobby."""
    try:
        result = client.lister_tables(statut=args.statut)
    except Exception as exc:  # noqa: BLE001
        print(f"Échec de la liste des tables: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_creer_table(args: argparse.Namespace) -> None:
    """Créer une table et asseoir l'hôte."""
    try:
        result = client.creer_table(
            id_hote=args.id_hote,
            nom_table=args.nom,
            nb_sieges=args.nb_sieges,
            mot_de_passe_table=args.mot_de_passe_table,
            skin_jeu=args.skin_jeu,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Échec de la création de la table: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Table créée:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_joindre_table(args: argparse.Namespace) -> None:
    """Rejoindre une table existante (prendre un siège comme invité)."""
    try:
        result = client.joindre_table(
            id_table=args.id_table,
            id_joueur=args.id_joueur,
            mot_de_passe_table=args.mot_de_passe_table,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Échec de la prise de siège: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Prise de siège réussie:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_joueur_pret(args: argparse.Namespace) -> None:
    """Marquer un joueur comme prêt à une table."""
    try:
        result = client.joueur_pret(
            id_table=args.id_table,
            id_joueur=args.id_joueur,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Échec pour marquer le joueur prêt: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Joueur marqué prêt:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_lancer_partie(args: argparse.Namespace) -> None:
    """ACC.115 – Lancer la partie pour une table (par l'hôte)."""
    try:
        result = client.lancer_partie(
            id_table=args.id_table,
            id_hote=args.id_hote,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Échec du lancement de la partie: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Partie lancée:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


# ----------------------------------------------------------------------
# parser
# ----------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cabinet-cli",
        description="CLI Cabinet – Gestion du lobby (ACC.011 / ACC.021 / ACC.111 / ACC.115)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # health
    p_health = subparsers.add_subparser(
        "health",
        help="Tester la santé du service Lobby",
    ) if hasattr(subparsers, "add_subparser") else subparsers.add_parser(
        "health",
        help="Tester la santé du service Lobby",
    )
    p_health.set_defaults(func=cmd_health)

    # inscrire (ACC.011)
    p_inscrire = subparsers.add_parser(
        "inscrire",
        help="ACC.011 – Inscrire un utilisateur inconnu au lobby",
    )
    p_inscrire.add_argument("pseudo", help="Pseudo / identifiant joueur (utilisé comme alias par défaut)")
    p_inscrire.add_argument("--email", "-e", required=True, help="Courriel du joueur (courriel)")
    p_inscrire.add_argument("--nom", "-n", required=True, help="Nom complet du joueur (nom)")
    p_inscrire.add_argument(
        "--mot-de-passe",
        "-p",
        required=True,
        help="Mot de passe du joueur (mot_de_passe)",
    )
    p_inscrire.add_argument(
        "--alias",
        "-a",
        required=False,
        help="Alias affiché (par défaut = pseudo)",
    )
    p_inscrire.set_defaults(func=cmd_inscrire)

    # auth (ACC.021)
    p_auth = subparsers.add_parser(
        "auth",
        help="ACC.021 – Authentifier un utilisateur déjà inscrit",
    )
    p_auth.add_argument("email", help="Courriel du joueur (courriel)")
    p_auth.add_argument(
        "--mot-de-passe",
        "-p",
        required=True,
        help="Mot de passe du joueur (mot_de_passe)",
    )
    p_auth.set_defaults(func=cmd_auth)

    # tables : lister
    p_tables = subparsers.add_parser(
        "tables",
        help="ACC.111 – Lister les tables du lobby",
    )
    p_tables.add_argument(
        "--statut",
        choices=["ouverte", "en_preparation", "en_cours", "terminee"],
        help="Filtrer par statut de table",
    )
    p_tables.set_defaults(func=cmd_tables)

    # creer-table
    p_creer = subparsers.add_parser(
        "creer-table",
        help="ACC.111 – Créer une table et y asseoir l'hôte",
    )
    p_creer.add_argument("id_hote", help="Identifiant du joueur hôte (id_joueur)")
    p_creer.add_argument(
        "--nom",
        "-n",
        required=True,
        help="Nom de la table",
    )
    p_creer.add_argument(
        "--nb-sieges",
        "-s",
        type=int,
        default=4,
        help="Nombre de sièges (par défaut 4)",
    )
    p_creer.add_argument(
        "--mot-de-passe-table",
        "-p",
        help="Mot de passe de la table (facultatif)",
    )
    p_creer.add_argument(
        "--skin-jeu",
        "-k",
        help="Variante / skin de jeu (facultatif)",
    )
    p_creer.set_defaults(func=cmd_creer_table)

    # joindre-table
    p_join = subparsers.add_parser(
        "joindre-table",
        help="ACC.111 – Rejoindre une table existante",
    )
    p_join.add_argument("id_table", help="Identifiant de la table")
    p_join.add_argument("id_joueur", help="Identifiant du joueur (id_joueur)")
    p_join.add_argument(
        "--mot-de-passe-table",
        "-p",
        help="Mot de passe de la table si nécessaire",
    )
    p_join.set_defaults(func=cmd_joindre_table)

    # joueur-pret
    p_ready = subparsers.add_parser(
        "joueur-pret",
        help="ACC.111 – Indiquer qu'un joueur est prêt à la table",
    )
    p_ready.add_argument("id_table", help="Identifiant de la table")
    p_ready.add_argument("id_joueur", help="Identifiant du joueur (id_joueur)")
    p_ready.set_defaults(func=cmd_joueur_pret)

    # lancer-partie (ACC.115)
    p_launch = subparsers.add_parser(
        "lancer-partie",
        help="ACC.115 – Lancer la partie pour une table (par l'hôte)",
    )
    p_launch.add_argument("id_table", help="Identifiant de la table")
    p_launch.add_argument("id_hote", help="Identifiant du joueur hôte (id_joueur)")
    p_launch.set_defaults(func=cmd_lancer_partie)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()

