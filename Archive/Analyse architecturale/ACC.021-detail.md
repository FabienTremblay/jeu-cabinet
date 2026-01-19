# ACC.021 — connexion d’un utilisateur reconnu

## 1. promesse d’architecture (P251)

Permettre à un utilisateur **déjà inscrit** de reprendre l’accès au système  
sans recréer son identité,  
et sans dépendre d’une partie ou d’un état de jeu actif.

**Intention P251**
- distinguer clairement *inscription* et *connexion*
- permettre la reprise d’un contexte existant
- maintenir ACC.021 dans le périmètre *accès / lobby*

---

## 2. objets et invariants

### objets principaux
- **Joueur**
  - `id_joueur` (identité persistante)
  - `pseudo`
- **Session / contexte de reprise** (logique)
  - jeton ou identifiant de session
  - horodatage de dernière activité

### invariants attendus
- aucun nouvel `Joueur` n’est créé
- l’identité récupérée correspond à un joueur existant
- aucune table ni partie n’est implicitement jointe
- la connexion ne modifie pas l’état de jeu

---

## 3. flux et canaux

### flux nominal
```
Client
  → POST /api/sessions
    → service lobby
      → validation identité
      → restauration du contexte minimal
      → réponse de connexion
```

### caractéristiques
- synchronisme REST
- flux idempotent du point de vue métier
- aucune émission d’événement de jeu

---

## 4. procédés modernes utilisés (apport à l’architecture)

### séparation inscription / connexion
- ACC.011 = création d’identité
- ACC.021 = réutilisation contrôlée

### reprise explicite du contexte
- le système reconnaît l’utilisateur sans supposer
  ni table, ni partie, ni phase

### sécurité pragmatique
- périmètre volontairement restreint
- pas d’authentification lourde prématurée
- surface d’attaque limitée au lobby

👉 Apport clé à l’architecture :  
**la continuité d’usage est gérée sans coupler l’accès au jeu**.

---

## 5. implémentation réalisée (solution)

### services
- `services/lobby/app.py`
  - endpoint `POST /api/sessions`
- `services/lobby/services_lobby.py`
  - logique de récupération / validation
- `services/lobby/repositories_sql.py`
  - accès joueur existant

### schémas / contrats
- `services/lobby/schemas.py`
  - schéma de requête de connexion
  - schéma de réponse (joueur + contexte)

---

## 6. écarts : prévu / fait / revu

### prévu (architecture P251)
- connexion simple
- reprise d’un joueur existant
- aucune logique de jeu

### fait (implémentation)
- endpoint dédié
- validation explicite de l’identité
- réponse structurée pour la suite du parcours

### revu (apprentissages)
- nécessité de distinguer clairement
  *joueur inconnu* vs *joueur invalide*
- importance d’un message d’erreur explicite
- clarification du périmètre de sécurité acceptable

---

## 7. preuves

### tests
- `services/lobby/tests/test_connexion_joueur.py` (ou équivalent)

### scripts / outils
- `services/cli_cabinet/cabinet_cli.py`
  (commande ACC.021)

### observabilité
- logs de connexion lobby
- réponses HTTP (200 / 404 / 400)

---

## 8. valeur observable

### pour l’utilisateur
- retour rapide dans le système
- continuité de l’expérience

### pour l’équipe
- découplage clair entre accès et jeu
- simplification des activités ACC.111+
- base stable pour gestion multi-sessions ultérieure

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
- valeur utilisateur : 3/5
- réduction de risque : 3/5
- réduction de dette : 3/5
- accélération future : 4/5
- observabilité/testabilité : 3/5  
**total ≈ 16/25**

---

## 10. conclusion architecturale

ACC.021 confirme que :
- l’accès mérite un traitement architectural autonome
- la gestion de la continuité est une valeur en soi
- les procédés modernes permettent d’éviter
  une fausse sécurité ou un couplage prématuré
