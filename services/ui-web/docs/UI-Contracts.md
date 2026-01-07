
# UI Contracts – Documentation complète (Version réalignée 2025-12)

## 1. Introduction

Ce document définit les contrats formels entre :
- **le frontend Web (React)**  
- **le service ui-état-joueur**  
- **le moteur de jeu Cabinet**

Il constitue la référence centrale pour garantir la cohérence :
- des actions envoyées au backend,
- de l’interprétation des états du moteur,
- de la navigation automatique,
- du rendu des panneaux UI,
- des transitions robustes entre phases,
- du comportement en cas d’erreurs ou de situations limites.

---

## 2. Principes fondamentaux des contrats UI

### 2.1. Le frontend est strictement *réactif*
Il n’invente jamais :
- d’actions non fournies par `actions_disponibles`,
- d’interprétation de phase,
- de navigation non dictée par `ancrage`.

### 2.2. Aucune logique de jeu n’est dans le frontend
Tout comportement provient :
- du moteur (`/parties/{partie_id}/actions`)
- du service ui-état-joueur (`/ui/joueurs/{id}/situation`)

Le frontend affiche **ce qu’on lui dit**, et envoie **exactement les actions fournies**.

### 2.3. Un seul endpoint pour agir
Toute action utilisateur est transformée en :

```
POST /parties/{partie_id}/actions
```

Format générique :

```json
{
  "acteur": "J000001",
  "type_action": "programme.engager_carte",
  "donnees": {
    "carte_id": "MES-004"
  }
}
```

---

## 3. Structure complète de la situation (`ui-état-joueur`)

La situation envoyée au frontend :

```json
{
  "version": 1,
  "joueur_id": "J000001",
  "ancrage": { ... },
  "etat_partie": { ... },
  "actions_disponibles": [ ... ],
  "journal_recent": [ ... ],
  "marqueurs": { ... }
}
```

### 3.1. Propriété : `ancrage`

| type | description |
|------|-------------|
| `"libre"` | Joueur disponible, avant table |
| `"lobby"` | Joueur dans le lobby |
| `"table"` | Joueur dans une table |
| `"partie"` | Joueur dans une partie |

Exemples :

```json
{ "type": "lobby" }
```

```json
{ "type": "table", "table_id": "T000001" }
```

```json
{ "type": "partie", "partie_id": "P000001" }
```

### 3.2. Propriété : `etat_partie`

Exemple complet :

```json
{
  "phase": "PROGRAMME",
  "sous_phase": "ENGAGER",
  "tour": 2,
  "axes": { ... },
  "eco": { ... },
  "joueurs": [ ... ],
  "programme": { ... }
}
```

### 3.3. Propriété : `actions_disponibles`

C’est la pièce maîtresse du contrat.

Structure :

```json
{
  "code": "programme.engager_carte",
  "label": "Engager une carte",
  "payload": {
    "op": "programme.engager_carte",
    "fields": [
      { "name": "joueur_id", "domain": "joueur_id", "required": true },
      { "name": "carte_id", "domain": "carte_main", "required": true }
    ],
    "type_attente": "ENGAGER_CARTE",
    "ecran": "programme"
  }
}
```

### 3.4. Propriété : `journal_recent`

Le journal suit l’ordre chronologique ascendant.

```json
{
  "occurred_at": "...",
  "message": "Une décision est attendue : Vote sur le programme"
}
```

### 3.5. Propriété : `marqueurs`

Utilisé uniquement pour les pollings conditionnels du frontend.

---

## 4. Norme contractuelle : actions UI → backend

Le moteur n’accepte qu’un seul format générique :

```json
{
  "acteur": "J000001",
  "type_action": "<code provenant de actions_disponibles>",
  "donnees": { ... }
}
```

Le frontend **ne doit jamais inventer** de nouveaux champs.

---

## 5. Contrats de navigation

La navigation dépend strictement de :

- `ancrage.type`
- `etat_partie.phase`

### 5.1. Matrice officielle

| ancrage | phase | UI doit aller |
|---------|-------|----------------|
| libre | — | /lobby |
| lobby | — | /lobby |
| table | — | /tables/{table_id} |
| partie | active | /parties/{id} |
| partie | TERMINEE | ❌ ne pas rediriger automatiquement |

### 5.2. Règle importante (2025)
Le frontend **ne redirige jamais** vers la partie lorsque :

```
phase === "TERMINEE"
```

Cela corrige le problème où l’UI revenait en boucle sur la page de fin.

---

## 6. Contrats des écrans UI

### 6.1. GameLayout (desktop)

Le GameLayout reçoit :

```ts
{
  header,
  vueEtat,
  vueProgramme,
  vueActions,
  vueJournal,
  layoutMode: "auto" | "desktop" | "mobile"
}
```

Il décide l’affichage en fonction de :

- `layoutMode`
- `useBreakpoint()` (mobile réel ou non)

### 6.2. GameLayout (mobile)

Mobile = panneaux + TabBar interne.

---

## 7. Contrats du mode d’affichage (sidebar)

L’UI offre trois modes :

- `"auto"` → basé sur la taille réelle
- `"desktop"` → force le layout large
- `"mobile"` → force le layout panneaux

Ce choix ne modifie **jamais** le moteur : uniquement l’affichage UI.

---

## 8. Contrats de cohérence : situation → affichage

### 8.1. Si actions_disponibles est vide

L’UI ne doit **pas afficher d’actions**.

### 8.2. Si attente terminée

Aucun bouton lié à l’attente ne doit être visible.

### 8.3. Si phase = TERMINEE

- afficher FinPartiePage
- ne jamais réinterpréter `actions_disponibles`
- ne pas rediriger automatiquement
- afficher bouton “Retour au lobby”

---

## 9. Exemples normatifs

### 9.1. Engager une carte

`actions_disponibles` :

```json
{
  "code": "programme.engager_carte",
  "payload": {
    "op": "programme.engager_carte",
    "fields": [
      { "name": "joueur_id", "required": true },
      { "name": "carte_id", "required": true }
    ]
  }
}
```

UI → moteur :

```json
{
  "acteur": "J000001",
  "type_action": "programme.engager_carte",
  "donnees": {
    "joueur_id": "J000001",
    "carte_id": "MES-004"
  }
}
```

---

### 9.2. Retour au lobby depuis fin de partie

UI :

```
navigate("/lobby")
```

Aucune redirection moteur après.

---

## 10. Cas limites couverts par le contrat

- Joueur recharge la page → l’affichage doit redevenir correct automatiquement
- Attente expirée → aucune action ne doit rester affichée
- Désynchronisation → polling force la correction
- Moteur envoie une action invalide → l’UI la masque automatiquement
- Joueur quitte la table → suppression immédiate de `ancrage.partie_id`

---

## 11. Conclusion générale

Ce document constitue la **spécification contractuelle centrale** de l’UI Cabinet.  
Il garantit :

- la cohérence des flux UI,
- la robustesse de la navigation,
- la compatibilité moteur ↔ ui-état ↔ frontend,
- la facilité future d’évolution (spectateur, replay, mobile natif).

Toute extension de l’interface doit se conformer strictement à ce document.
