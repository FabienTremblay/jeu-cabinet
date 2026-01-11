#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# scripts/menage-scripts.sh
#
# Objectif:
#   - Inventorier les "scripts" (shell + scripts python utilitaires) du dépôt
#   - Déterminer s'ils sont référencés par des fichiers "d'orchestration" (Makefile,
#     docker-compose.yml, docs/*.md, README, etc.)
#   - Détecter les doublons (même sha256)
#   - Optionnel: archiver (déplacer) les scripts non référencés dans archives/
#
# Philosophie sécurité:
#   - Par défaut: DRY-RUN, aucune modification
#   - Pour déplacer: exiger --archive-unreferenced --apply
# ==============================================================================

# ---------- Config (ajuste au besoin) ----------
EXCLUSIONS_DIRS=(
  "./archives"
  "./.pytest_cache"
  "./.venv"
  "./venv"
  "./node_modules"
  "./rules-service/target"
  "./**/__pycache__"
)

# "scripts" à considérer:
# - *.sh / *.bash / *.zsh (partout sauf exclusions)
# - scripts/*.py (utilitaires)
# - services/**/client-*.py (scripts client)
# - sql/*.sh (init db)
INCLUDE_FIND_EXPR=(
  "(" -name "*.sh" -o -name "*.bash" -o -name "*.zsh" ")"
  -o "(" -path "./scripts/*.py" ")"
  -o "(" -path "./services/**/client-*.py" ")"
  -o "(" -path "./sql/*.sh" ")"
)

# Fichiers dans lesquels on cherche des références (ajuste si tu veux)
REFERENCE_GLOBS=(
  "./Makefile"
  "./docker-compose.yml"
  "./README.md"
  "./docs/**/*.md"
  "./contrats/**/*.md"
  "./scripts/*.sh"
  "./scripts/*.py"
  "./services/**/Makefile"
  "./*.sh"
)

# ---------- Options ----------
MODE_DRY_RUN=1
DO_ARCHIVE=0
APPLY=0
LIST_ONLY=0
RAPPORT_PATH=""

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/menage-scripts.sh [options]

Options:
  --report <fichier.tsv>       Chemin du rapport TSV (défaut: reports/menage_scripts_YYYYMMDD_HHMM.tsv)
  --list-unreferenced          Affiche seulement la liste des scripts non référencés (selon heuristique)
  --archive-unreferenced       Prépare l'archivage des scripts non référencés vers archives/menage_scripts_YYYYMMDD/
  --apply                      Applique l'archivage (sinon dry-run)
  --help                       Aide

Exemples:
  ./scripts/menage-scripts.sh
  ./scripts/menage-scripts.sh --list-unreferenced
  ./scripts/menage-scripts.sh --archive-unreferenced --apply
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --report) RAPPORT_PATH="${2:-}"; shift 2;;
    --list-unreferenced) LIST_ONLY=1; shift;;
    --archive-unreferenced) DO_ARCHIVE=1; shift;;
    --apply) APPLY=1; MODE_DRY_RUN=0; shift;;
    --help|-h) usage; exit 0;;
    *)
      echo "Option inconnue: $1" >&2
      usage
      exit 2
      ;;
  esac
done

# ---------- Déterminer la racine du repo ----------
if command -v git >/dev/null 2>&1 && git rev-parse --show-toplevel >/dev/null 2>&1; then
  RACINE="$(git rev-parse --show-toplevel)"
else
  # fallback: racine = parent du dossier où se trouve ce script
  RACINE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi
cd "$RACINE"

mkdir -p reports

timestamp="$(date +"%Y%m%d_%H%M")"
if [[ -z "$RAPPORT_PATH" ]]; then
  RAPPORT_PATH="reports/menage_scripts_${timestamp}.tsv"
fi

# ---------- Outils requis ----------
if ! command -v sha256sum >/dev/null 2>&1; then
  echo "Erreur: sha256sum est requis." >&2
  exit 1
fi
if ! command -v wc >/dev/null 2>&1; then
  echo "Erreur: wc est requis." >&2
  exit 1
fi

# ---------- Construire la liste des fichiers de référence ----------
# On expand les globs via bash (globstar)
shopt -s globstar nullglob

