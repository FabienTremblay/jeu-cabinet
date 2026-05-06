# AGENTS.md

## Objectif Du Projet

Le projet est un système de jeu distribué, orienté événements, avec :

- contrats OpenAPI et JSON Schema ;
- services Python découplés ;
- moteur de règles Java / Quarkus ;
- UI web React / TypeScript ;
- projections d’état joueur ;
- intégration Kafka ;
- Docker Compose pour l’exécution locale.

L’architecture, les contrats et le vocabulaire métier priment sur les optimisations locales.

## Principes Directeurs

### Préserver L’architecture

Ne pas effectuer de refactorisation massive sans demande explicite.

Respecter les frontières suivantes :

- `contrats/` : source de vérité des interfaces ;
- `services/cabinet/` : noyau de jeu ;
- `services/api_moteur/` : façade HTTP du moteur ;
- `services/lobby/` : tables, joueurs, sièges ;
- `services/ui_etat_joueur/` : projection UI ;
- `services/ui-web/` : frontend React ;
- `rules-service/` : moteur de règles ;
- `services/commande_moteur/` et `services/adapter-evenements/` : workers Kafka.

Ne pas fusionner arbitrairement les couches, déplacer les dossiers, renommer les concepts métier ou introduire un framework de remplacement sans validation.

### Priorité Aux Contrats

Avant toute modification d’API, DTO, événement, structure JSON, échange Kafka ou comportement UI, vérifier :

- `contrats/openapi/`
- `contrats/jsonschema/`
- `contrats/README.md`
- `Document/ui-contracts.md`
- `services/ui-web/docs/UI-Contracts.md`

Les contrats sont la source de vérité. Toute rupture doit être explicitée avec impacts et proposition de migration.

### Vocabulaire Français Stable

Conserver les termes métier français existants. Ne pas remplacer arbitrairement :

- `etat`
- `joueur`
- `partie`
- `situation`
- `action`
- `marqueur`
- `ancrage`
- `moteur`
- `règles`
- `événements`
- `lobby`

## Manière De Travailler

Avant modification importante :

1. lire les fichiers pertinents ;
2. expliquer la compréhension actuelle ;
3. proposer un plan minimal ;
4. appliquer des changements localisés ;
5. lister les impacts et contrats affectés ;
6. lancer les tests pertinents ou signaler ceux non exécutés.

Ne pas modifier les fichiers non liés à la tâche.

Éviter les changements dans :

- `.env`
- archives `.zip`
- `node_modules/`
- caches Python / pytest / Maven / Vite
- fichiers binaires de documentation
- données locales ou exportées

## Tests Et Validation

Commandes probables :

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
docker compose config
```

Pour l’exécution locale :

```bash
docker compose up --build
```

ou :

```bash
make up
```

Toujours signaler les tests non exécutés.

## Kafka

Les topics, événements et commandes doivent rester explicites, traçables et compatibles avec les contrats.

Documenter tout nouveau topic ou nouveau type d’événement.

Ne pas introduire d’événements implicites ou ambigus.

## Règles Métier

Le `rules-service` est une composante métier critique.

Ne pas contourner les règles, dupliquer la logique métier dans l’UI ou déplacer les validations sans justification.

Privilégier les règles centralisées, les validations explicites et les tests reproductibles.

## UI Web

Le frontend est réactif : il affiche l’état projeté et envoie les actions disponibles.

Il ne doit pas inventer :

- d’actions absentes de `actions_disponibles` ;
- d’interprétation métier de phase ;
- de navigation contraire à `ancrage` ;
- de logique de jeu côté UI.

## Sécurité

Ne jamais exposer ou modifier inutilement les secrets.

Respecter :

- `.env.example` comme modèle public ;
- `.env` comme fichier local non versionné ;
- `SECURITY.md` pour les règles de sécurité.

Ne pas contourner la sécurité pour résoudre un problème local.

## Documentation

Pour une décision structurante, proposer une mise à jour dans `docs/` ou une courte note d’architecture.

Les décisions doivent rester compréhensibles plusieurs mois plus tard.
