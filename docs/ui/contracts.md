# Contrats UI — Source Officielle

## 1. Rôle

Ce document définit les règles contractuelles transverses entre :

- `services/ui-web/` ;
- `services/ui_etat_joueur/` ;
- `services/api_moteur/` ;
- `services/lobby/`.

Il complète les contrats HTTP normatifs dans `contrats/` sans les remplacer.

Sources normatives :

- `contrats/openapi/lobby.openapi.json`
- `contrats/openapi/api_moteur.openapi.json`
- `contrats/openapi/ui_etat_joueur.openapi.json`
- `contrats/jsonschema/http/`

Documents complémentaires :

- parcours joueur : `docs/ui/flux-auth-lobby-table.md`
- journal : `docs/ui/journal.md`

## 2. Principes

Le frontend est réactif :

- il affiche la situation fournie par `ui_etat_joueur` ;
- il envoie les actions exposées par le backend ;
- il ne déduit pas de règle métier absente des contrats ;
- il ne crée pas d’action absente de `actions_disponibles`.

Le moteur et les règles restent propriétaires de la logique métier.

## 3. Situation Joueur

L’UI consomme principalement :

```http
GET /ui/joueurs/{joueur_id}/situation
```

La réponse suit `SituationJoueurDTO` :

```json
{
  "version": 1,
  "joueur_id": "J000001",
  "ancrage": {
    "type": "lobby",
    "table_id": null,
    "partie_id": null
  },
  "etat_partie": {
    "phase": null,
    "sous_phase": null,
    "tour": null
  },
  "actions_disponibles": [],
  "journal_recent": [],
  "marqueurs": {}
}
```

Le schéma public actuel définit `ancrage.type` avec les valeurs :

- `lobby`
- `table`
- `partie`

`table_id` est renseigné lorsque `type = "table"`.

`partie_id` est renseigné lorsque `type = "partie"`.

## 4. Actions Disponibles

L’UI ne doit proposer que les actions reçues dans `actions_disponibles`.

Structure contractuelle :

```json
{
  "code": "programme.engager_carte",
  "label": "Engager une carte",
  "payload": {},
  "requires_confirmation": false
}
```

Règles :

- `code` identifie l’action métier ;
- `label` peut être affiché ;
- `payload` contient les données nécessaires à l’action ;
- `requires_confirmation` indique si une confirmation UI est nécessaire.

## 5. Envoi D’action

Toutes les actions de jeu passent par :

```http
POST /parties/{partie_id}/actions
```

Format contractuel :

```json
{
  "acteur": "J000001",
  "type_action": "programme.engager_carte",
  "donnees": {
    "carte_id": "MES-004"
  }
}
```

Règles :

- `acteur` est l’identifiant du joueur courant ;
- `type_action` vient de `actions_disponibles[].code` ;
- `donnees` est construit à partir du `payload` et des choix explicites de l’utilisateur.

L’UI ne doit pas inventer de champ métier supplémentaire.

## 6. Navigation

La navigation dépend de `ancrage.type` et, en partie, de `etat_partie.phase`.

Matrice officielle :

| ancrage.type | phase | destination |
| --- | --- | --- |
| `lobby` | — | `/lobby` |
| `table` | — | `/tables/{table_id}` |
| `partie` | active | `/parties/{partie_id}` |
| `partie` | `TERMINEE` | ne pas rediriger automatiquement vers la partie |

Règles :

- une partie terminée doit permettre l’affichage de la page de fin ;
- l’UI ne doit pas reboucler vers `/parties/{partie_id}` lorsque `phase = "TERMINEE"` ;
- le retour au lobby est une action UI explicite.

## 7. Journal

Le journal exposé dans `journal_recent[]` suit `EntreeJournalDTO`.

Le contrat détaillé vit dans :

```text
docs/ui/journal.md
```

L’UI peut utiliser :

- `message` pour l’affichage ;
- `severity` pour les alertes ;
- `category` pour le classement ;
- `event_id` pour la déduplication ;
- `meta` pour l’enrichissement.

## 8. Marqueurs

`marqueurs` signale les sections qui ont changé.

Les marqueurs sont des aides de polling et de rafraîchissement. Ils ne portent pas de logique métier.

## 9. Layout UI

Les choix d’affichage (`desktop`, `mobile`, panneaux, onglets, sidebar) ne modifient jamais le moteur.

Ils peuvent dépendre :

- de la taille d’écran ;
- d’un réglage local d’affichage ;
- de la présence ou non de contenus dans les vues.

## 10. Documents Obsolètes

Les anciennes copies dans `services/ui-web/docs/` et `docs/ui/_from-services-ui-web/` ont été retirées pour éviter les doublons.

`Document/ui-contracts.md` reste un document de conception historique tant qu’il n’a pas été explicitement resynchronisé.

En cas de divergence :

1. `contrats/` prime pour les formats HTTP ;
2. ce document prime pour les règles UI transverses ;
3. `docs/ui/flux-auth-lobby-table.md` décrit le parcours ;
4. `docs/ui/journal.md` prime pour le journal.
