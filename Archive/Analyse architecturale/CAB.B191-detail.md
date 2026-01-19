# CAB.B191 — gestion et priorisation des intentions du joueur

## 1. promesse d’architecture (P251)

Permettre au joueur d’exprimer **des intentions structurées**  
qui orientent ses choix, ses priorités et ses actions,  
sans transformer ces intentions en règles exécutoires directes.

**Intention P251**
- distinguer l’intention de l’action
- rendre explicites les priorités du joueur
- influencer les décisions sans court-circuiter les règles

CAB.B191 introduit l’**intention comme signal architectural**, pas comme commande.

---

## 2. objets et invariants

### objets principaux
- **Intention**
  - identifiant
  - type (personnelle, stratégique, institutionnelle)
  - priorité
  - portée temporelle
- **EnsembleIntentions**
  - collection ordonnée d’intentions actives
- **ContexteDecisionnel**
  - état courant
  - intentions actives du joueur

### invariants attendus
- une intention n’entraîne **aucune mutation directe**
- plusieurs intentions peuvent coexister
- les intentions influencent les décisions, pas l’exécution
- l’ordre de priorité est explicite et stable

---

## 3. flux et canaux

### flux nominal
```
Joueur
  → déclaration / mise à jour intentions
    → stockage intentions
      → utilisation par CAB.B103 / CAB.B211
```

### caractéristiques
- flux déclaratif
- persistance légère
- aucune exécution immédiate

---

## 4. procédés modernes utilisés (apport à l’architecture)

### séparation intention / action
- évite la confusion volonté / effet
- protège le moteur d’une logique subjective

### influence douce des règles
- les intentions modulent les décisions
- elles ne remplacent jamais les règles

### explicabilité
- le système peut expliquer *pourquoi* une action est favorisée
- base pour IA ou assistants futurs

👉 Apport clé à l’architecture :  
**le système écoute les intentions sans leur obéir aveuglément**.

---

## 5. implémentation réalisée (solution)

### services
- `services/ui_etat_joueur/`
  - capture et gestion des intentions
- `services/cabinet/moteur/regles_interfaces.py`
  - passage des intentions au moteur de décision
- `rules-service/...`
  - prise en compte des intentions dans les règles

### contrats
- structure d’intention intégrée au facts-contract
- priorité et type explicités

---

## 6. écarts : prévu / fait / revu

### prévu (architecture P251)
- intentions comme méta-informations
- aucune logique impérative

### fait (implémentation)
- intentions intégrées au contexte décisionnel
- pondération des décisions

### revu (apprentissages)
- nécessité de limiter le pouvoir des intentions
- importance d’une typologie claire
- vigilance face à la dérive “script de stratégie”

---

## 7. preuves

### tests
- tests de décision avec intentions variées
- scénarios contradictoires

### scripts / outils
- simulations avec priorités différentes
- inspection des décisions résultantes

### observabilité
- logs de prise en compte des intentions
- traçage des arbitrages décisionnels

---

## 8. valeur observable

### pour l’utilisateur
- sentiment de contrôle stratégique
- cohérence entre objectifs et options proposées

### pour l’équipe
- enrichissement du moteur décisionnel sans complexifier l’exécution
- base solide pour IA, tutoriels, aides contextuelles

---

## 9. contribution au barème (indicatif)

### complexité (travail)
- objets : 3/5
- flux : 2/5
- contrats : 3/5
- règles : 3/5
- projection : 2/5
- outillage : 2/5  
**total ≈ 15/30**

### valeur
- valeur utilisateur : 5/5
- réduction de risque : 3/5
- réduction de dette : 4/5
- accélération future : 5/5
- observabilité/testabilité : 4/5  
**total ≈ 21/25**

---

## 10. conclusion architecturale

CAB.B191 introduit une couche rarement formalisée :
- ce que le joueur *veut*
- sans confondre avec ce que le système *fait*

En traitant l’intention comme un signal plutôt qu’un ordre,
l’architecture gagne en finesse,
en explicabilité
et en potentiel d’évolution à long terme.
