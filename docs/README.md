# jeu Cabinet (Conseil des ministres)

Simulation politique et stratégique **événementielle**, jouable en ligne, inspirée des dynamiques réelles d’un conseil des ministres.

Le projet explore — de manière ludique mais rigoureuse — la prise de décision collective, les rapports de force institutionnels, les perturbations internes et externes, et les effets émergents produits par les interactions humaines.

---

## objectifs du projet

- simuler un **système politique dynamique** plutôt qu’un jeu à règles figées
- expérimenter une architecture **event‑driven** proche de systèmes réels
- séparer clairement :
  - le **noyau de jeu** (décisions, événements)
  - les **règles** (versionnées, externalisées)
  - les **interfaces** (web, tui)
- permettre l’ajout progressif de contextes de jeu (*skins*)

---

## principes de conception

- **événement avant état** : l’état est une projection dérivée des événements
- **séparation stricte des responsabilités** entre noyau, règles et UI
- **langage métier explicite**, en français
- **contrats et règles versionnés**
- **testabilité** du noyau et des règles

---

## documentation

La documentation détaillée se trouve dans le dossier `docs/` :

- **architecture générale** : `docs/architecture.md`
- **exécution locale (docker‑compose)** : `docs/execution-locale.md`
- **documents de conception** : `Document/`
- **contrats (avro / jsonschema / openapi)** : `contrats/`

---

## aperçu fonctionnel

- création et gestion de tables de jeu (lobby)
- attribution des rôles (hôte, joueurs)
- déroulement par **phases** et **sous‑phases**
- actions disponibles calculées dynamiquement
- journal des événements par joueur
- cartes, programmes, perturbations et axes politiques

---

## architecture (résumé)

```
UI (web / tui)
      │
      ▼
api_moteur (façade HTTP)
      │
      ▼
Kafka (commandes / événements)
      │
      ▼
Cabinet (noyau de jeu)
      │
      ▼
Rules‑service (BRE, règles versionnées)
```

Pour le détail des flux et responsabilités, voir `docs/architecture.md`.

---

## structure du dépôt (simplifiée)

```
.
├── docs/                 # documentation lisible GitHub
├── Document/             # documents de conception (odt, eddx)
├── contrats/             # contrats techniques (avro, jsonschema, openapi)
├── docker/               # configuration infra (traefik, kafka)
├── rules-service/        # moteur de règles (java / BRE)
├── services/             # services applicatifs (python, ui)
├── scripts/              # scripts utilitaires
├── docker-compose.yml
└── README.md
```

---

## exécution locale

### prérequis

- docker + docker‑compose
- python 3.11+
- node 18+
- java 17+

### démarrage rapide

```bash
cp .env.example .env
docker-compose up --build
```

Pour les détails (ports, kafka, registry, scripts), voir :
`docs/execution-locale.md`.

---

## état du projet

- projet **en évolution active**
- règles v1 en cours de stabilisation
- interfaces fonctionnelles, amélioration continue
- architecture volontairement explicite et pédagogique

---

## philosophie

Ce projet n’est pas conçu comme un produit commercial, mais comme :

- un **laboratoire conceptuel**
- un outil de réflexion sur les systèmes politiques
- un terrain d’expérimentation logiciel (événements, règles, projections)

---

## contributions

Le projet n’est pas ouvert aux contributions externes pour le moment.

Les retours conceptuels, critiques argumentées et signalements de bugs reproductibles sont toutefois bienvenus.

Voir `CONTRIBUTING.md`.

---

## sécurité

Voir `SECURITY.md` pour la politique de signalement des vulnérabilités.

---

## licence

Le code source est distribué sous licence **GNU Affero General Public License v3 (AGPL‑3.0)**.

Cette licence garantit que toute utilisation, y compris via un service réseau, conserve le caractère libre et ouvert du projet.

Voir le fichier `LICENSE` pour le texte complet.

