#!/bin/bash

KAFKA_UI_URL="http://kafka:9092"   # adapte si nécessaire
CLUSTER="cabinet"

TOPICS=(
  "cab.commands"
  "cab.events"
  "cabinet.joueurs.evenements"
  "cabinet.parties.evenements"
  "cabinet.tables.evenements"
)

for TOPIC in "${TOPICS[@]}"; do
  echo "Purge du topic : $TOPIC"
  curl -X POST "$KAFKA_UI_URL/api/clusters/$CLUSTER/topics/$TOPIC/messages/delete"
  echo -e "\n---"
done
