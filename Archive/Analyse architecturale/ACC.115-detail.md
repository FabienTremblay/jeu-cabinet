# ACC.115 — état prêt et lancement de la partie

## 1. promesse d’architecture (P251)

Permettre aux joueurs regroupés autour d’une table de **confirmer leur disponibilité**
et de **déclencher explicitement le démarrage d’une partie**,  
sans que le lobby ne prenne en charge la logique de jeu.

**Intention P251**
- introduire un mécanisme collectif de synchronisation (prêt)
- déclencher le passage du monde *accès / coordination* vers le monde *jeu*
- marquer une frontière architecturale claire avant le moteur

---

## 2. objets et invariants

### objets principaux
- **Table**
  - `statut` : ouverte → en_attente → lancee
- **JoueurTable**
  - indicateur `pret`
- **EvenementPartieLancee**
  - signal unique de transition vers le jeu

### invariants attendus
- un joueur peut changer son état prêt librement tant que la partie n’est pas lancée
- une partie ne peut être lancée qu’une seule fois par table
- le lancement nécessite des conditions explicites (ex. tous prêts, hôte)
- aucune création de partie n’a lieu dans le lobby

---

## 3. flux et canaux

### flux nominal
```
Client
  → POST /api/tables/{id}/joueurs/pret
  → POST /api/tables/{id}/lancer
      → validation des invariants
      → émission EvenementPartieLancee
```

### caractéristiques
- REST synchrones côté lobby
- émission d’un événement métier asynchrone
- aucune dépendance directe au moteur

---

## 4. procédés modernes utilisés (apport à l’architecture)

### passage REST → événement
- le lobby **déclenche** mais n’orchestre pas
- la responsabilité est transférée par événement

### découplage intentionnel
- ACC.115 ne connaît ni le moteur ni les règles
- seul le fait “la partie est lancée” est publié

### robustesse par événement
- possibilité de reprise
- possibilité de consommateurs multiples

👉 Apport clé à l’architecture :  
**faire du lancement une transition observable, pas un appel direct**.

---

## 5. implémentation réalisée (solution)

### services
- `services/lobby/app.py`
  - `POST /api/tables/{id}/joueurs/pret`
  - `POST /api/tables/{id}/lancer`
- `services/lobby/services_lobby.py`
  - règles de validation (prêt, autorité)
- `services/lobby/events.py`
  - `EvenementPartieLancee`

### intégration
- publication Kafka sur `cabinet.parties.evenements`

---

## 6. écarts : prévu / fait / revu

### prévu (architecture P251)
- transition contrôlée vers le jeu
- responsabilité minimale du lobby

### fait (implémentation)
- validation complète côté lobby
- émission explicite d’un événement dédié

### revu (apprentissages)
- clarification des règles de lancement
- gestion des cas limites (joueur quitte, double clic)
- importance de l’idempotence de l’événement

---

## 7. preuves

### tests
- `services/lobby/tests/test_pret_joueur.py`
- `services/lobby/tests/test_lancer_partie.py`

### scripts / outils
- `services/cli_cabinet/cabinet_cli.py`
  (commandes ACC.115)

### observabilité
- logs d’état prêt
- message Kafka `EvenementPartieLancee`

---

## 8. valeur observable

### pour l’utilisateur
- visibilité claire de l’état des autres joueurs
- démarrage maîtrisé de la partie

### pour l’équipe
- frontière nette lobby / moteur
- point d’entrée unique pour le jeu
- base solide pour l’orchestration event-driven

---

## 9. contribution au barème (indicatif)

### complexité (travail)
- objets : 2/5
- flux : 3/5
- contrats : 2/5
- règles : 2/5
- projection : 1/5
- outillage : 1/5  
**total ≈ 11/30**

### valeur
- valeur utilisateur : 4/5
- réduction de risque : 4/5
- réduction de dette : 4/5
- accélération future : 5/5
- observabilité/testabilité : 4/5  
**total ≈ 21/25**

---

## 10. conclusion architecturale

ACC.115 constitue un **point d’inflexion architectural** :
- la coordination devient un signal événementiel
- le lobby cesse définitivement d’être un orchestrateur
- les procédés modernes permettent une transition propre
  vers un système distribué et testable
