# ACC.111 — gestion des tables (création, consultation, rejoindre)

## 1. promesse d’architecture (P251)

Permettre aux utilisateurs connectés de **se regrouper intentionnellement**  
autour d’une table de jeu,  
sans démarrer la partie ni activer le moteur.

**Intention P251**
- introduire un espace collectif intermédiaire (la table)
- préparer la coordination entre joueurs
- maintenir la séparation *accès / lobby* vs *jeu*

---

## 2. objets et invariants

### objets principaux
- **Table**
  - `id_table`
  - `nom_table`
  - `nb_sieges`
  - `id_hote`
  - `statut` (ouverte, en_attente, lancee)
- **Siege**
  - association unique joueur ↔ table

### invariants attendus
- une table a un nombre fixe de sièges
- un joueur ne peut occuper qu’un seul siège par table
- une table peut exister sans partie associée
- aucune règle de jeu n’est évaluée à ce stade

---

## 3. flux et canaux

### flux principaux
```
Client
  → POST /api/tables            (création)
  → GET  /api/tables            (consultation)
  → POST /api/tables/{id}/joueurs (rejoindre)
```

### caractéristiques
- REST synchrones
- transactions courtes
- aucune dépendance au moteur ou au BRE

---

## 4. procédés modernes utilisés (apport à l’architecture)

### bounded context explicite
- la **table** est un concept autonome
- le lobby gère la coordination humaine, pas le jeu

### invariants métier centralisés
- règles de sièges gérées côté service
- élimination des règles implicites côté client

### anticipation de la distribution
- la table sert de frontière naturelle
  avant l’introduction des événements

👉 Apport clé à l’architecture :  
**formaliser un espace collectif sans déclencher le système complexe**.

---

## 5. implémentation réalisée (solution)

### services
- `services/lobby/app.py`
  - `POST /api/tables`
  - `GET /api/tables`
  - `POST /api/tables/{id}/joueurs`
- `services/lobby/services_lobby.py`
  - règles de création et de prise de siège
- `services/lobby/domaine.py`
  - entité `Table`
- `services/lobby/repositories_sql.py`
  - persistance

### schémas / contrats
- `services/lobby/schemas.py`
  - schémas Table / JoinTable

---

## 6. écarts : prévu / fait / revu

### prévu (architecture P251)
- gestion simple des regroupements
- tables comme prérequis au jeu

### fait (implémentation)
- API REST complète
- invariants explicitement codés
- persistance immédiate

### revu (apprentissages)
- importance de la concurrence (2 joueurs rejoignent en même temps)
- clarification du rôle de l’hôte
- séparation stricte table ≠ partie

---

## 7. preuves

### tests
- `services/lobby/tests/test_tables.py`
- `services/lobby/tests/test_rejoindre_table.py`

### scripts / outils
- `services/cli_cabinet/cabinet_cli.py`
  (commandes ACC.111)

### observabilité
- logs de création et de jointure
- réponses HTTP explicites (200 / 400 / 409)

---

## 8. valeur observable

### pour l’utilisateur
- visibilité des tables disponibles
- choix explicite de rejoindre un groupe

### pour l’équipe
- réduction de la complexité du moteur
- base claire pour ACC.115 (prêt / lancer)
- meilleure testabilité des règles sociales

---

## 9. contribution au barème (indicatif)

### complexité (travail)
- objets : 2/5
- flux : 2/5
- contrats : 2/5
- règles : 1/5
- projection : 0/5
- outillage : 1/5  
**total ≈ 8/30**

### valeur
- valeur utilisateur : 3/5
- réduction de risque : 3/5
- réduction de dette : 4/5
- accélération future : 4/5
- observabilité/testabilité : 3/5  
**total ≈ 17/25**

---

## 10. conclusion architecturale

ACC.111 montre que :
- la coordination humaine mérite un traitement architectural dédié
- introduire des objets intermédiaires réduit la complexité globale
- les procédés modernes aident à retarder l’activation du moteur
  tout en préparant sa mise en œuvre
