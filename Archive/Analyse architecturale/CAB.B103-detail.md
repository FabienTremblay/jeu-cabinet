# CAB.B103 — obtention de la règle de sous-phase (décision)

## 1. promesse d’architecture (P251)

Déterminer, à partir de l’état courant de la partie,  
**quelle sous-phase doit s’appliquer et quelles actions deviennent possibles**,  
sans coder cette logique directement dans le moteur.

**Intention P251**
- externaliser la décision
- rendre la logique de phase explicite, versionnable et testable
- préparer la boucle décision → commandes → effets

CAB.B103 introduit la **décision comme objet architectural**.

---

## 2. objets et invariants

### objets principaux
- **Etat**
  - phase courante
  - sous-phase courante
  - tour, journée, contexte global
- **DecisionSousPhase**
  - sous-phase résultante
  - liste d’actions / commandes proposées
- **Règle**
  - versionnée
  - indépendante du moteur

### invariants attendus
- une décision est **pure** (pas d’effet de bord)
- la même entrée produit la même sortie
- aucune mutation de l’état n’a lieu lors de la décision
- le moteur reste ignorant des règles internes

---

## 3. flux et canaux

### flux nominal
```
Etat (moteur)
  → appel décision
    → rules-service (BRE)
      → décision sous-phase
        → moteur
```

### caractéristiques
- appel synchrone (API REST)
- contrat explicite de facts
- réponse structurée (décision)

---

## 4. procédés modernes utilisés (apport à l’architecture)

### BRE (Business Rules Engine)
- logique déclarative
- séparation règles / exécution
- versioning indépendant du code

### contrat de facts
- l’état est **traduit**, pas exposé directement
- réduction du couplage structurel

### décision comme artefact
- testable isolément
- explicable
- remplaçable

👉 Apport clé à l’architecture :  
**la décision devient un composant de premier ordre, pas un `if/else`**.

---

## 5. implémentation réalisée (solution)

### moteur / api
- `services/cabinet/moteur/regles_interfaces.py`
  - interface `regle_sous_phase`
- `services/api_moteur/rules_client.py`
  - appel REST vers le rules-service

### rules-service
- `rules-service/src/main/java/...`
  - décisions de sous-phase
- `rules-service/src/main/resources/rules/...`
  - règles versionnées
- `rules-service/src/test/...`
  - tests de règles (fixtures)

### contrats
- `services/cabinet/skins/*/facts-contract-v1.schema.json`

---

## 6. écarts : prévu / fait / revu

### prévu (architecture P251)
- règles externes
- moteur centré sur l’exécution

### fait (implémentation)
- BRE Quarkus dédié
- interface claire moteur → règles
- contrats de facts versionnés

### revu (apprentissages)
- nécessité de figer tôt le vocabulaire des facts
- importance des tests de règles
- gestion explicite des versions de règles

---

## 7. preuves

### tests
- `rules-service/...Test.java`
- fixtures JSON de décision

### scripts / outils
- scripts de smoke test décision
- appels curl via api_moteur

### observabilité
- logs rules-service
- traçage version de règle utilisée

---

## 8. valeur observable

### pour l’utilisateur
- comportement cohérent des phases
- actions disponibles compréhensibles

### pour l’équipe
- modification des règles sans toucher au moteur
- réduction massive du risque de régression
- meilleure explicabilité du jeu

---

## 9. contribution au barème (indicatif)

### complexité (travail)
- objets : 2/5
- flux : 2/5
- contrats : 4/5
- règles : 4/5
- projection : 2/5
- outillage : 2/5  
**total ≈ 16/30**

### valeur
- valeur utilisateur : 4/5
- réduction de risque : 5/5
- réduction de dette : 5/5
- accélération future : 5/5
- observabilité/testabilité : 5/5  
**total ≈ 24/25**

---

## 10. conclusion architecturale

CAB.B103 marque l’instant où :
- la logique quitte définitivement le moteur
- l’architecture assume la **décision comme service**
- les procédés modernes (BRE, contrats, tests)
  produisent plus de valeur que du code impératif

C’est l’un des meilleurs leviers de projection à long terme du projet.
