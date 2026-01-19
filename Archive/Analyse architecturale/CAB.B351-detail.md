# CAB.B351 — validation d’une action avant exécution (préconditions et coûts)

## 1. promesse d’architecture (P251)

Valider qu’une action demandée par un joueur est **légitime, applicable et payable**
avant toute mutation de l’état,  
en centralisant les règles de validation hors du moteur d’exécution.

**Intention P251**
- empêcher l’exécution d’actions invalides
- séparer la *validation* de l’*application*
- garantir des erreurs explicables et déterministes

CAB.B351 institue la **validation préalable** comme garde-fou architectural.

---

## 2. objets et invariants

### objets principaux
- **ActionDemandee**
  - identifiant d’action
  - paramètres fournis
- **ResultatValidation**
  - valide / invalide
  - raisons normalisées
  - coûts calculés
- **Cout**
  - type (attention, ressources, cartes, etc.)
  - montant
- **Decision**
  - contexte décisionnel issu de CAB.B103

### invariants attendus
- aucune action invalide n’est exécutée
- les coûts sont calculés **avant** l’exécution
- la validation est **pure** (pas d’effet de bord)
- les règles de validation sont centralisées

---

## 3. flux et canaux

### flux nominal
```
ActionDemandee (client)
  → validation (CAB.B351)
    → résultat (ok + coûts | refus + raisons)
      → (si ok) CAB.D001
```

### caractéristiques
- appel synchrone
- déterministe
- aucune mutation d’état

---

## 4. procédés modernes utilisés (apport à l’architecture)

### séparation validation / exécution
- évite les effets partiels
- simplifie le moteur d’effets

### règles externalisées
- validation déclarative (BRE)
- versioning indépendant

### erreurs explicables
- raisons structurées
- messages utilisateur cohérents

👉 Apport clé à l’architecture :  
**l’exécution devient sûre parce que la validation est formelle**.

---

## 5. implémentation réalisée (solution)

### moteur / interfaces
- `services/cabinet/moteur/regles_interfaces.py`
  - interface de validation d’action
- `services/api_moteur/rules_client.py`
  - appel au rules-service

### rules-service
- `rules-service/...`
  - règles de validation (préconditions, coûts)
- `rules-service/src/test/...`
  - tests de validation (fixtures)

### contrats
- requête validation `{ action_id, params, contexte }`
- réponse `{ valide, couts, raisons }`

---

## 6. écarts : prévu / fait / revu

### prévu (architecture P251)
- validation centralisée
- moteur protégé des actions invalides

### fait (implémentation)
- validation via BRE
- calcul des coûts avant exécution

### revu (apprentissages)
- importance de normaliser les raisons d’échec
- nécessité de distinguer *action interdite* vs *action impossible*
- gestion des coûts partiels et cumulés

---

## 7. preuves

### tests
- tests unitaires de validation d’action
- fixtures de coûts et refus

### scripts / outils
- appels curl de validation
- scénarios d’actions invalides

### observabilité
- logs de validation
- traçage des refus et des coûts

---

## 8. valeur observable

### pour l’utilisateur
- refus compréhensibles
- absence de comportements incohérents

### pour l’équipe
- moteur simplifié
- règles testables et versionnées
- réduction drastique des bugs d’état

---

## 9. contribution au barème (indicatif)

### complexité (travail)
- objets : 2/5
- flux : 2/5
- contrats : 4/5
- règles : 4/5
- projection : 1/5
- outillage : 2/5  
**total ≈ 15/30**

### valeur
- valeur utilisateur : 4/5
- réduction de risque : 5/5
- réduction de dette : 5/5
- accélération future : 4/5
- observabilité/testabilité : 5/5  
**total ≈ 23/25**

---

## 10. conclusion architecturale

CAB.B351 verrouille la chaîne décisionnelle :
- ce qui est possible (B211)
- ce qui est valide et payable (B351)
- ce qui peut être exécuté (D001)

Cette étape garantit que le moteur n’est jamais en situation ambiguë,
et que la cohérence du jeu repose sur des règles explicites et vérifiables.
