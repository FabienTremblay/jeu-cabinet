#!/usr/bin/env python3
"""
rôle: mettre à niveau le fichier .env historique de MaisonNeuve sans afficher les secrets.
usage: lancer depuis la racine du dépôt avec `python3 appliquer-env-maisonneuve-prod.py`.
contexte: utilisé lors de la stabilisation de la configuration Docker de production MaisonNeuve.
statut: actif
"""
from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
from pathlib import Path
import shutil

CHEMIN_ENV = Path(".env")

VALEURS_CIBLES = OrderedDict([
    ("COMPOSE_PROJECT_NAME", "le-cabinet"),
    ("STACK_ID", "maisonneuve-prod-main"),
    ("STACK_NETWORK", "cabinet_net"),
    ("TRAEFIK_DOMAIN", "cabinet.localhost"),
    ("TRAEFIK_HTTP_PORT", "80"),
    ("TRAEFIK_HTTPS_PORT", "443"),
    ("TRAEFIK_API_PORT", "8085"),
    ("PUBLIC_BASE_URL", "https://jeu-caucus.com"),
    ("PUBLIC_HOST", "jeu-caucus.com"),
    ("PUBLIC_HOSTS_RULE", "Host(`jeu-caucus.com`) || Host(`www.jeu-caucus.com`) || Host(`jeu-caucus.ca`) || Host(`www.jeu-caucus.ca`)"),
    ("CORS_ORIGINS", "https://jeu-caucus.com,https://www.jeu-caucus.com,https://jeu-caucus.ca,https://www.jeu-caucus.ca,http://localhost:5173,http://192.168.2.11:5173,http://192.168.2.28:5173"),
    ("POSTGRES_PORT", "5432"),
    ("KAFKA_PLAINTEXT_PORT", "9092"),
    ("KAFKA_CONTROLLER_PORT", "9093"),
    ("KAFKA_UI_PORT", "8082"),
    ("REGISTRY_HTTP_PORT", "8080"),
    ("RULES_HTTP_PORT", "8081"),
    ("LOBBY_HTTP_PORT", "8083"),
    ("KAFKA_BROKER_ID", "1"),
    ("KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR", "1"),
    ("KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR", "1"),
    ("KAFKA_TRANSACTION_STATE_LOG_MIN_ISR", "1"),
    ("KAFKA_AUTO_CREATE_TOPICS_ENABLE", "false"),
    ("REGISTRY_LOG_LEVEL", "INFO"),
    ("TRAEFIK_HOST_KAFKA_UI", "kafka.cabinet.localhost"),
    ("TRAEFIK_HOST_REGISTRY", "registry.cabinet.localhost"),
    ("TRAEFIK_HOST_RULES", "rules.cabinet.localhost"),
    ("TOPICS", "cab.commands,cab.events,cabinet.joueurs.evenements,cabinet.tables.evenements,cabinet.parties.evenements"),
    ("LOBBY_PERSISTENCE_BACKEND", "postgres"),
    ("LOBBY_ID_MODE", "uuid"),
    ("LOBBY_KAFKA_ACTIF", "true"),
    ("LOBBY_TIMEOUT_PARTIE_ACTIF", "true"),
    ("LOBBY_TIMEOUT_PARTIE_DELAI_INACTIVITE_SECONDES", "3600"),
    ("CAB_RULES_BRE_URL", "http://rules-service:8081"),
])

SECRETS_A_PRESERVER = {
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "JEU_DB",
    "JEU_DB_USER",
    "JEU_DB_PASSWORD",
    "KAFKA_CLUSTER_ID",
    "KAFKA_UI_USERNAME",
    "KAFKA_UI_PASSWORD",
}

VALEURS_PAR_DEFAUT_SI_ABSENTES = OrderedDict([
    ("POSTGRES_USER", "postgres"),
    ("POSTGRES_PASSWORD", "changeme"),
    ("POSTGRES_DB", "postgres"),
    ("JEU_DB", "jeu"),
    ("JEU_DB_USER", "jeu"),
    ("JEU_DB_PASSWORD", "changeme"),
    ("KAFKA_CLUSTER_ID", "CHANGE_ME_22_CHARS_ID"),
    ("KAFKA_UI_USERNAME", "admin"),
    ("KAFKA_UI_PASSWORD", "changeme"),
])


