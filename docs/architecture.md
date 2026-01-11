# architecture — jeu Cabinet

Ce document présente l’architecture générale du projet **jeu Cabinet** : ses principes, ses composants majeurs et les flux qui les relient.

L’architecture est volontairement **explicite, modulaire et événementielle**, afin de servir à la fois :
- de support de jeu,
- de laboratoire conceptuel,
- de terrain d’expérimentation logiciel.

---

## principes structurants

### 1. architecture événementielle

- les **commandes** expriment une intention
- les **événements** décrivent des faits irréversibles
- l’**état** est une projection dérivée des événements

Aucun service ne modifie directement l’état d’un autre service.

---

### 2. séparation stricte des responsabilités

- le **noyau** décide
- les **règles** calculent et contraignent
- les **projections** traduisent pour l’UI
- les **interfaces** consomment, jamais l’inverse

Cette séparation permet d’évoluer indépendamment chaque couche.

---

### 3. vocabulaire métier explicite

- français privilégié
- concepts stables (phase, sous-phase, tour, action, attente)
- contrats versionnés

Le vocabulaire est considéré comme un artefact architectural.

---

## vue d’ensemble

```
                 ┌──────────────────┐
                 │    ui-web / tui   │
                 │  (interfaces)    │
                 └─────────▲────────┘
                           │ HTTP
                           │
                 ┌─────────┴────────┐
                 │    api_moteur    │
                 │ (façade HTTP)   │
                 └─────────▲────────┘
                           │ commandes
                           │
        ┌──────────────────┴──────────────────┐
        │              kafka                   │
        │      (bus d’événements)              │
        └─────────▲───────────────▲────────────┘
                  │               │
          événements│               │commandes
                  │               │
      ┌───────────┴──────┐  ┌─────┴───────────┐
      │      cabinet     │  │ commande_moteur │
      │  (noyau de jeu)  │  │  (worker cmd)   │
      └───────────▲──────┘  └─────────────────┘
                  │
          appels règles
                  │
          ┌───────┴────────┐
          │  rules-service  │
          │      (BRE)      │
          └────────────────┘
```

---

## composants principaux

### cabinet — noyau de jeu

Responsabilités :
- validation des commandes
- orchestration du déroulement (phases, tours)
- émission des événements
- garantie de cohérence métier

Caractéristiques :
- aucune dépendance UI
- dépendance abstraite vers les règles
- logique déterministe

---

### rules-service — moteur de règles (BRE)

Responsabilités :
- calculer les actions disponibles
- valider l’usage des cartes
- gérer les transitions complexes

Caractéristiques :
- règles versionnées (`v1`, `v2`, …)
- implémentation Java (DMN / DRL)
- remplaçable sans modifier le noyau

---

### api_moteur — façade HTTP

Responsabilités :
- exposer le moteur au monde extérieur
- adapter HTTP → commandes
- valider les schémas d’entrée

Aucune logique métier persistante.

---

### kafka — bus d’événements

Responsabilités :
- transport des commandes et événements
- découplage des services
- support de la projection asynchrone

Caractéristiques :
- KRaft (sans Zookeeper)
- création automatique des topics désactivée

---

### projections (ui_etat_joueur)

Responsabilités :
- transformer les événements en état lisible
- produire une vue spécifique par joueur
- alimenter journal, notifications et actions disponibles

Ces projections sont **jetables** et recalculables.

---

### lobby

Responsabilités :
- gestion des tables
- gestion des joueurs
- persistance des sièges et statuts

Le lobby est volontairement séparé du noyau de jeu.

---

## flux principaux

### 1. action joueur

1. l’UI déclenche une action
2. l’API moteur transforme en commande
3. la commande est publiée sur Kafka
4. le noyau traite et émet des événements
5. les projections se mettent à jour
6. l’UI consomme l’état projeté

---

### 2. calcul des règles

1. le noyau prépare un contexte métier
2. appel au rules-service
3. application des règles versionnées
4. retour des décisions calculées

---

## versionnement

- règles : versionnées par dossier (`v1`, `v2`, …)
- contrats : versionnés explicitement
- événements : stables et rétrocompatibles

La compatibilité est privilégiée sur la nouveauté.

---

## choix assumés

- complexité explicite plutôt qu’implicite
- séparation forte plutôt que rapidité de prototypage
- cohérence métier avant ergonomie

---

## périmètre volontairement exclu

- intelligence artificielle autonome
- matchmaking
- persistance événementielle distribuée

Ces éléments pourront être ajoutés ultérieurement.

---

## lien avec la documentation

- exécution locale : `docs/execution-locale.md`
- contrats : `contrats/`
- règles BRE : `rules-service/.../README.md`
- documents de conception : `Document/`

