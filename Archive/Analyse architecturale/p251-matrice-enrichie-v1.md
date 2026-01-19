# matrice enrichie p251 → solution (v1)

Ce document établit le lien entre les **activités P251**, l’**intention d’architecture**, et leur **réalisation concrète** dans la solution.
Il sert à :
- apprendre à l’architecture ce que les procédés modernes apportent,
- préparer un barème travail / valeur pour les prochains défis.

---

## légende des colonnes

- **intention** : ce que l’architecture projette (but, promesse)
- **objets & invariants** : objets métier concernés et règles fondamentales
- **flux & canaux** : REST, événements, commandes, topics
- **contrats** : schémas, DTO, payloads, versioning
- **procédés modernes** : event-driven, BRE, contrats, projections, outillage
- **implémentation** : services, modules, fichiers
- **preuves** : tests, scripts, logs, endpoints
- **écarts** : prévu / fait / revu (à compléter)

---

## matrice globale

| code p251 | intention | objets & invariants | flux & canaux | contrats | procédés modernes | implémentation | preuves | écarts |
|---|---|---|---|---|---|---|---|---|
| ACC.011 | inscrire un utilisateur au lobby | Joueur unique, id stable | REST lobby | schemas lobby | séparation accès / domaine | services/lobby/app.py, domaine.py | tests lobby, CLI | à documenter |
| ACC.021 | connecter un utilisateur reconnu | session / reprise | REST lobby | schemas lobby | gestion explicite de la reprise | services/lobby/app.py | tests | à documenter |
| ACC.111 | gérer les tables | Table, sièges uniques | REST lobby | schemas lobby | bounded context lobby | services/lobby/* | tests lobby | à documenter |
| ACC.115 | prêt et lancement | tous prêts, autorité | REST → événement | event PartieLancee | REST → event | lobby + kafka | logs, tests | à documenter |
| CAB.A101 | créer une partie | Partie, Etat initial | event → command | enveloppe commande | orchestration event-driven | adapter-evenements, commande_moteur | logs kafka | à documenter |
| CAB.B103 | décider la sous-phase | Etat → décision | API moteur → BRE | facts-contract v1 | BRE versionné | api_moteur, rules-service | tests BRE | à documenter |
| CAB.D001 | appliquer les commandes | Command atomique | commandes internes | modèle Command | moteur d’effets | moteur/etat.py | scénarios | à documenter |
| CAB.D101 | maj axes / économie | Axe clampé, éco cohérente | commandes axes.*, eco.* | config skin | catalogue d’opérations | moteur + skins | fixtures | à documenter |
| CAB.D300 | gérer le programme | Programme cohérent | commandes programme.* | config skin | projection-friendly | moteur/etat.py | tests | à documenter |
| CAB.D400 | gérer événements | événement appliqué une fois | evt.*, deck.* | config skin | séparation événement/programme | moteur/etat.py | logs | à documenter |
| CAB.D500 | valider usage carte | carte jouable, coût payé | moteur → BRE | contrat D500 | validation externalisée | rules-service | tests | à documenter |

---

## gabarit d’analyse détaillée (par activité)

À utiliser pour ACC.011, ACC.111, CAB.A101, etc.

### activité : <code p251>

**promesse d’architecture**  
<ce que P251 projetait>

**objets & invariants**  
- objet :
- invariant :

**flux & canaux**  
- source →
- transformation →
- destination →

**procédés modernes utilisés**  
- ce que la technique apporte à l’architecture

**implémentation réalisée**  
- services :
- fichiers clés :

**écarts**
- prévu :
- fait :
- revu :

**preuves**
- tests :
- scripts :
- endpoints :

**valeur observable**
- pour l’utilisateur :
- pour l’équipe :

---

## usage recommandé

1. compléter la colonne « écarts » dans la matrice
2. produire 2–3 fiches détaillées
3. utiliser ces fiches pour calibrer le barème travail / valeur