REF_FILES=()
for g in "${REFERENCE_GLOBS[@]}"; do
  for f in $g; do
    [[ -f "$f" ]] && REF_FILES+=("$f")
  done
done

# Dédupliquer
declare -A vu_ref=()
REF_FILES_UNIQ=()
for f in "${REF_FILES[@]}"; do
  if [[ -z "${vu_ref[$f]+x}" ]]; then
    vu_ref["$f"]=1
    REF_FILES_UNIQ+=("$f")
  fi
done

# ---------- Construire find avec exclusions ----------
# On exclut explicitement certains dossiers
# (Note: find sans globstar; exclusions simples)
FIND_EXCLUDE=()
for d in "${EXCLUSIONS_DIRS[@]}"; do
  # On ne peut pas passer "**" proprement à find; on gère surtout archives et dossiers majeurs.
  case "$d" in
    "./archives") FIND_EXCLUDE+=( -path "./archives/*" -o -path "./archives" );;
    "./.pytest_cache") FIND_EXCLUDE+=( -o -path "./.pytest_cache/*" -o -path "./.pytest_cache" );;
    "./.venv") FIND_EXCLUDE+=( -o -path "./.venv/*" -o -path "./.venv" );;
    "./venv") FIND_EXCLUDE+=( -o -path "./venv/*" -o -path "./venv" );;
    "./node_modules") FIND_EXCLUDE+=( -o -path "./node_modules/*" -o -path "./node_modules" );;
    "./rules-service/target") FIND_EXCLUDE+=( -o -path "./rules-service/target/*" -o -path "./rules-service/target" );;
    *) : ;;
  esac
done

# ---------- Trouver les scripts ----------
mapfile -t SCRIPTS < <(
  # shellcheck disable=SC2016
  find . -type f \
    \( "${INCLUDE_FIND_EXPR[@]}" \) \
    \( -false "${FIND_EXCLUDE[@]}" \) -prune -o -print \
  | sed 's|^\./||' \
  | sort
)

