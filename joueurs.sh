#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://lobby.cabinet.localhost}"   # ajuste si ton lobby est ailleurs

echo "== Inscription utilisateur 1 =="
curl -sS -X POST "$BASE_URL/api/joueurs" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Fabien",
    "alias": "fab",
    "courriel": "fabien.tremblay@levio.ca",
    "mot_de_passe": "Coco"
  }'

echo
echo "== Inscription utilisateur 2 =="
curl -sS -X POST "$BASE_URL/api/joueurs" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Christine",
    "alias": "Titi",
    "courriel": "bernardchristine@hotmail.com",
    "mot_de_passe": "Coco"
  }'

echo ""
