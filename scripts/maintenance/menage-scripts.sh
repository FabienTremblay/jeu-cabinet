#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# scripts/menage-scripts.sh
#
# Inventorie les scripts (shell + quelques utilitaires python), détecte:
#   - scripts non référencés (heuristique: Makefile, docker-compose, docs, README…)
#   - doublons (sha256 identique)
# Peut archiver (déplacer) les non-référencés vers archives/...
#
# Par défaut: DRY-RUN (aucune modif).
# ==============================================================================

# ---------- Options ----------
DO_ARCHIVE=0
APPLY=0
LIST_ONLY=0
REPORT_PATH=""

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/menage-scripts.sh [options]

Options:
  --report <fichier.tsv>       Chemin du rapport TSV (défaut: reports/menage_scripts_YYYYMMDD_HHMM.tsv)
  --list-unreferenced          Affiche seulement la liste des scripts non référencés (heuristique)
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
    --report) REPORT_PATH="${2:-}"; shift 2;;
    --list-unreferenced) LIST_ONLY=1; shift;;
    --archive-unreferenced) DO_ARCHIVE=1; shift;;
    --apply) APPLY=1; shift;;
    --help|-h) usage; exit 0;;
    *) echo "Option inconnue: $1" >&2; usage; exit 2;;
  esac
done

# ---------- Racine repo ----------
if command -v git >/dev/null 2>&1 && git rev-parse --show-toplevel >/dev/null 2>&1; then
  ROOT="$(git rev-parse --show-toplevel)"
else
  ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi
cd "$ROOT"

mkdir -p reports

ts="$(date +"%Y%m%d_%H%M")"
if [[ -z "${REPORT_PATH}" ]]; then
  REPORT_PATH="reports/menage_scripts_${ts}.tsv"
fi

# ---------- Outils requis ----------
command -v sha256sum >/dev/null 2>&1 || { echo "Erreur: sha256sum requis" >&2; exit 1; }
command -v awk >/dev/null 2>&1 || { echo "Erreur: awk requis" >&2; exit 1; }
command -v grep >/dev/null 2>&1 || { echo "Erreur: grep requis" >&2; exit 1; }

# ---------- Fichiers où chercher des références ----------
shopt -s globstar nullglob

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

REF_FILES=()
declare -A seen_ref=()
for g in "${REFERENCE_GLOBS[@]}"; do
  for f in $g; do
    [[ -f "$f" ]] || continue
    # normalise ./xxx -> xxx
    f="${f#./}"
    if [[ -z "${seen_ref[$f]+x}" ]]; then
      seen_ref["$f"]=1
      REF_FILES+=("$f")
    fi
  done
done

# ---------- Trouver les scripts ----------
# Exclusions: archives, node_modules, venv, etc.
EXCLUDE_REGEX='^(archives/|node_modules/|\.venv/|venv/|\.pytest_cache/|rules-service/target/|.*__pycache__/).*'

mapfile -t ALL_FILES < <(find . -type f -print | sed 's|^\./||' | sort)

