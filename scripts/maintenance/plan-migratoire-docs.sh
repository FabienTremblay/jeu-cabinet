#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-apply}" # apply | dry-run
RACINE="$(pwd)"

run() {
  if [[ "$MODE" == "dry-run" ]]; then
    echo "+ $*"
  else
    echo "+ $*"
    eval "$@"
  fi
}

info() { echo "== $* =="; }

if [[ ! -f "$RACINE/README.md" ]]; then
  echo "ERREUR: exécute ce script à la racine du dépôt (README.md manquant)." >&2
  exit 2
fi

info "Création structure archives/"
run "mkdir -p archives archives/documentation-historique archives/documentation-services archives/notes archives/images archives/odt archives/tech"

if [[ ! -f "archives/README.md" ]]; then
  run "cat > archives/README.md <<'EOF'
# archives

Ce répertoire contient des artefacts historiques et des documents de travail
qui ne doivent plus être considérés comme documentation officielle.

Règle :
- documentation officielle : dossier \`docs/\` (et \`contrats/\` pour les contrats).
- tout document non référencé depuis \`README.md\` ou \`docs/README.md\` est présumé historique.
EOF"
fi

info "Canonicalisation des noms dans docs/"
run "mkdir -p docs docs/ui docs/infra docs/archi"

if [[ -f "docs/docs_architecture.md" && ! -f "docs/architecture.md" ]]; then
  run "git mv docs/docs_architecture.md docs/architecture.md 2>/dev/null || mv docs/docs_architecture.md docs/architecture.md"
fi

if [[ -f "docs/docs_execution_locale.md" && ! -f "docs/execution-locale.md" ]]; then
  run "git mv docs/docs_execution_locale.md docs/execution-locale.md 2>/dev/null || mv docs/docs_execution_locale.md docs/execution-locale.md"
fi

info "Déplacement documentation legacy vers archives/"

if [[ -f "docker/Architecture organique.odt" ]]; then
  run "git mv 'docker/Architecture organique.odt' 'archives/odt/Architecture organique.odt' 2>/dev/null || mv 'docker/Architecture organique.odt' 'archives/odt/Architecture organique.odt'"
fi

if [[ -d "rules-service/src/main/resources/rules/debut_mandat/v1/documents" ]]; then
  run "mkdir -p 'archives/odt/rules-service/debut_mandat/v1'"
  run "git mv 'rules-service/src/main/resources/rules/debut_mandat/v1/documents' 'archives/odt/rules-service/debut_mandat/v1/documents' 2>/dev/null || mv 'rules-service/src/main/resources/rules/debut_mandat/v1/documents' 'archives/odt/rules-service/debut_mandat/v1/documents'"
fi

if [[ -f "services/cabinet/skins/Mandat_difficile/documentation.odt" ]]; then
  run "mkdir -p 'archives/odt/skins/Mandat_difficile'"
  run "git mv 'services/cabinet/skins/Mandat_difficile/documentation.odt' 'archives/odt/skins/Mandat_difficile/documentation.odt' 2>/dev/null || mv 'services/cabinet/skins/Mandat_difficile/documentation.odt' 'archives/odt/skins/Mandat_difficile/documentation.odt'"
fi

if [[ -d "services/ui-web/docs" ]]; then
  run "mkdir -p 'docs/ui/_from-services-ui-web'"
  run "cp -a 'services/ui-web/docs/.' 'docs/ui/_from-services-ui-web/'"
  if [[ ! -f "services/ui-web/docs/README.md" ]]; then
    run "cat > 'services/ui-web/docs/README.md' <<'EOF'
# Documentation UI (déplacée)

La documentation UI a été centralisée dans \`docs/ui/\`.

Voir :
- \`docs/ui/_from-services-ui-web/\` (copie des fichiers historiques)
- \`docs/\` pour la documentation officielle
EOF"
  fi
fi

if [[ -f "services/ui-web/conversation.txt" ]]; then
  run "git mv 'services/ui-web/conversation.txt' 'archives/notes/ui-web-conversation.txt' 2>/dev/null || mv 'services/ui-web/conversation.txt' 'archives/notes/ui-web-conversation.txt'"
fi

info "Déplacement fichiers de sauvegarde/backup (ex: *~)"
if [[ -d "services/ui-web/src" ]]; then
  fichiers_backup=()
  while IFS= read -r -d '' f; do
    fichiers_backup+=("$f")
  done < <(find services/ui-web/src -name '*~' -type f -print0 2>/dev/null || true)

  if (( ${#fichiers_backup[@]} > 0 )); then
    run "mkdir -p archives/tech/editor-backups"

    if [[ "$MODE" == "dry-run" ]]; then
      for f in "${fichiers_backup[@]}"; do
        echo "+ mv \"$f\" archives/tech/editor-backups/ (avec sous-dossier miroir)"
      done
    else
      for f in "${fichiers_backup[@]}"; do
        rel_dir="$(dirname "$f" | sed 's|^services/ui-web/src/||')"
        dest="archives/tech/editor-backups/${rel_dir}"
        mkdir -p "$dest"
        mv "$f" "$dest/"
      done
    fi
  fi
fi

info "Mise à jour docs/README.md (index documentaire)"
if [[ ! -f "docs/README.md" ]]; then
  run "cat > docs/README.md <<'EOF'
# documentation

## index

- architecture : \`docs/architecture.md\`
- exécution locale : \`docs/execution-locale.md\`
- contrats : \`contrats/README.md\`
- UI (historique) : \`docs/ui/_from-services-ui-web/\`
EOF"
fi

info "Vérification .gitignore (rappel backups)"
if [[ -f ".gitignore" ]]; then
  if ! grep -q '^\*~$' .gitignore; then
    run "echo '*~' >> .gitignore"
  fi
fi

info "Terminé (mode=$MODE)"
