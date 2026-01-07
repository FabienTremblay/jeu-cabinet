#!/usr/bin/env bash

# Nom du fichier de sortie
OUTFILE="stats_fichiers.tsv"

# En-tête
printf "path\tcreation\tmodification\tlines\n" > "$OUTFILE"

# Parcours récursif de tous les fichiers, en excluant les .pyc
find . -type f ! -name "*.pyc" -print0 | while IFS= read -r -d '' f; do
    # Date de création (peut être "-" si inconnue)
    creation=$(stat -c %w "$f")
    [ "$creation" = "-" ] && creation=""

    # Date de dernière modification
    modification=$(stat -c %y "$f")

    # Nombre de lignes (si texte lisible)
    if lines=$(wc -l < "$f" 2>/dev/null); then
        :
    else
        lines=""
    fi

    # Écriture dans le fichier TSV
    printf "%s\t%s\t%s\t%s\n" "$f" "$creation" "$modification" "$lines" >> "$OUTFILE"
done

echo "Statistiques écrites dans : $OUTFILE"
