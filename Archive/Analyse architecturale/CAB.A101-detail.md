# CAB.A101 — création et mise en place de la partie (orchestration)

## 1. promesse d’architecture (P251)

Transformer le **signal de lancement** émis par le lobby  
en une **partie jouable initialisée**,  
sans coupler le lobby au moteur ni aux règles de jeu.

**Intention P251**
- orchestrer la création de la partie
- établir l’état initial du jeu
- préparer le cycle décision → commandes → effets

CAB.A101 est la **porte d’entrée officielle** dans le monde du jeu.

---

## 2. objets et invariants

### objets principaux
- **Partie**
  - `id_partie`
  - `id_table`
  - `joueurs`
  - `skin`
- **Etat**
  - axes initiaux
  - économie initiale
  - decks initialisés
  - programme vide
- **Commande**
  - `op = partie.creer`
  - paramètres de création

### invariants attendus
- une partie est créée **une seule fois par table**
- la création est **idempotente**
- l’état initial est cohérent et complet
- aucune règle métier de jeu n’est évaluée ici

---

## 3. flux et canaux

### flux nominal
```
EvenementPartieLancee (Kafka)
  → adapter-evenements
    → Commande { op: "partie.creer" }
      → cab.commands (Kafka)
        → commande_moteur
          → API moteur
            → création Partie + Etat
```

### caractéristiques
- entièrement asynchrone jusqu’à l’API moteur
- découplage total lobby ↔ moteur
- orchestration par événements et commandes

---

## 4. procédés modernes utilisés (apport à l’architecture)

### event-driven orchestration
- le lobby **annonce**
- l’adapter **traduit**
- le moteur **exécute**

### anti-corruption layer
- l’adapter protège le moteur
  des formats et décisions du lobby

### commandes comme contrat interne
- format stable
- traçable
- testable indépendamment

👉 Apport clé à l’architecture :  
**l’orchestration devient observable, découplée et remplaçable**.

---

## 5. implémentation réalisée (solution)

### services
- `services/adapter-evenements/adapter_evenements/worker_adapter.py`
  - consommation `cabinet.parties.evenements`
  - production `cab.commands`
- `services/commande_moteur/worker_moteur.py`
  - consommation `cab.commands`
  - appel API moteur
- `services/api_moteur/app.py`
  - endpoint de création de partie
- `services/cabinet/moteur/etat.py`
  - initialisation de l’état

### contrats
- enveloppe commande `{ op, params, meta }`
- paramètres initiaux issus du lobby

---

## 6. écarts : prévu / fait / revu

### prévu (architecture P251)
- création de partie déclenchée par un signal
- séparation stricte des responsabilités

### fait (implémentation)
- chaîne événement → commande → API
- état initial construit côté moteur

### revu (apprentissages)
- importance critique de l’idempotence
- nécessité d’une traçabilité cause → effet
- clarification du rôle exact de l’adapter

---

## 7. preuves

### tests
- tests d’intégration adapter / commande_moteur
- tests moteur d’initialisation d’état

### scripts / outils
- `scripts/bootstrap-topics.sh`
- scénarios de lancement manuel

### observabilité
- logs Kafka (event + command)
- logs création partie moteur

---

## 8. valeur observable

### pour l’utilisateur
- démarrage fiable de la partie
- absence de comportements ambigus au lancement

### pour l’équipe
- découplage fort lobby / moteur
- possibilité d’ajouter d’autres sources d’événements
- facilité de test et de simulation

---

## 9. contribution au barème (indicatif)

### complexité (travail)
- objets : 3/5
- flux : 4/5
- contrats : 3/5
- règles : 1/5
- projection : 2/5
- outillage : 2/5  
**total ≈ 15/30**

### valeur
- valeur utilisateur : 4/5
- réduction de risque : 5/5
- réduction de dette : 5/5
- accélération future : 5/5
- observabilité/testabilité : 4/5  
**total ≈ 23/25**

---

## 10. conclusion architecturale

CAB.A101 est le **pivot architectural** du projet :
- il valide l’architecture event-driven
- il rend le moteur indépendant du lobby
- il transforme une intention humaine
  en une réalité jouable de manière maîtrisée

C’est à partir de CAB.A101 que
l’architecture commence réellement à “porter” le développement.
