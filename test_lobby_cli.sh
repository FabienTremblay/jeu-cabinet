#!/usr/bin/env bash
set -euo pipefail

# Point d'entrée du CLI
CLI="python -m services.cli_cabinet.cabinet_cli"

# Petite fonction utilitaire pour extraire un ID joueur ou table depuis une sortie texte
# - cherche un pattern J-xxxx ou T-xxxx en hexadécimal
extract_id() {
  grep -oE '[JT]-[0-9a-f]+' | head -n1
}

echo "=== 1) Inscription joueur 1 ==="
$CLI inscrire joueur1 \
  --email joueur1@example.com \
  --nom "Joueur Un" \
  --mot-de-passe "secret1" \
  --alias "Alias1"

echo "=== 2) Auth joueur 1 → récupération id_joueur_1 ==="
auth_j1_output="$(
  $CLI auth joueur1@example.com \
    --mot-de-passe "secret1"
)"
echo "$auth_j1_output"
id_joueur_1="$(echo "$auth_j1_output" | extract_id)"
echo "id_joueur_1 = $id_joueur_1"

echo "=== 3) Création de la table avec joueur 1 comme hôte ==="
creer_table_output="$(
  $CLI creer-table "$id_joueur_1" \
    --nom "Table test multi" \
    --nb-sieges 2 \
    --skin "minimal"
)"
echo "$creer_table_output"
id_table="$(echo "$creer_table_output" | grep -oE 'T-[0-9a-f]+' | head -n1)"
echo "id_table = $id_table"

echo "=== 4) Inscription + auth joueur 2 ==="
$CLI inscrire joueur2 \
  --email joueur2@example.com \
  --nom "Joueur Deux" \
  --mot-de-passe "secret2" \
  --alias "Alias2"

auth_j2_output="$(
  $CLI auth joueur2@example.com \
    --mot-de-passe "secret2"
)"
echo "$auth_j2_output"
id_joueur_2="$(echo "$auth_j2_output" | extract_id)"
echo "id_joueur_2 = $id_joueur_2"

echo "=== 5) Joueur 2 rejoint la table ==="
$CLI joindre-table "$id_table" "$id_joueur_2"

echo "=== 6) Marquer les deux joueurs prêts ==="
$CLI joueur-pret "$id_table" "$id_joueur_1"
$CLI joueur-pret "$id_table" "$id_joueur_2"

echo "=== 7) Lancer la partie (par l'hôte) ==="
$CLI lancer-partie "$id_table" "$id_joueur_1"

echo "=== Scénario terminé avec succès ==="