SCRIPTS=()
for p in "${ALL_FILES[@]}"; do
  [[ "$p" =~ $EXCLUDE_REGEX ]] && continue
  case "$p" in
    *.sh|*.bash|*.zsh) SCRIPTS+=("$p") ;;
    scripts/*.py) SCRIPTS+=("$p") ;;
    services/**/client-*.py) SCRIPTS+=("$p") ;;
    sql/*.sh) SCRIPTS+=("$p") ;;
    *) : ;;
  esac
done

is_executable() { [[ -x "$1" ]] && echo "oui" || echo "non"; }
shebang() {
  local l
  l="$(head -n 1 "$1" 2>/dev/null || true)"
  [[ "$l" == "#!"* ]] && echo "${l//$'\t'/ }" || echo ""
}
script_type() {
  case "$1" in
    *.sh|*.bash|*.zsh) echo "shell" ;;
    *.py) echo "python" ;;
    *) echo "autre" ;;
  esac
}

count_refs() {
  local path="$1"
  local base
  base="$(basename "$path")"
  local hits=0
  local rf

  for rf in "${REF_FILES[@]}"; do
    [[ "$rf" == "$path" ]] && continue
    # chemin complet (relatif) OU basename: heuristique
    if grep -F -q -- "$path" "$rf" 2>/dev/null; then
      hits=$((hits + $(grep -F -- "$path" "$rf" | wc -l | tr -d ' ')))
    fi
    if grep -F -q -- "$base" "$rf" 2>/dev/null; then
      hits=$((hits + $(grep -F -- "$base" "$rf" | wc -l | tr -d ' ')))
    fi
  done

  echo "$hits"
}

# ---------- Rapport TSV ----------
echo -e "path\ttype\texecutable\tshebang\tsize_bytes\tlines\tsha256\tref_hits\treferenced\tduplicate_of" > "$REPORT_PATH"

declare -A sha_first=()

for f in "${SCRIPTS[@]}"; do
  [[ -f "$f" ]] || continue

  typ="$(script_type "$f")"
  exec_flag="$(is_executable "$f")"
  sb="$(shebang "$f")"
  size_bytes="$(wc -c < "$f" | tr -d ' ')"
  lines="$(wc -l < "$f" | tr -d ' ')"
  sha="$(sha256sum "$f" | awk '{print $1}')"
  ref_hits="$(count_refs "$f")"
  referenced="non"
  [[ "$ref_hits" -gt 0 ]] && referenced="oui"

  dup_of=""
  if [[ -z "${sha_first[$sha]+x}" ]]; then
    sha_first["$sha"]="$f"
  else
    dup_of="${sha_first[$sha]}"
  fi

  echo -e "${f}\t${typ}\t${exec_flag}\t${sb}\t${size_bytes}\t${lines}\t${sha}\t${ref_hits}\t${referenced}\t${dup_of}" >> "$REPORT_PATH"
done

total="${#SCRIPTS[@]}"
non_ref_count="$(awk -F'\t' 'NR>1 && $9=="non"{c++} END{print c+0}' "$REPORT_PATH")"
dup_count="$(awk -F'\t' 'NR>1 && $10!=""{c++} END{print c+0}' "$REPORT_PATH")"

echo ""
echo "== Rapport généré =="
echo "  Fichier : $REPORT_PATH"
echo "  Scripts : $total"
echo "  Non référencés (heuristique) : $non_ref_count"
echo "  Doublons (contenu identique) : $dup_count"
echo ""

if [[ "$LIST_ONLY" -eq 1 ]]; then
  echo "== Scripts non référencés (heuristique) =="
  awk -F'\t' 'NR>1 && $9=="non"{print $1}' "$REPORT_PATH"
  exit 0
fi

if [[ "$DO_ARCHIVE" -eq 1 ]]; then
  archive_dir="archives/menage_scripts_${ts}"
  echo "== Archivage des scripts non référencés =="
  echo "  Destination: $archive_dir"
  if [[ "$APPLY" -eq 1 ]]; then
    echo "  Mode: APPLY"
  else
    echo "  Mode: DRY-RUN (ajoute --apply pour déplacer)"
  fi

  mapfile -t TO_MOVE < <(awk -F'\t' 'NR>1 && $9=="non"{print $1}' "$REPORT_PATH")
  if [[ "${#TO_MOVE[@]}" -eq 0 ]]; then
    echo "  Rien à archiver."
    exit 0
  fi

  echo "  Candidats (${#TO_MOVE[@]}):"
  printf '   - %s\n' "${TO_MOVE[@]}"
  echo ""

  [[ "$APPLY" -eq 1 ]] || { echo "DRY-RUN: aucune modification effectuée."; exit 0; }

  mkdir -p "$archive_dir"

  use_git=0
  if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    use_git=1
  fi

  for f in "${TO_MOVE[@]}"; do
    dest="${archive_dir}/${f}"
    mkdir -p "$(dirname "$dest")"
    if [[ "$use_git" -eq 1 ]] && git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
      git mv "$f" "$dest"
    else
      mv "$f" "$dest"
    fi
    echo "Déplacé: $f -> $dest"
  done

  echo ""
  echo "Archivage terminé."
fi