# Fix: la logique -prune ci-dessus est délicate; on filtre aussi en post-traitement
# pour éviter un find trop fragile.
SCRIPTS_FILTRÉS=()
for p in "${SCRIPTS[@]}"; do
  # Filtrage post: archives/
  if [[ "$p" == archives/* ]]; then
    continue
  fi
  SCRIPTS_FILTRÉS+=("$p")
done

# ---------- Fonctions utilitaires ----------
est_executable() {
  local f="$1"
  [[ -x "$f" ]] && echo "oui" || echo "non"
}

lire_shebang() {
  local f="$1"
  # retourne la première ligne si commence par #!
  local l
  l="$(head -n 1 "$f" 2>/dev/null || true)"
  if [[ "$l" == "#!"* ]]; then
    echo "$l"
  else
    echo ""
  fi
}

type_script() {
  local f="$1"
  case "$f" in
    *.sh|*.bash|*.zsh) echo "shell";;
    *.py) echo "python";;
    Makefile) echo "makefile";;
    *) echo "autre";;
  esac
}

compter_refs() {
  local chemin="$1"
  local base
  base="$(basename "$chemin")"

  local hits=0
  local h

  # On cherche à la fois le chemin relatif et le basename.
  # On limite aux fichiers "REF_FILES_UNIQ" (pas tout le repo) pour éviter bruit (ex. stats_fichiers.tsv).
  for rf in "${REF_FILES_UNIQ[@]}"; do
    # skip si c'est le script lui-même
    [[ "$rf" == "$chemin" ]] && continue

    # match chemin
    if grep -F -n -- "$chemin" "$rf" >/dev/null 2>&1; then
      h="$(grep -F -n -- "$chemin" "$rf" | wc -l | tr -d ' ')"
      hits=$((hits + h))
      continue
    fi

    # match basename (heuristique)
    if grep -F -n -- "$base" "$rf" >/dev/null 2>&1; then
      h="$(grep -F -n -- "$base" "$rf" | wc -l | tr -d ' ')"
      hits=$((hits + h))
      continue
    fi
  done

  echo "$hits"
}

# ---------- Construire le rapport ----------
# Colonnes:
# path, type, executable, shebang, size_bytes, lines, sha256, ref_hits, referenced, duplicate_of
echo -e "path\ttype\texecutable\tshebang\tsize_bytes\tlines\tsha256\tref_hits\treferenced\tduplicate_of" > "$RAPPORT_PATH"

declare -A sha2first=()
declare -A sha2paths=()

for f in "${SCRIPTS_FILTRÉS[@]}"; do
  [[ -f "$f" ]] || continue

  typ="$(type_script "$f")"
  exec_flag="$(est_executable "$f")"
  shebang="$(lire_shebang "$f")"
  size_bytes="$(wc -c < "$f" | tr -d ' ')"
  lines="$(wc -l < "$f" | tr -d ' ')"
  sha="$(sha256sum "$f" | awk '{print $1}')"
  ref_hits="$(compter_refs "$f")"
  if [[ "$ref_hits" -gt 0 ]]; then
    referenced="oui"
  else
    referenced="non"
  fi

  # Doublons
  if [[ -z "${sha2first[$sha]+x}" ]]; then
    sha2first["$sha"]="$f"
  fi
  sha2paths["$sha"]+="$f|"

  dup_of=""
  if [[ "${sha2first[$sha]}" != "$f" ]]; then
    dup_of="${sha2first[$sha]}"
  fi

  # Nettoyage shebang (éviter tabs)
  shebang="${shebang//$'\t'/ }"

  echo -e "${f}\t${typ}\t${exec_flag}\t${shebang}\t${size_bytes}\t${lines}\t${sha}\t${ref_hits}\t${referenced}\t${dup_of}" >> "$RAPPORT_PATH"
done

# ---------- Résumé ----------
total="${#SCRIPTS_FILTRÉS[@]}"
non_ref_count="$(awk -F'\t' 'NR>1 && $9=="non"{c++} END{print c+0}' "$RAPPORT_PATH")"
dup_count="$(awk -F'\t' 'NR>1 && $10!=""{c++} END{print c+0}' "$RAPPORT_PATH")"

echo ""
echo "== Rapport généré =="
echo "  Fichier : $RAPPORT_PATH"
echo "  Scripts : $total"
echo "  Non référencés (heuristique) : $non_ref_count"
echo "  Doublons (contenu identique) : $dup_count"
echo ""

if [[ "$LIST_ONLY" -eq 1 ]]; then
  echo "== Scripts non référencés (heuristique) =="
  awk -F'\t' 'NR>1 && $9=="non"{print $1}' "$RAPPORT_PATH"
  exit 0
fi

# ---------- Archivage (optionnel) ----------
if [[ "$DO_ARCHIVE" -eq 1 ]]; then
  archive_dir="archives/menage_scripts_${timestamp}"
  echo "== Archivage des scripts non référencés =="
  echo "  Destination: $archive_dir"
  if [[ "$MODE_DRY_RUN" -eq 1 ]]; then
    echo "  Mode: DRY-RUN (ajoute --apply pour déplacer réellement)"
  else
    echo "  Mode: APPLY"
  fi

  mapfile -t A_DEPLACER < <(awk -F'\t' 'NR>1 && $9=="non"{print $1}' "$RAPPORT_PATH")

  if [[ "${#A_DEPLACER[@]}" -eq 0 ]]; then
    echo "  Rien à archiver."
    exit 0
  fi

  echo ""
  echo "  Candidats (${#A_DEPLACER[@]}):"
  printf '   - %s\n' "${A_DEPLACER[@]}"
  echo ""

  if [[ "$MODE_DRY_RUN" -eq 1 ]]; then
    echo "DRY-RUN: aucune modification effectuée."
    exit 0
  fi

  mkdir -p "$archive_dir"

  # git mv si possible
  use_git=0
  if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    use_git=1
  fi

  for f in "${A_DEPLACER[@]}"; do
    dest="$archive_dir/$f"
    mkdir -p "$(dirname "$dest")"
    if [[ "$use_git" -eq 1 ]]; then
      # si suivi par git, git mv; sinon mv
      if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
        git mv "$f" "$dest"
      else
        mv "$f" "$dest"
      fi
    else
      mv "$f" "$dest"
    fi
    echo "Déplacé: $f -> $dest"
  done

  echo ""
  echo "Archivage terminé."
  echo "Astuce: vérifie, puis commit si nécessaire."
fi
