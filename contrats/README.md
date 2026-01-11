# contrats — centre de vérité

Ce répertoire centralise **tous les contrats du projet jeu Cabinet**.

Un contrat définit une **interface stable** entre deux parties du système (services, UI, moteur de règles), indépendamment de leur implémentation.

L’objectif est de rendre l’architecture :
- lisible pour les collaborateurs,
- explicite sur les responsabilités,
- robuste face à l’évolution.

---

## principes

- un contrat = un engagement explicite
- les contrats sont **versionnés** et **documentés**
- la source de vérité est **centralisée ici**, même si les services génèrent les artefacts
- on privilégie la stabilité et la rétro-compatibilité

---

## structure du répertoire

```
contrats/
├── README.md              # ce document
├── openapi/               # snapshots OpenAPI des services HTTP
└── jsonschema/
    ├── _common/           # schémas partagés
    │   └── http/          # erreurs et structures communes HTTP
    └── http/              # schémas JSON extraits des OpenAPI
        ├── lobby/
        ├── api_moteur/
        └── ui_etat_joueur/
```

---

## contrats HTTP (OpenAPI)

### rôle

Les fichiers OpenAPI décrivent les **interfaces HTTP publiques** exposées par les services.

Ils constituent la **source de vérité fonctionnelle** pour :
- les développeurs front-end,
- les intégrations,
- la génération des schémas JSON.

### fichiers canoniques

- `openapi/lobby.openapi.json`
- `openapi/api_moteur.openapi.json`
- `openapi/ui_etat_joueur.openapi.json`

Ces fichiers sont des **snapshots versionnés** des OpenAPI générées par les services en cours d’exécution.

---

## contrats HTTP (JSON Schema)

### rôle

Les schémas JSON sont extraits automatiquement des sections `components.schemas` des OpenAPI.

Ils servent à :
- clarifier les DTO sans parcourir le code,
- faciliter la validation,
- servir de référence contractuelle indépendante des frameworks.

### organisation

- `jsonschema/http/<service>/` : schémas propres à un service
- `jsonschema/_common/http/` : schémas partagés (ex. erreurs de validation)

Exemples :

- `jsonschema/http/lobby/DemandeCreationTable.schema.json`
- `jsonschema/http/ui_etat_joueur/SituationJoueurDTO.schema.json`
- `jsonschema/_common/http/ValidationError.schema.json`

---

## workflow de mise à jour

1. les services exposent leur OpenAPI (FastAPI / autre)
2. on capture un snapshot dans `contrats/openapi/`
3. on extrait les schémas JSON via le script dédié

Commande de référence :

```bash
./scripts/sync-openapi.sh
```

Ce script :
- récupère les OpenAPI actives
- les versionne dans `contrats/openapi/`
- génère les schémas JSON dans `contrats/jsonschema/http/`

---

## règles de stabilité

- les fichiers OpenAPI sont considérés **contractuels**
- toute modification doit être intentionnelle et relue
- les schémas JSON reflètent l’état réel des services
- les schémas communs (`_common`) sont particulièrement sensibles

---

## périmètre actuel

À ce stade, ce répertoire couvre :
- les contrats HTTP des services (lobby, moteur, UI état joueur)

Les contrats internes suivants seront ajoutés progressivement :
- contrats BRE (moteur de règles)
- contrats commandes / événements (Kafka)

---

## philosophie

Les contrats sont traités comme du **code critique** :

- ils structurent les échanges,
- ils portent le vocabulaire métier,
- ils conditionnent l’évolutivité du système.

Un contrat flou est une dette.
