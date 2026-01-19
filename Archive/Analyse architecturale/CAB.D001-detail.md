# CAB.D001 — application des commandes (moteur d’effets)

## 1. promesse d’architecture (P251)

Appliquer une liste de **commandes** sur l’état de la partie  
de manière déterministe, complète et traçable,  
en garantissant la cohérence du jeu et la reproductibilité.

**Intention P251**
- exécuter les effets décidés (règles, actions, événements)
- structurer l’exécution en opérations stables (catalogue d’op)
- produire un résultat observable (événements / projection / journal)

CAB.D001 est le **cœur mécanique** : là où toute la valeur devient réalité.

---

## 2. objets et invariants

### objets principaux
- **Etat**
  - source de vérité du jeu
  - contient axes, économie, decks, programme, joueurs, marqueurs, etc.
- **Commande**
  - `op` (ex. `axes.delta`, `programme.ajouter`, `evt.resoudre`, etc.)
  - paramètres
  - `meta` (cause, version, trace)
- **Résultat d’application**
  - nouvel état
  - journal d’événements internes (si présent)
  - indicateurs de fin (partie terminée, raison, etc.)

### invariants attendus
- exécution **déterministe** à entrée identique
- application **atomique** par commande (succès ou erreur explicite)
- absence d’effets de bord externes
- maintien des invariants domaine (bornes des axes, cohérence économie, etc.)
- traçabilité : on peut dire *quelles commandes ont produit quel effet*

---

## 3. flux et canaux

### flux nominal (vue système)
```
Décision / Validation (CAB.B103, B351)
  → Commandes
    → CAB.D001 (moteur)
      → Etat muté
        → Evénements publiés / projection (CAB.A205)
```

### flux interne (boucle d’exécution)
```
liste_commandes
  → pour chaque commande:
      - valider op + params (syntaxe)
      - router vers le handler (famille Dxxx)
      - appliquer mutation sur Etat
      - enregistrer trace / journal
  → vérifier fins de phase / fin de partie
```

### caractéristiques
- exécution purement locale (pas d’appels réseau)
- structure orientée “catalogue d’opérations”
- support naturel du replay (si trace conservée)

---

## 4. procédés modernes utilisés (apport à l’architecture)

### moteur d’effets à base de commandes
- l’exécution est découplée des règles
- permet plusieurs producteurs de commandes (BRE, cartes, événements)

### catalogue d’opérations versionnable
- `op` est un vocabulaire stable
- réduit la dette de couplage
- rend les projections plus simples (catégories Dxxx)

### traçabilité et reproductibilité
- chaque commande peut porter sa cause (event_id, decision_id, etc.)
- permet debug, replay, tests de non-régression

👉 Apport clé à l’architecture :  
**une exécution simple, stable, testable — même dans un système distribué**.

---

## 5. implémentation réalisée (solution)

### cœur du moteur
- `services/cabinet/moteur/etat.py`
  - méthode d’application des commandes (`appliquer_commandes` ou équivalent)
  - gestion des opérations `axes.*`, `eco.*`, `programme.*`, `evt.*`, `deck.*`, etc.

### structuration des événements / opérations
- `services/cabinet/moteur/events.py`
  - familles d’opérations (D100, D200, D300, D400, D500…)
  - catégories de consommation (utile projection)

### entrée système (orchestration)
- `services/commande_moteur/worker_moteur.py`
  - réception `cab.commands`
  - appel à l’API moteur → exécution → retour

---

## 6. écarts : prévu / fait / revu

### prévu (architecture P251)
- moteur d’effets central
- exécution par opérations stables
- cohérence et fin de partie gérées ici

### fait (implémentation)
- application de commandes sur un `Etat` structuré
- opérations déjà cataloguées par familles
- base solide pour projection par événements/catégories

### revu (apprentissages)
- nécessité d’une gestion stricte des erreurs de commande
- importance de la traçabilité “cause → effets”
- besoin de tests de replay / non-régression (golden traces)

---

## 7. preuves

### tests
- tests unitaires du moteur (handlers d’opérations)
- tests de scénarios (séquences de commandes)
- tests rules-service + moteur (contrat bout-en-bout)

### scripts / outils
- `eval.sh` (expérimental) pour smoke
- scripts de bootstrap topics Kafka
- scénarios CLI de partie

### observabilité
- logs du moteur sur application de commandes
- traces d’opérations (si conservées)
- état projeté cohérent en UI

---

## 8. valeur observable

### pour l’utilisateur
- le jeu avance de manière cohérente
- les effets attendus se produisent
- les erreurs sont rares et explicables

### pour l’équipe
- centre de gravité unique pour la cohérence
- possibilité de rejouer et déboguer rapidement
- base pour multi-skins et évolution continue

---

## 9. contribution au barème (indicatif)

### complexité (travail)
- objets : 5/5
- flux : 3/5
- contrats : 3/5
- règles : 1/5
- projection : 3/5
- outillage : 3/5  
**total ≈ 18/30**

### valeur
- valeur utilisateur : 5/5
- réduction de risque : 5/5
- réduction de dette : 5/5
- accélération future : 5/5
- observabilité/testabilité : 5/5  
**total ≈ 25/25**

---

## 10. conclusion architecturale

CAB.D001 est le point où :
- les décisions deviennent des mutations,
- les intentions deviennent des conséquences,
- l’architecture devient une mécanique fiable.

Si CAB.A101 est la porte du jeu
et CAB.B103 la raison du jeu,
CAB.D001 est la **physique du jeu**.

La qualité de CAB.D001 conditionne directement :
- la vitesse d’ajout de nouveaux skins,
- la stabilité des projections,
- la robustesse du système distribué.