def nettoyer_valeur(valeur: str) -> str:
    """Retire les commentaires inline non cités utilisés dans l'ancien .env."""
    valeur = valeur.strip()
    if " #" in valeur:
        valeur = valeur.split(" #", 1)[0].rstrip()
    if valeur.startswith('"') and valeur.endswith('"') and len(valeur) >= 2:
        valeur = valeur[1:-1]
    return valeur


def lire_env(chemin: Path) -> OrderedDict[str, str]:
    donnees: OrderedDict[str, str] = OrderedDict()
    if not chemin.exists():
        return donnees
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        cle, valeur = ligne.split("=", 1)
        donnees[cle.strip()] = nettoyer_valeur(valeur)
    return donnees


def main() -> None:
    if not CHEMIN_ENV.exists():
        raise SystemExit("Erreur: .env introuvable dans le répertoire courant.")

    horodatage = datetime.now().strftime("%Y%m%d-%H%M%S")
    sauvegarde = CHEMIN_ENV.with_name(f".env.backup-{horodatage}")
    shutil.copy2(CHEMIN_ENV, sauvegarde)

    actuel = lire_env(CHEMIN_ENV)
    final: OrderedDict[str, str] = OrderedDict()

    for cle, valeur in VALEURS_CIBLES.items():
        final[cle] = valeur

    for cle, defaut in VALEURS_PAR_DEFAUT_SI_ABSENTES.items():
        final[cle] = actuel.get(cle, defaut)

    # Réordonner pour garder les secrets dans les sections attendues.
    ordre = [
        "COMPOSE_PROJECT_NAME", "STACK_ID", "STACK_NETWORK",
        "TRAEFIK_DOMAIN", "TRAEFIK_HTTP_PORT", "TRAEFIK_HTTPS_PORT", "TRAEFIK_API_PORT",
        "PUBLIC_BASE_URL", "PUBLIC_HOST", "PUBLIC_HOSTS_RULE", "CORS_ORIGINS",
        "POSTGRES_PORT", "KAFKA_PLAINTEXT_PORT", "KAFKA_CONTROLLER_PORT", "KAFKA_UI_PORT", "REGISTRY_HTTP_PORT", "RULES_HTTP_PORT", "LOBBY_HTTP_PORT",
        "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB", "JEU_DB", "JEU_DB_USER", "JEU_DB_PASSWORD",
        "KAFKA_BROKER_ID", "KAFKA_CLUSTER_ID", "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR", "KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR", "KAFKA_TRANSACTION_STATE_LOG_MIN_ISR", "KAFKA_AUTO_CREATE_TOPICS_ENABLE",
        "REGISTRY_LOG_LEVEL", "KAFKA_UI_USERNAME", "KAFKA_UI_PASSWORD",
        "TRAEFIK_HOST_KAFKA_UI", "TRAEFIK_HOST_REGISTRY", "TRAEFIK_HOST_RULES",
        "TOPICS",
        "LOBBY_PERSISTENCE_BACKEND", "LOBBY_ID_MODE", "LOBBY_KAFKA_ACTIF", "LOBBY_TIMEOUT_PARTIE_ACTIF", "LOBBY_TIMEOUT_PARTIE_DELAI_INACTIVITE_SECONDES",
        "CAB_RULES_BRE_URL",
    ]

    lignes = [
        "# .env MaisonNeuve — généré à partir du .env historique local",
        "# Les secrets existants ont été conservés localement.",
        "",
    ]
    for cle in ordre:
        lignes.append(f"{cle}={final[cle]}")

    CHEMIN_ENV.write_text("\n".join(lignes) + "\n", encoding="utf-8")

    print(f"Sauvegarde créée: {sauvegarde}")
    print(".env mis à niveau sans afficher les secrets.")
    print("À vérifier ensuite:")
    print("  docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env config >/tmp/compose-prod-valide.yml")


if __name__ == "__main__":
    main()
