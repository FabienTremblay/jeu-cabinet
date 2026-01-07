#!/usr/bin/env bash
set -euo pipefail

REG_PORT="${REGISTRY_HTTP_PORT:-8080}"
URL="http://localhost:${REG_PORT}/apis/registry/v2"

code=$(curl -s -o /dev/null -w "%{http_code}" "$URL")
if [ "$code" = "200" ]; then
  echo "✅ Apicurio Registry OK (200) — $URL"
  exit 0
else
  echo "❌ Apicurio Registry renvoie HTTP $code — $URL"
  exit 1
fi
