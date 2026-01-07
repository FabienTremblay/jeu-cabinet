#!/usr/bin/env bash
# sql/00-config-postgres.sh
# Initialise la base applicative (aligné avec .env : JEU_DB / JEU_DB_USER / JEU_DB_PASSWORD)
# - idempotent (re-démarrages OK)
# - exécute le schéma en tant que JEU_DB_USER pour que les tables lui appartiennent
set -euo pipefail

: "${JEU_DB:?variable manquante (ex: jeu)}"
: "${JEU_DB_USER:?variable manquante (ex: jeu)}"
: "${JEU_DB_PASSWORD:?variable manquante}"

psql -v ON_ERROR_STOP=1 \
  -U "${POSTGRES_USER}" \
  -d postgres \
  -v dbname="${JEU_DB}" \
  -v dbuser="${JEU_DB_USER}" \
  -v dbpass="${JEU_DB_PASSWORD}" <<SQL

-- 1) créer le rôle si absent
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'dbuser', :'dbpass')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'dbuser')\gexec

-- 2) (optionnel) aligner le mot de passe si le rôle existe déjà
SELECT format('ALTER ROLE %I WITH LOGIN PASSWORD %L', :'dbuser', :'dbpass')
WHERE EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'dbuser')\gexec
 
 -- 3) créer la base si absente
 SELECT format('CREATE DATABASE %I OWNER %I', :'dbname', :'dbuser')
 WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :'dbname')\gexec
 
 -- 4) s'assurer que l'owner est correct si la base existait déjà
 SELECT format('ALTER DATABASE %I OWNER TO %I', :'dbname', :'dbuser')\gexec
 
SQL

# Exécuter le schéma en tant que l'utilisateur applicatif pour que l'owner des tables soit JEU_DB_USER.
SCHEMA_FILE="/opt/sql/01-init-jeu.sql"
if [[ -f "${SCHEMA_FILE}" ]]; then
  psql -v ON_ERROR_STOP=1 -U "${JEU_DB_USER}" -d "${JEU_DB}" -f "${SCHEMA_FILE}"
else
  echo "WARN: fichier de schéma introuvable: ${SCHEMA_FILE}" >&2
fi
