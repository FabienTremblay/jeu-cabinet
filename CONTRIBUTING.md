# contributing

## état du projet
Le projet n’est pas ouvert aux contributions externes (PR) pour le moment.
La stabilité d’ensemble (contrats, règles, event-driven) exige une coordination serrée.

## retours acceptés
Les retours utiles :
- signalements de bugs reproductibles (avec logs)
- critiques conceptuelles sur les règles / phases
- suggestions sur l’architecture (contrats, projections, idempotence)

## comment signaler un bug
Merci d’inclure :
- étapes de reproduction (le plus minimal possible)
- résultat attendu vs obtenu
- logs pertinents
- commit/tag (ou date) + environnement (OS, docker)

## conventions internes (si tu contribues en “core team”)
- français privilégié pour le vocabulaire métier
- tests requis avant merge
- éviter les renommages inutiles des types/DTO (stabilité des contrats)
