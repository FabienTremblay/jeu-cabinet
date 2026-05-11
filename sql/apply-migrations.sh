#!/usr/bin/env bash
# sql/apply-migrations.sh
# Applique les migrations SQL idempotentes sur une base existante.
set -euo pipefail

: "${JEU_DB:?variable manquante (ex: jeu)}"
: "${JEU_DB_USER:?variable manquante (ex: jeu)}"

MIGRATIONS_DIR="${MIGRATIONS_DIR:-/opt/sql/migrations}"

psql -v ON_ERROR_STOP=1 -U "${JEU_DB_USER}" -d "${JEU_DB}" <<'SQL'
create table if not exists schema_migrations (
  version text primary key,
  nom text not null,
  applique_le timestamptz not null default now()
);
SQL

shopt -s nullglob
migrations=("${MIGRATIONS_DIR}"/*.sql)

if (( ${#migrations[@]} == 0 )); then
  echo "Aucune migration SQL trouvee dans ${MIGRATIONS_DIR}."
  exit 0
fi

for migration in "${migrations[@]}"; do
  fichier="$(basename "${migration}")"
  version="${fichier%%_*}"

  if [[ -z "${version}" || "${version}" == "${fichier}" ]]; then
    echo "Migration ignoree, nom invalide: ${fichier}" >&2
    exit 1
  fi

  deja_appliquee="$(
    psql -v ON_ERROR_STOP=1 -U "${JEU_DB_USER}" -d "${JEU_DB}" \
      -v version="${version}" \
      -tA <<'SQL'
select exists (select 1 from schema_migrations where version = :'version');
SQL
  )"

  if [[ "${deja_appliquee}" == "t" ]]; then
    echo "Migration deja appliquee: ${fichier}"
    continue
  fi

  echo "Application migration: ${fichier}"
  psql -v ON_ERROR_STOP=1 -U "${JEU_DB_USER}" -d "${JEU_DB}" -f "${migration}"
  psql -v ON_ERROR_STOP=1 -U "${JEU_DB_USER}" -d "${JEU_DB}" \
    -v version="${version}" \
    -v nom="${fichier}" <<'SQL'
insert into schema_migrations(version, nom)
values (:'version', :'nom')
on conflict (version) do nothing;
SQL
done
