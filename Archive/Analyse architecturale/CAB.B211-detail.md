# CAB.B211 — détermination des actions disponibles pour le joueur

## 1. promesse d’architecture (P251)

Déterminer, pour un joueur donné et un état donné,  
**quelles actions sont effectivement disponibles**,  
sans exposer les règles internes ni surcharger l’interface utilisateur.

**Intention P251**
- transformer une décision abstraite en possibilités concrètes
- adapter les actions au contexte (phase, rôle, contraintes)
- maintenir l’UI comme simple consommatrice

CAB.B211 introduit la **notion d’action disponible comme produit de la décision**.

---

## 2. objets et invariants

### objets principaux
- **Decision**
  - issue de CAB.B103 (sous-phase, intentions)
- **ActionDisponible**
  - identifiant stable
  - libellé
  - conditions satisfaites
  - paramètres requis
- **ContexteJoueur**
  - rôle
  - ressources disponibles
  - état local (cartes, attention, etc.)

### invariants attendus
- une action proposée est **réalisable immédiatement**
- aucune action impossible ne doit être exposée
- la liste est cohérente avec la sous-phase courante
- les règles restent centralisées côté décision

---

## 3. flux et canaux

### flux nominal
```
Etat + Contexte joueur
  → décision (CAB.B103)
    → filtrage / adaptation
      → liste ActionsDisponibles
        → projection / UI
```

### caractéristiques
- calcul déterministe
- lecture seule
- dépendance forte aux décisions, faible au moteur

---

## 4. procédés modernes utilisés (apport à l’architecture)

### décision → affordances
- passage d’une règle abstraite à une action concrète
- réduction de la complexité côté interface

### centralisation de la logique
- les conditions d’activation sont évaluées hors UI
- évite la duplication de règles

### testabilité accrue
- une action disponible est testable comme résultat
- scénarios clairs “état → actions”

👉 Apport clé à l’architecture :  
**l’architecture décide, l’UI exécute**.

---

## 5. implémentation réalisée (solution)

### services
- `services/cabinet/moteur/regles_interfaces.py`
  - récupération des décisions enrichies
- `services/ui_etat_joueur/projection/`
  - transformation décisions → actions UI
- `services/ui_etat_joueur/domaine.py`
  - modèle ActionDisponible

### intégration
- dépendance directe à CAB.B103
- intégration naturelle dans CAB.A205 (projection)

---

## 6. écarts : prévu / fait / revu

### prévu (architecture P251)
- actions dérivées des règles
- UI sans logique métier

### fait (implémentation)
- actions construites à partir des décisions
- filtrage selon le contexte joueur

### revu (apprentissages)
- nécessité de nommer clairement les actions
- importance de messages explicites pour l’utilisateur
- vigilance face à la prolifération d’actions similaires

---

## 7. preuves

### tests
- tests de projection des actions
- scénarios “état donné → actions attendues”

### scripts / outils
- simulations de tour
- inspection de l’état projeté

### observabilité
- logs de décisions et d’actions proposées
- comparaison moteur / projection

---

## 8. valeur observable

### pour l’utilisateur
- clarté sur ce qu’il peut faire maintenant
- réduction de l’erreur et de la frustration

### pour l’équipe
- UI simplifiée
- règles concentrées en un seul endroit
- meilleure maintenabilité à long terme

---

## 9. contribution au barème (indicatif)

### complexité (travail)
- objets : 2/5
- flux : 2/5
- contrats : 3/5
- règles : 3/5
- projection : 4/5
- outillage : 2/5  
**total ≈ 16/30**

### valeur
- valeur utilisateur : 5/5
- réduction de risque : 4/5
- réduction de dette : 5/5
- accélération future : 5/5
- observabilité/testabilité : 4/5  
**total ≈ 23/25**

---

## 10. conclusion architecturale

CAB.B211 consolide un principe clé :
- le système ne dit pas seulement *ce qui est vrai*,
- il dit *ce qui est possible maintenant*.

En séparant décisions et actions disponibles,
l’architecture protège l’UI,
clarifie l’expérience utilisateur
et rend le jeu extensible sans explosion de complexité.
