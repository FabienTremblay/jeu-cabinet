# CAB.A205 — préparation et publication de l’état projeté aux joueurs

## 1. promesse d’architecture (P251)

Rendre visible aux joueurs **un état compréhensible et exploitable** de la partie,  
sans exposer directement l’état interne du moteur,  
et sans coupler l’interface utilisateur aux décisions ou aux règles.

**Intention P251**
- séparer l’état interne du moteur de l’état perçu par les joueurs
- permettre plusieurs projections à partir d’une même source
- préparer l’UI à consommer des vues stables et évolutives

CAB.A205 introduit la **projection comme responsabilité architecturale explicite**.

---

## 2. objets et invariants

### objets principaux
- **EtatInterne**
  - état complet du moteur (non exposé)
- **EtatProjeté**
  - phase, sous-phase
  - actions disponibles
  - informations pertinentes pour le joueur
- **ProjectionJoueur**
  - vue filtrée selon le rôle / le contexte

### invariants attendus
- l’état projeté est **dérivé**, jamais source de vérité
- aucune mutation de l’état interne n’est possible via la projection
- un même état interne peut produire plusieurs projections
- la projection est cohérente avec les décisions courantes

---

## 3. flux et canaux

### flux nominal
```
Etat interne (moteur)
  → préparation projection
    → publication / exposition
      → consommation UI / clients
```

### caractéristiques
- calcul déterministe
- pas de logique métier lourde
- consommation en lecture seule

---

## 4. procédés modernes utilisés (apport à l’architecture)

### read-model / projection
- application du pattern CQRS
- séparation claire écriture / lecture

### découplage UI ↔ moteur
- l’UI ne connaît ni les règles ni les commandes
- elle consomme une vue stabilisée

### extensibilité naturelle
- nouvelles projections possibles sans modifier le moteur
- adaptation multi-clients (web, mobile, CLI)

👉 Apport clé à l’architecture :  
**l’état devient interprétable sans devenir manipulable**.

---

## 5. implémentation réalisée (solution)

### services
- `services/ui_etat_joueur/`
  - consommateurs d’événements
  - construction de l’état projeté
- `services/ui_etat_joueur/projection/`
  - logique de transformation état → vue
- `services/ui_etat_joueur/repository.py`
  - persistance éventuelle de la projection

### intégration
- consommation des événements du moteur
- exposition via API REST dédiée à l’UI

---

## 6. écarts : prévu / fait / revu

### prévu (architecture P251)
- séparation claire moteur / interface
- vues adaptées aux joueurs

### fait (implémentation)
- micro-service de projection dédié
- logique de transformation isolée

### revu (apprentissages)
- importance de la granularité des événements
- nécessité de classer les événements par catégories
- attention à la dérive vers un “mini-moteur” côté projection

---

## 7. preuves

### tests
- tests unitaires des projections
- tests de consommation d’événements

### scripts / outils
- scénarios de simulation de partie
- appels API `ui_etat_joueur`

### observabilité
- logs de consommation d’événements
- cohérence visible entre moteur et UI

---

## 8. valeur observable

### pour l’utilisateur
- compréhension claire de la situation de jeu
- actions disponibles explicites

### pour l’équipe
- liberté d’évolution de l’UI
- réduction du couplage et des régressions
- base solide pour l’analytique et le replay

---

## 9. contribution au barème (indicatif)

### complexité (travail)
- objets : 3/5
- flux : 3/5
- contrats : 3/5
- règles : 1/5
- projection : 5/5
- outillage : 2/5  
**total ≈ 17/30**

### valeur
- valeur utilisateur : 5/5
- réduction de risque : 4/5
- réduction de dette : 5/5
- accélération future : 5/5
- observabilité/testabilité : 5/5  
**total ≈ 24/25**

---

## 10. conclusion architecturale

CAB.A205 consacre un principe fondamental :
- le moteur calcule,
- la projection explique,
- l’interface consomme.

C’est cette séparation qui permet au projet :
- de croître sans rigidité,
- de supporter plusieurs interfaces,
- et de transformer l’état du jeu en véritable information.
