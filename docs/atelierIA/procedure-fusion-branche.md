# Procédure de fusion de branche

Ce document décrit la procédure recommandée avant de fusionner une branche de
travail vers `main` pour le projet `jeu-cabinet`.

Il complète :

- `CONTRIBUTING.md` ;
- `docs/execution-docker.md` ;
- `docs/atelierIA/codex-gardien-issues.md`.

## Objectif

Une fusion vers `main` doit préserver :

- les contrats publics ;
- les règles métier ;
- les données locales ou MaisonLinux ;
- la capacité de redémarrer la stack Docker ;
- la traçabilité des décisions dans GitHub Issues.

La fusion ne doit pas dépendre d'une destruction de volume ou d'une intervention
implicite non documentée.

## Préparation

Avant la fusion :

1. vérifier l'état Git ;
2. lister les fichiers modifiés ;
3. identifier les contrats touchés ;
4. identifier les migrations SQL ajoutées ;
5. vérifier les issues GitHub associées.

Commandes utiles :

```bash
git status --short
git diff --stat
git diff --check
```

Si des changements non liés sont présents, les séparer avant la fusion ou les
documenter explicitement.

## Revue Des Contrats

Si la branche modifie une API HTTP, un DTO, un événement Kafka ou une structure
JSON, vérifier les sources de vérité :

- `contrats/openapi/` ;
- `contrats/jsonschema/` ;
- `contrats/README.md` si présent ;
- `docs/ui/contracts.md` ;
- `docs/ui/flux-auth-lobby-table.md` ;
- `docs/ui/journal.md`.

Points à confirmer :

- les noms métier français sont conservés ;
- les ruptures sont documentées ;
- les schémas sont cohérents avec les types backend et frontend ;
- les changements UI ne créent pas de logique métier absente des contrats.

## Tests Avant Fusion

Lancer les tests pertinents selon les zones touchées.

Commandes de référence :

```bash
pytest -q
```

```bash
cd rules-service && mvn test
```

```bash
cd services/ui-web && npm test
```

```bash
cd services/ui-web && npm run build
```

```bash
docker compose config --quiet
```

Si un outil n'est pas disponible dans l'environnement courant, le signaler dans
le rapport de fusion.

## Validation Docker

Valider au minimum la configuration Docker de l'environnement concerné.

Développement :

```bash
docker compose --env-file .env.dev.example -p cabinet-dev-test -f docker-compose.yml -f docker-compose.dev.yml config --quiet
```

MaisonLinux :

```bash
docker compose --env-file .env.maisonlinux.example -p cabinet-maisonlinux-test -f docker-compose.yml -f docker-compose.maisonlinux.yml config --quiet
```

Production future :

```bash
docker compose --env-file .env.prod.example -p cabinet-prod-test -f docker-compose.yml -f docker-compose.prod.yml config --quiet
```

## Migrations SQL

Si la branche ajoute ou modifie une structure SQL, utiliser la mécanique maison
de migrations.

Avant fusion :

1. vérifier que le fichier `sql/migrations/<version>_<nom>.sql` existe ;
2. vérifier que la migration est idempotente autant que possible ;
3. appliquer les migrations sur un environnement de développement ;
4. rejouer le script une seconde fois ;
5. vérifier `schema_migrations`.

Commandes :

```bash
make migrate-dev
```

ou :

```bash
docker compose --env-file .env.dev -p cabinet-dev -f docker-compose.yml -f docker-compose.dev.yml exec postgres /opt/sql/apply-migrations.sh
```

Contrôle :

```bash
docker compose --env-file .env.dev -p cabinet-dev -f docker-compose.yml -f docker-compose.dev.yml exec postgres psql -U jeu -d jeu -c "select version, nom, applique_le from schema_migrations order by version"
```

Ne pas utiliser `docker compose down -v` pour appliquer une évolution SQL sur
une base existante.

## Procédure MaisonLinux Après Fusion

Après fusion dans `main`, sur MaisonLinux :

1. récupérer la nouvelle version ;
2. valider la configuration Docker ;
3. appliquer les migrations ;
4. redémarrer les services si nécessaire ;
5. vérifier les logs principaux.

Commandes indicatives :

```bash
git fetch
git switch main
git pull
```

```bash
docker compose --env-file .env.maisonlinux -p cabinet-maisonlinux -f docker-compose.yml -f docker-compose.maisonlinux.yml config --quiet
```

```bash
make migrate-maisonlinux
```

```bash
docker compose --env-file .env.maisonlinux -p cabinet-maisonlinux -f docker-compose.yml -f docker-compose.maisonlinux.yml up -d --build
```

Logs utiles :

```bash
docker compose --env-file .env.maisonlinux -p cabinet-maisonlinux -f docker-compose.yml -f docker-compose.maisonlinux.yml logs -f --tail=200 lobby
docker compose --env-file .env.maisonlinux -p cabinet-maisonlinux -f docker-compose.yml -f docker-compose.maisonlinux.yml logs -f --tail=200 api-moteur
docker compose --env-file .env.maisonlinux -p cabinet-maisonlinux -f docker-compose.yml -f docker-compose.maisonlinux.yml logs -f --tail=200 moteur-commands
```

## Issues GitHub

Avant fusion, vérifier les issues associées :

- l'issue décrit bien les critères d'acceptation ;
- les critères satisfaits sont commentés ;
- les tests exécutés ou non exécutés sont mentionnés ;
- les limites restantes sont documentées.

Utiliser `docs/atelierIA/codex-gardien-issues.md` pour les règles de
maintenance.

Ne pas fermer une issue importante sans validation explicite.

## Retour Arrière

Le retour arrière dépend du type de changement.

Pour un changement applicatif sans migration destructive :

```bash
git switch main
git revert <commit>
docker compose --env-file .env.maisonlinux -p cabinet-maisonlinux -f docker-compose.yml -f docker-compose.maisonlinux.yml up -d --build
```

Pour un changement SQL :

- ne pas supprimer les volumes ;
- ne pas supposer qu'un `down -v` est acceptable ;
- documenter une migration corrective si nécessaire ;
- demander validation humaine avant toute action destructive.

## Checklist Finale

Avant de déclarer la fusion prête :

- `git diff --check` est OK ;
- les tests pertinents sont exécutés ou les limites sont signalées ;
- les contrats modifiés sont synchronisés ;
- les migrations SQL sont appliquées et rejouables ;
- la documentation impactée est à jour ;
- les issues GitHub sont commentées ;
- le plan MaisonLinux est clair ;
- aucun secret local n'est ajouté ;
- aucune destruction de volume n'est requise.

## Rapport De Fusion Attendu

Le rapport doit contenir :

- résumé des changements ;
- contrats touchés ;
- migrations SQL à appliquer ;
- tests exécutés ;
- tests non exécutés ;
- documentation mise à jour ;
- issues GitHub concernées ;
- commandes MaisonLinux à lancer après fusion ;
- risques ou points de vigilance.
