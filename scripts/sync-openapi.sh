#!/usr/bin/env bash
set -euo pipefail

mkdir -p contrats/openapi \
         contrats/jsonschema/_common/http \
         contrats/jsonschema/http/lobby \
         contrats/jsonschema/http/api_moteur \
         contrats/jsonschema/http/ui_etat_joueur

echo "== snapshot openapi =="
curl -fsS http://lobby.cabinet.localhost/openapi.json    -o contrats/openapi/lobby.openapi.json
curl -fsS http://api.cabinet.localhost/openapi.json      -o contrats/openapi/api_moteur.openapi.json
curl -fsS http://ui-etat.cabinet.localhost/openapi.json  -o contrats/openapi/ui_etat_joueur.openapi.json

echo "== extract jsonschema =="
python3 scripts/extract-openapi-schemas.py contrats/openapi/lobby.openapi.json lobby
python3 scripts/extract-openapi-schemas.py contrats/openapi/api_moteur.openapi.json api_moteur
python3 scripts/extract-openapi-schemas.py contrats/openapi/ui_etat_joueur.openapi.json ui_etat_joueur

echo "OK"
