# Contrat Journal — v1.1

## 1. objectif

Ce document définit le **contrat canonique des entrées de journal métier** produites par le moteur du jeu *Conseil des ministres*.

Il décrit :
- le **sens** des événements,
- leur **structure minimale stable**,
- et les règles garantissant leur **exploitation fiable** par les projections et l’UI.

Ce contrat est **moteur‑centric** et **indépendant de toute interface utilisateur**.

---

## 2. principes fondateurs

- le moteur **exprime l’intention**
- les projections **traduisent**
- l’UI **met en scène**

Aucune logique d’affichage, de déduction visuelle ou de comportement UI ne doit apparaître dans ce contrat.

---

## 3. structure générale

Une entrée de journal est un objet structuré, immuable, identifié de manière unique, et destiné à être projeté sans interprétation implicite.

---

## 4. champs obligatoires

### 4.1 `event_id`

Identifiant globalement unique.

**Règles**
- invariant en cas de retry
- utilisé pour :
  - idempotence
  - corrélation
  - déduplication

---

### 4.2 `occurred_at`

Date ISO‑8601.

**Sens**
- moment effectif de l’événement métier
- pas un horodatage technique différé

---

### 4.3 `message`

Texte lisible par un humain.

**Règles**
- porte le **sens principal**
- jamais technique brut
- jamais dépendant du contexte UI

---

## 5. `severity`

Niveau de gravité métier.

**Valeurs autorisées**
- `debug`
- `info`
- `warn`
- `error`

**Règles**
- `warn` et `error` signalent une anomalie fonctionnelle
- aucune règle d’affichage n’est définie ici

---

## 6. `category`

Catégorie fonctionnelle de l’événement.

**Exemples**
- `story` – narration
- `action` – action joueur ou système
- `phase` – transition d’état
- `system` – événement technique métier
- `hand` – cartes / main

**Usages**
- filtrage
- regroupement
- analytics

---

## 7. `scope`

Portée conceptuelle de l’événement.

**Valeurs typiques**
- `joueur`
- `table`
- `partie`
- `systeme`

⚠️ Le `scope` **n’est pas** la diffusion.

---

## 8. `actor`

Décrit l’origine de l’événement.

**Exemples**
```json
{ "type": "joueur", "joueur_id": "J000002" }
{ "type": "systeme" }
```

**Règles**
- optionnel
- informatif
- ne porte jamais le sens principal

---

## 9. `audience`

Décrit explicitement à qui l’événement est destiné.

**Exemples**
```json
{ "scope": "tous" }
{ "scope": "joueur", "joueur_id": "J000003" }
{ "scope": "table", "table_id": "T000001" }
```

**Règles**
- la diffusion est **explicite**
- aucune déduction implicite côté projection

---

## 10. `refs`

Références métier liées à l’événement.

**Exemples**
- `joueur_id`
- `carte_id`
- `programme_id`
- `partie_id`

**Usages**
- navigation
- enrichissement UI
- corrélation analytique

---

## 11. `meta`

Données additionnelles **non porteuses du sens principal**.

**Exemples**
- phase courante
- sous‑phase
- indicateurs techniques
- flags de debug

**Règles**
- jamais nécessaires pour comprendre le message
- peuvent évoluer sans casser le contrat

---

## 12. idempotence & stabilité

Une entrée de journal doit être :
- reproductible sans duplication visible
- stable face aux retries
- identifiable uniquement par `event_id`

---

## 13. règle d’or

> Le moteur exprime l’intention.  
> Les projections traduisent.  
> L’UI met en scène.

Toute tentative de logique d’affichage ou de comportement UI dans ce contrat constitue une **violation**.

---

## 14. relation avec l’UI

Ce contrat est projeté vers :
- `EntreeJournalDTO`
- `journal_recent[]` dans `SituationJoueurDTO`

Toute simplification UI est une **projection**, jamais une perte d’intention moteur.

---
