#!/usr/bin/env bash
set -euo pipefail

BOOTSTRAP=${BOOTSTRAP:-"kafka:9092"}

echo "[bootstrap-topics] Bootstrapping Kafka topics on ${BOOTSTRAP}"

# Fonction helper pour créer un topic seulement s'il n'existe pas
create_topic() {
  local topic=$1

  if /usr/bin/kafka-topics --bootstrap-server "${BOOTSTRAP}" --list | grep -q "^${topic}$"; then
    echo "[bootstrap-topics] Topic '${topic}' existe déjà ✔"
  else
    echo "[bootstrap-topics] Création du topic '${topic}'…"
    /usr/bin/kafka-topics \
      --bootstrap-server "${BOOTSTRAP}" \
      --create \
      --topic "${topic}" \
      --partitions 3 \
      --replication-factor 1
    echo "[bootstrap-topics] Topic '${topic}' créé ✔"
  fi
}

create_topic "cab.commands"
create_topic "cab.events"

# topics utilisés par lobby pour ses événements de domaine
create_topic "cabinet.joueurs.evenements"
create_topic "cabinet.tables.evenements"
create_topic "cabinet.parties.evenements"

echo "[bootstrap-topics] Terminé ✔"
