# jeu Cabinet (Conseil des ministres)

Simulation politique et stratégique, orientée **événements**, jouable en ligne, inspirée des dynamiques réelles d’un conseil des ministres.

Le projet vise à explorer — de manière ludique mais rigoureuse — la prise de décision collective, les rapports de force, les perturbations internes et externes, et les effets émergents produits par les interactions humaines et institutionnelles.

---

## objectifs du projet

- simuler un **système politique dynamique** plutôt qu’un simple jeu à règles fixes
- expérimenter une architecture **event-driven** proche de systèmes réels
- séparer clairement :
  - le **noyau de jeu** (règles, états, décisions)
  - les **interfaces** (web, mobile, cli)
  - les **moteurs de règles** (versions, évolutivité)
- permettre l’ajout progressif de *skins* (contextes politiques, périodes, scénarios)

---

## principes de conception

- **événement avant état** : l’état est une projection d’événements
- **langage métier explicite**, en français
- **versionnement des règles** (v1, v2, …)
- **faible couplage** entre moteur, règles et interfaces
- **testabilité** du noyau (tests unitaires et d’intégration)

---

## aperçu fonctionnel

- création et gestion de tables de jeu (lobby)
- attribution des rôles (hôte, joueurs, négociateurs)
- déroulement par **phases** et **sous-phases**
- actions disponibles calculées dynamiquement
- journal des événements visibles aux joueurs
- cartes, axes politiques, perturbations, programmes

---

## architecture générale

```
┌─────────────┐      ┌──────────────┐
│ Interfaces  │◀────▶│  API moteur  │
│ (Web/UI)   │      │              │
└─────────────┘      └──────┬───────┘
                             │
                       événements / commandes
                             │
                   ┌─────────▼─────────┐
                   │   Noyau Cabinet    │
                   │ (moteur de jeu)    │
                   └─────────┬─────────┘
                             │
                   ┌─────────▼─────────┐
                   │ Rules Engine (BRE) │
                   │  v1 / v2 / …       │
                   └───────────────────┘
```

---

## structure du dépôt

```
.
├── services/
│   ├── cabinet/              # noyau de jeu (python)
│   │   ├── moteur/
│   │   ├── domaine/
│   │   ├── evenements/
│   │   └── projections/
│   ├── lobby/                # gestion des tables et joueurs
│   ├── api-moteur/            # exposition HTTP du moteur
│   ├── ui-etat-joueur/        # projection dédiée à l’UI
│   ├── rules-service/         # moteur de règles (java / BRE)
│   └── ui2-web/               # interface web (react / ts)
│
├── docker-compose.yml         # stack locale
├── docs/                      # documents d’architecture
└── README.md
```

---

## noyau de jeu (cabinet)

Responsable de :
- la validation des commandes
- l’émission des événements
- la cohérence du déroulement (phases, tours)

Il **ne connaît pas** l’interface utilisateur.

---

## règles et moteur de règles (BRE)

- règles **externes** au noyau
- versionnées (ex. `v1`, `v2`)
- responsables de :
  - calculer les actions disponibles
  - appliquer les effets des cartes
  - gérer certaines transitions complexes

Le moteur de règles peut être remplacé ou enrichi sans modifier le noyau.

---

## événements et vocabulaire

Les échanges entre services reposent sur des messages structurés :

- **commandes** : intentions d’action
- **événements** : faits irréversibles

Chaque événement contient :
- type
- identifiants (partie, table, joueur)
- métadonnées (tour, phase, version)

---

## installation (développement local)

### prérequis

- docker + docker-compose
- python 3.11+
- node 18+
- java 17+

### démarrage

```
docker-compose up --build
```

Les services sont alors accessibles localement (ports définis dans le compose).

---

## état du projet

- projet **en évolution active**
- règles BRE v1 en cours de stabilisation
- interfaces fonctionnelles mais perfectibles
- architecture volontairement explicite et pédagogique

---

## philosophie

Ce jeu n’est pas conçu comme un produit commercial, mais comme :

- un **laboratoire conceptuel**
- un outil de réflexion sur les systèmes politiques
- un terrain d’expérimentation logiciel (événementiel, règles, projections)

---

## contributions

Le projet n’est pas ouvert aux contributions externes pour le moment.

Les discussions, critiques et retours conceptuels sont toutefois bienvenus.

---

## licence

Ce projet est distribué sous licence GNU Affero General Public License v3 (AGPL-3.0).

Cette licence garantit que toute utilisation, modification ou exploitation du logiciel,
y compris via un service réseau, doit conserver le caractère libre et ouvert du projet.

L’objectif est de préserver l’intégrité conceptuelle du jeu et d’éviter toute
appropriation fermée de ses mécanismes.


