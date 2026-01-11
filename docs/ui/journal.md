# journal & notifications

Ce document décrit le journal côté UI et la manière dont il est exposé au front via `ui_etat_joueur`.

## contrat principal (ui_etat_joueur)

Endpoint :
- `GET /ui/joueurs/{joueur_id}/situation`

Objet retourné : `SituationJoueurDTO` (voir `contrats/jsonschema/http/ui_etat_joueur/SituationJoueurDTO.schema.json`)

Champs clés :
- `journal_recent[]` : liste de `EntreeJournalDTO`
- `actions_disponibles[]` : liste de `ActionDisponibleDTO`
- `marqueurs` : `MarqueursMajDTO` (timestamps de maj)
- `ancrage` : `AncrageDTO` (lobby/table/partie)

## EntreeJournalDTO

Champs attendus (résumé) :
- `occurred_at` (date-time) : horodatage de l'événement
- `message` (string) : texte prêt à afficher
- `severity` (string|null) : gravité (si utilisée)
- `category` (string|null) : catégorie (si utilisée)
- `code` (string|null) : code interne (si utilisé)
- `event_id` (string|null) : id de l'événement source (si disponible)
- `meta` (object) : données additionnelles
- `audience` (object|null) : ciblage/portée (si utilisée)

## règles d'affichage (conventions)

- `message` doit être compréhensible sans inspecter `meta`.
- `meta` sert à enrichir (debug, détails UI, analytics), pas à porter le sens principal.
- `occurred_at` est la clé de tri (du plus récent au plus ancien côté UI).

## à clarifier / décisions à prendre

- vocabulaire exact de `severity` (ex: info/warn/error) et mapping UI
- usage de `category` (groupement, filtres, onglets)
- format d'`audience` (si on le standardise)
