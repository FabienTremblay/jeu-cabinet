# contrat-journal.md (version 1.1)

## changelog

- **1.1 (2025-12-16)** : clarification de **audience** (diffusion) vs **scope/actor** (sens métier) + invariant “journal stocké par joueur”.
- **1.0** : version initiale.

---

## 1. objectif

Ce document définit le **contrat canonique des messages de journal** produits par le moteur du jeu *Conseil des ministres*.

Il vise à garantir que :
- les messages sont interprétés correctement par l’UI (journal, bandeau critique, flash),
- les intentions métier (information, alerte, narration, technique) sont respectées,
- les comportements UI restent stables malgré l’évolution du moteur.

Le moteur **ne décide pas de l’affichage**, mais **exprime clairement l’intention**.

---

## 2. principe fondamental

> **un message = une intention explicite**

Le moteur doit toujours produire des messages :
- auto-suffisants,
- idempotents,
- classifiables sans heuristique UI.

L’UI applique ensuite des règles simples et déterministes.

---

## 3. structure canonique d’un JournalEntry

```json
{
  "event_id": "evt-uuid",
  "timestamp": "2025-12-16T14:32:10Z",
  "tour": 3,
  "message": "Points d’attention insuffisants pour engager la carte.",
  "severity": "warn",
  "kind": "action",
  "category": "programme",
  "scope": "joueur",
  "actor": {
    "joueur_id": "J000001",
    "opposition": false
  },
  "refs": {
    "carte_id": "MES-004",
    "op": "programme.engager_carte",
    "evenement_id": null,
    "procedure_code": "ENGAGER_PROGRAMME",
    "aggregate_id": "P000001"
  },
  "payload": {
    "payload_version": 1
  },
  "ui": {
    "persist": true,
    "toast": true,
    "flash": false
  }
}
```

---

## 4. champs obligatoires

### 4.1 event_id (obligatoire)

- identifiant unique **stable**
- ne doit pas changer lors d’un retry ou d’une rediffusion
- utilisé par l’UI pour la déduplication (toast / flash)

---

### 4.2 timestamp

- ISO 8601
- horodatage du **commit métier**, pas du transport

---

### 4.3 tour

- numéro du tour concerné
- `null` si hors-tour (lobby, technique, système)

---

### 4.4 message

- texte court, lisible par un humain
- jamais de message technique brut
- pas de formatage HTML

---

## 5. severity (niveau de gravité)

Valeurs autorisées uniquement :

| valeur | sens |
|------|------|
| debug | diagnostic technique |
| info  | information / narration |
| warn  | action refusée attendue / contrainte métier |
| error | invariant brisé / bug / incohérence grave |

### règles
- `warn` et `error` déclenchent un **bandeau critique (toast)**
- `info` ne déclenche jamais d’alerte
- ne jamais utiliser `warn/error` pour créer du « drama narratif »
- **interdit** : `warning`, `critical`, `success`, etc. (à normaliser côté adapter si nécessaire)

---

## 6. kind (nature du message)

| kind | usage |
|-----|------|
| story | narration politique, événements, conséquences |
| action | actions joueurs (acceptées ou refusées) |
| phase | début/fin de tour, transitions |
| system | messages système ou règles |
| hand | information sur la main du joueur |

> le `kind` détermine **l’onglet du journal UI**

---

## 7. category (classification fine)

Libre mais recommandée.

Exemples :
- programme
- carte
- vote
- opposition
- axe
- eco
- regle
- reseau

Utilisée pour filtrage futur et analyse.

---

## 8. scope (portée métier)

| scope | signification |
|------|--------------|
| joueur | concerne un joueur précis |
| partie | concerne l’ensemble de la partie |
| table | concerne la table (lobby) |

> `scope` décrit **le sens métier** (à qui cela s’applique), pas la stratégie de stockage.

---

## 9. actor (acteur/sujet)

Indique **qui agit ou subit**.

```json
{
  "joueur_id": "J000002",
  "opposition": false
}
```

- `joueur_id` optionnel
- `opposition=true` si l’acteur est l’opposition

---

## 10. refs (références métier)

Permet à l’UI de contextualiser.

Champs usuels :
- `carte_id`
- `evenement_id`
- `op`
- `procedure_code`
- `aggregate_id`

### règle critique

> **un message avec `evenement_id` est éligible au Flash Une**

---

## 11. payload

- données complémentaires
- toujours versionnées (`payload_version`)
- jamais interprétées par défaut par l’UI

---

## 12. ui (directives explicites UI)

Optionnel mais fortement recommandé.

```json
"ui": {
  "persist": true,
  "toast": false,
  "flash": true
}
```

| champ | effet |
|------|------|
| persist | écrit dans l’historique de partie |
| toast | autorise affichage bandeau |
| flash | autorise affichage Flash Une |

> à défaut, l’UI applique ses règles par `severity` et `evenement_id`

---

## 13. audience (diffusion)

### 13.1 définition

`audience` n’est **pas** un champ du JournalEntry canonique.  
C’est un **champ interne/projection** (ex. `journal_recent` côté UI-état-joueur) qui indique **à qui le message a été diffusé**.

- `scope/actor` = **sens métier**
- `audience` = **ciblage de diffusion** (transport / notifications / duplication)

### 13.2 forme recommandée

```json
"audience": { "scope": "joueur", "joueur_id": "J000002" }
```

Scopes possibles (projection) :
- `joueur`
- `all`
- `liste` (si tu gardes cette variante)

### 13.3 invariant (important)

Si l’architecture stocke le journal **par joueur** (ex. `EtatJoueurUI.journal_recent`) :

- entrée stockée avec `joueur_id = J` ⇒ `audience` doit être `null` ou `{ "scope":"joueur", "joueur_id": J }`
- une audience globale (`all`) doit être **convertie** lors de la duplication (une entrée par joueur)

Objectif : éviter les incohérences du type “entrée du journal de J mais audience=all”.

---

## 14. règles de publication (résumé)

| cas | persist | toast | flash |
|----|---------|-------|-------|
| action refusée | oui | oui | non |
| action acceptée | oui | non | non |
| événement mondial | oui | selon gravité | oui |
| changement de phase | oui | non | non |
| message technique | non | non | non |

---

## 15. idempotence et retries

- un même événement métier doit conserver le même `event_id`
- les workers doivent être tolérants aux rediffusions
- aucun effet UI ne doit se répéter si `event_id` déjà vu

---

## 16. tests d’acceptation obligatoires

1. action refusée → journal + toast, pas de flash
2. événement mondial → journal + flash
3. fin de tour → journal uniquement
4. retry technique → aucun duplicat UI
5. diagnostic → visible uniquement en temps réel

---

## 17. règle d’or

> **le moteur exprime l’intention, l’UI met en scène**

Toute ambiguïté non résolue dans le moteur deviendra une incohérence UI.
