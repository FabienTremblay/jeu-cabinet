# ACC.011 — inscription d’un utilisateur au lobby

## 1. promesse d’architecture (P251)

Permettre à un utilisateur **non reconnu** d’entrer dans le système,  
sans présumer d’une partie existante,  
et sans introduire de dépendance prématurée avec le moteur de jeu.

**Intention P251**  
- point d’entrée minimal
- création d’une identité exploitable par les activités suivantes (ACC.021, ACC.111)
- responsabilité strictement limitée au contexte *accès / lobby*

---

## 2. objets et invariants

### objets principaux
- **Joueur**
  - `id_joueur` : identifiant technique unique
  - `pseudo` : lisible humain
  - `date_creation`
  - (optionnel) contexte de reprise

### invariants attendus
- un joueur est créé **une seule fois**
- l’identifiant est **stable** sur toute la durée de vie
- aucun lien direct avec une table ou une partie à ce stade
- aucune règle de jeu évaluée ici

---

## 3. flux et canaux

### flux nominal
```
Client
  → POST /api/joueurs
    → service lobby
      → persistance Joueur
      → réponse Joueur
```

### caractéristiques
- synchronisme REST
- aucune émission d’événement métier obligatoire
- pas de Kafka requis pour ACC.011

---

## 4. procédés modernes utilisés (apport à l’architecture)

### séparation des responsabilités
- **ACC.011 n’interagit pas avec le moteur**
- le lobby constitue un *bounded context* autonome

### identités techniques
- génération d’identifiants dès l’entrée
- évite la propagation d’identités faibles (pseudo seul)

### testabilité
- endpoint REST isolable
- persistance testable indépendamment des règles de jeu

👉 Apport clé à l’architecture :  
**retarder volontairement la complexité** (jeu, règles, événements)  
jusqu’à ce qu’elle soit nécessaire.

---

## 5. implémentation réalisée (solution)

### services
- `services/lobby/app.py`
  - endpoint `POST /api/joueurs`
- `services/lobby/domaine.py`
  - entité `Joueur`
- `services/lobby/repositories_sql.py`
  - persistance PostgreSQL

### schémas / contrats
- `services/lobby/schemas.py`
  - schéma de requête et de réponse Joueur

---

## 6. écarts : prévu / fait / revu

### prévu (architecture P251)
- inscription simple
- création d’une identité minimale
- aucune dépendance externe

### fait (implémentation)
- inscription REST complète
- persistance immédiate
- schéma explicite de réponse

### revu (apprentissages)
- nécessité de prévoir tôt la **reprise de contexte**
- clarification de l’erreur « pseudo déjà utilisé »
- importance de tester la création indépendamment de toute table

---

## 7. preuves

### tests
- `services/lobby/tests/test_inscription_joueur.py` (ou équivalent)

### scripts / outils
- `services/cli_cabinet/cabinet_cli.py`  
  (commande ACC.011)

### observabilité
- logs du service lobby
- réponse HTTP explicite (201 / 400)

---

## 8. valeur observable

### pour l’utilisateur
- entrée immédiate dans le système
- récupération d’un identifiant réutilisable

### pour l’équipe
- point d’entrée stable pour tous les scénarios
- base solide pour ACC.021 et ACC.111
- réduction du couplage précoce avec le moteur

---

## 9. contribution au barème (indicatif)

### complexité (travail)
- objets : 1/5
- flux : 1/5
- contrats : 2/5
- règles : 0/5
- projection : 0/5
- outillage : 1/5  
**total ≈ 5/30**

### valeur
- valeur utilisateur : 2/5
- réduction de risque : 3/5
- réduction de dette : 3/5
- accélération future : 4/5
- observabilité/testabilité : 3/5  
**total ≈ 15/25**

---

## 10. conclusion architecturale

ACC.011 démontre que :
- une activité simple mérite une **architecture explicite**
- la valeur n’est pas proportionnelle à la complexité du code
- les procédés modernes (contrats, séparation, tests)  
  **créent de la capacité future dès l’entrée du système**
