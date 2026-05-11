# Contrat Journal — v1.1

## 1. Objectif

Ce document définit le contrat canonique du journal exposé à l’UI via :

- `SituationJoueurDTO.journal_recent[]`
- `EntreeJournalDTO`
- `contrats/jsonschema/http/ui_etat_joueur/EntreeJournalDTO.schema.json`

Le journal est une projection par joueur. Le moteur et les workers peuvent produire des événements plus riches, mais la forme contractuelle consommée par l’UI est celle de `EntreeJournalDTO`.

## 2. Principe

- Le moteur exprime l’intention métier.
- `ui_etat_joueur` normalise et projette les entrées.
- L’UI affiche et classe les entrées sans inventer de logique métier.

Le contrat public est volontairement réduit et stable.

## 3. Structure Canonique

```json
{
  "event_id": "E-001",
  "occurred_at": "2025-12-16T15:00:00Z",
  "category": "ACTION",
  "severity": "warn",
  "message": "Points d’attention insuffisants pour engager la carte.",
  "code": "programme.engager_carte.refusee",
  "meta": {
    "carte_id": "MES-004"
  },
  "audience": {
    "scope": "joueur",
    "joueur_id": "J000001"
  }
}
```

Champs requis par le schéma public :

- `occurred_at`
- `message`

Les autres champs sont optionnels, mais recommandés quand l’information existe.

## 4. Champs

### `event_id`

Identifiant stable de l’événement ou de l’entrée projetée.

Règles :
- stable en cas de retry ou rediffusion ;
- utilisé pour déduplication, corrélation et effets UI ponctuels ;
- optionnel dans le schéma, mais fortement recommandé.

### `occurred_at`

Date ISO 8601 de l’événement métier ou de sa projection.

Règles :
- champ canonique ; ne pas utiliser `timestamp` dans le contrat UI ;
- toujours exposé comme date sérialisée ;
- normalisé côté projection pour éviter les dates naïves.

### `message`

Texte court lisible par un humain.

Règles :
- porte le sens principal ;
- pas de HTML ;
- pas de message technique brut.

### `category`

Catégorie fonctionnelle normalisée par `ui_etat_joueur`.

Valeurs publiques utilisées aujourd’hui :

- `DEROULEMENT`
- `ACTION`
- `SYSTEME`
- `TECH`
- `MESSAGE`

Si une catégorie inconnue arrive, la projection la normalise, par défaut vers `TECH` ou selon le `op_code`.

### `severity`

Gravité normalisée par `ui_etat_joueur`.

Valeurs publiques utilisées aujourd’hui :

- `info`
- `warn`
- `error`

Normalisations connues :

- `warning` → `warn`
- `err`, `fatal` → `error`
- `ok`, `passed`, valeur absente ou inconnue → `info`

### `code`

Code métier optionnel de l’entrée.

Exemples :

- `action.attente.ouverte`
- `phase.tour`
- `programme.engager_carte.refusee`

Le code sert à corréler une entrée avec une opération métier sans surcharger `message`.

### `meta`

Objet libre pour données complémentaires non porteuses du sens principal.

Règles :
- ne remplace jamais `message` ;
- peut contenir des références métier (`carte_id`, `partie_id`, `op`, etc.) ;
- doit rester tolérant à l’évolution.

### `audience`

Audience stockée avec l’entrée projetée.

Le journal étant stocké par joueur, l’audience exposée doit être :

```json
null
```

ou :

```json
{ "scope": "joueur", "joueur_id": "J000001" }
```

Une diffusion globale interne (`all`) ou une liste de destinataires doit être convertie en entrées par joueur avant stockage dans `journal_recent`.

Invariant :

- une entrée stockée dans le journal de `J000001` ne doit pas exposer `audience.joueur_id = J000002` ;
- une entrée stockée dans un journal joueur ne doit pas exposer `audience.scope = "all"`.

## 5. Ce Qui N’est Pas Canonique

### `timestamp`

Ancien nom ou champ de transport. Le contrat UI utilise `occurred_at`.

### `kind`

`kind` est une notion UI dérivée pour classer l’affichage (`story`, `action`, `phase`, `system`, etc.). Elle n’est pas exposée par `EntreeJournalDTO`.

L’UI peut la déduire depuis `category`.

### `payload` et `ui`

Ces champs ne font pas partie du contrat public `EntreeJournalDTO`.

- les données complémentaires vont dans `meta` ;
- les décisions d’affichage restent côté UI, principalement à partir de `category`, `severity`, `code` et `meta`.

## 6. Règles De Projection

Le service `ui_etat_joueur` garantit :

- ordre chronologique ascendant de `journal_recent` ;
- limite de taille du journal récent ;
- normalisation de `severity` ;
- normalisation de `category` ;
- cohérence de `audience` avec le joueur destinataire.

## 7. Relation Avec L’UI

L’UI consomme `journal_recent[]` tel quel.

Elle peut :

- afficher `message` ;
- utiliser `severity` pour les alertes ou toasts ;
- utiliser `category` pour classer les onglets ;
- utiliser `event_id` pour éviter les doublons ;
- utiliser `meta` pour enrichir l’affichage.

Elle ne doit pas inventer d’événements, ni inférer une action métier absente des contrats.

## 8. Règle D’or

> Le moteur exprime l’intention.  
> La projection normalise.  
> L’UI met en scène.

Toute donnée nécessaire à la compréhension de l’entrée doit être présente dans `message`, `category`, `severity`, `code` ou `meta`, jamais seulement dans une heuristique d’affichage.
