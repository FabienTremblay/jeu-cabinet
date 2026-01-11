
# Flux Auth → Lobby → Table → Jeu → Fin (Version complète — Documentation Officielle)

Sources de vérité contractuelles :
- OpenAPI Lobby : `contrats/openapi/lobby.openapi.json`
- OpenAPI API Moteur : `contrats/openapi/api_moteur.openapi.json`
- OpenAPI UI État Joueur : `contrats/openapi/ui_etat_joueur.openapi.json`
- JSON Schema UI : `contrats/jsonschema/http/ui_etat_joueur/`

## 1. Introduction

Ce document décrit l’ensemble du flux opérationnel vécu par un joueur dans l’application Cabinet : authentification, navigation entre le lobby, les tables, les parties, le déroulement complet du jeu, et la fin de partie. Il s’agit de la référence officielle pour les équipes frontend, backend et design.

---

## 2. Architecture conceptuelle

Le flux s’appuie sur trois services synchronisés :

- **UI (React)** : affiche la situation et envoie des actions via `/parties/{id}/actions`
- **ui-état-joueur** : calcule l’ancrage, fournit les actions disponibles, le journal, et l’état affichable
- **Moteur** : applique les règles et modifie l’état de la partie

Communication :

```
UI → ui-état-joueur → moteur → ui-état-joueur → UI
```

Le frontend ne déduit rien : il réagit à la situation renvoyée par ui-état-joueur.

---

## 3. Authentification → Lobby

### 3.1. Authentification

Après login :

```json
{
  "version": 1,
  "joueur_id": "J000001",
  "ancrage": { "type": "libre" },
  "etat_partie": null,
  "actions_disponibles": []
}
```

L’UI se base uniquement sur `ancrage.type === "lobby"` pour afficher l’écran Lobby.

---

### 3.2. Lobby

Le joueur voit les tables existantes, peut :

- créer une table
- rejoindre une table
- consulter son profil

Le service renvoie :

```json
{
  "ancrage": { "type": "lobby" },
  "etat_partie": null
}
```

Action possible : rejoindre une table → l’ancrage devient :

```json
"ancrage": { "type": "table", "table_id": "T000001" }
```
Le champ table_id correspond à AncrageDTO.table_id.
---

## 4. Table → Pré-partie → Démarrage

Dans l’écran de table, les joueurs marquent leur statut *Prêt*.

Exemple :

```json
{
  "ancrage": { "type": "table", "table_id": "T000001" },
  "actions_disponibles": [
    { "code": "table.pret" },
    { "code": "table.demarrer_partie" }
  ]
}
```

Une fois tous prêts, l’hôte peut démarrer.

Le moteur crée une nouvelle partie :

```
partie_id = "P000001" (généré par l’API moteur)
```

→ ancrage devient :

```json
"ancrage": { "type": "partie", "partie_id": "P000001" }
```

UI redirige : `/parties/P000001`

---

## 5. Déroulement complet d’une partie

Toutes les phases décrites ci-dessous sont **pilotées par les règles moteur** ; l’UI n’encode aucune logique métier.

### 5.1. Structure d’un tour

Chaque tour suit :

1. Confection du programme  
2. Vote  
3. Perturbations  
4. Fin de tour  

Ces phases peuvent inclure des attentes et perturbations.

---

### 5.2. Phase : Confection du programme

Actions :

```json
{
  "actions_disponibles": [
    {
      "code": "programme.engager_carte",
      "payload": { "op": "programme.engager_carte", ... }
    },
    {
      "code": "attente.joueur_recu",
      "payload": { "op": "attente.joueur_recu", ... }
    }
  ]
}
```

Le moteur attend que tous aient joué → `type_attente = "ENGAGER_CARTE"`.

---

### 5.3. Phase : Vote

Structure identique :

- bouton voter
- bouton terminer sa participation

Attente jusqu’à ce que tous aient voté.

---

### 5.4. Phase : Perturbations

Actions immédiates jouables :

- cartes d’influence
- interruptions
- passer son tour

---

### 5.5. Fin de tour

État retourné :

```json
{ "phase": "tour", "tour": 2 }
```

Le cycle recommence.

---

## 6. Actions envoyées par l’UI

Toujours :

Conforme au contrat `RequeteAction.schema.json`.

```
POST /parties/{partie_id}/actions
```

Exemple :

```json
{
  "acteur": "J000001",
  "type_action": "joueur.jouer_carte",
  "donnees": { "carte_id": "MES-004" }
}
```

Toutes les actions UI sont transformées en cette forme unique.

---

## 7. Navigation : ancrage + auto-redirection

La navigation est *réactive* :

| ancrage | phase | destination UI |
|---------|-------|----------------|
| lobby | — | /lobby |
| table | — | /tables/T000001 |
| partie | en cours | /parties/P000001 |
| partie | TERMINEE | ❌ ne pas rediriger automatiquement |

### Correction importante (2025)

> Le frontend **ne doit plus auto-rediriger vers la partie**
> lorsque `etat_partie.phase === "TERMINEE"`.

Cela évite la boucle vers la page de victoire.

---

## 8. Fin de partie

### 8.1. État renvoyé :

```json
{
  "ancrage": { "type": "partie", "partie_id": "P000001" },
  "etat_partie": { "phase": "TERMINEE" },
  "actions_disponibles": []
}
```

L’UI affiche :

- le palmarès
- les scores
- les capitaux
- un bouton “Retour au lobby”

---

### 8.2. Retour au lobby

UI fait :

```
navigate("/lobby")
```

Le polling *ne rebascule plus* vers la partie.

---

## 9. Cas particuliers

### 9.1. Reconnexion pendant une attente

Le service renvoie la situation exacte :

- attentes
- actions disponibles
- cartes engagées
- programme en cours

→ L’UI reconstruit l’état sans garder de logique locale.

---

### 9.2. Déconnexion — aucun impact moteur

La partie continue sans lui.

---

### 9.3. Fin forcée

Le moteur peut forcer la fin :

```
"message": "Partie terminée : Fin forcée"
```

UI doit afficher la page de fin, sans actions disponibles.

---

## 10. Diagramme du flux

```
[AUTH] 
   ↓
[LOBBY]
   ↓ rejoindre
[TABLE]
   ↓ démarrer
[PARTIE]
   ↳ Programme
   ↳ Vote
   ↳ Perturbations
   ↳ Nouveau tour
   (répéter)
   ↓
[FIN DE PARTIE]
   ↓
[LOBBY]
```

---

## 11. Conclusion

Ce flux est la spécification officielle pour :

- les comportements UI,
- les transitions backend,
- la synchronisation moteur/ui-état-joueur,
- le développement d’extensions (mobile, TUI, multi-plateforme).

Ce document doit être utilisé comme référence centrale pour toute évolution du jeu Cabinet.

