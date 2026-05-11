# Présence et session joueur

Ce document décrit le fonctionnement de la présence joueur et des sessions
lobby. Il fixe les invariants métier à préserver dans les évolutions futures.

## Problème traité

Le projet doit distinguer cinq notions proches mais différentes :

- le `joueur`, identité durable connue du lobby ;
- la `session`, lien technique temporaire entre le front et le lobby ;
- la présence, état observé à partir des heartbeats ;
- le siège à la table, relation métier entre une table et un `id_joueur` ;
- la participation à une partie, relation métier entre une partie et un
  `id_joueur`.

Un joueur peut disparaître techniquement sans abandonner sa place métier. Par
exemple, un onglet fermé, une panne réseau ou un appareil en veille doivent
faire expirer la session, mais ne doivent pas retirer automatiquement le joueur
de sa table ou de sa partie.

## Principe architectural

La session est jetable. Le joueur est durable.

Le siège est lié à `id_joueur`, pas à `id_session`. Une session expirée signifie
que le front doit se reconnecter. Elle ne signifie pas que le joueur abandonne
sa table, son siège ou sa partie.

Règles principales :

- l'expiration de session force une reconnexion ;
- l'expiration de session ne retire pas le joueur de sa table ;
- la reconnexion crée une nouvelle session ;
- la reconnexion peut retourner un `contexte_reprise` si le joueur est encore
  lié à une table active ou à une partie active.

Le lobby reste la source de vérité pour les tables, les sièges et le contexte de
reprise.

## Cycle nominal

Le front connecte un joueur par :

```http
POST /api/sessions
```

Le lobby vérifie les identifiants, invalide les anciennes sessions remplaçables
du joueur, puis crée une nouvelle session `active`.

La réponse contient `jeton_session`. Côté front, ce jeton est conservé comme
identifiant de session et envoyé sur les appels protégés.

Le front maintient ensuite la présence par heartbeat périodique :

```http
POST /api/sessions/{id_session}/heartbeat
```

Le heartbeat ne crée pas de nouvelle session. Il retrouve la session existante
par `id_session`, puis renouvelle :

- `dernier_heartbeat` ;
- `expire_le` ;
- `statut`, qui redevient `active`.

## Expiration

Chaque session porte un instant `expire_le`.

Si `expire_le` est dépassé, la session devient `expiree`. Une session `expiree`
est refusée pour les appels protégés. Le backend retourne une erreur de session,
par exemple `session_expiree` ou `session_requise` selon le cas.

Le front doit alors oublier la session locale et forcer une reconnexion. Cette
reconnexion est une action technique. Elle ne modifie pas l'appartenance métier
du joueur à sa table ou à sa partie.

## Reprise

Après reconnexion, le backend cherche si le joueur est encore lié à une table
active ou à une partie active.

Si un contexte existe, `ReponseConnexion` contient `contexte_reprise`, avec les
informations nécessaires pour revenir au bon endroit :

- `id_joueur` ;
- `id_table` ;
- `id_partie` ;
- `statut_table` ;
- `skin_jeu`.

Le front utilise `contexte_reprise` pour rediriger directement le joueur vers la
table ou la partie. Le mécanisme `resoudreDestinationJoueur` reste un filet de
sécurité : il peut relire la situation UI ou le contexte lobby si le contexte
retourné à la connexion est absent ou insuffisant.

## Persistance

La table `lobby_sessions` contient :

- `id_session` ;
- `id_joueur` ;
- `statut` ;
- `dernier_heartbeat` ;
- `expire_le` ;
- `cree_le` ;
- `maj_le`.

Les statuts possibles sont :

- `active` ;
- `absente` ;
- `expiree`.

Les tables `lobby_tables` et `lobby_table_joueurs` ne dépendent pas de
`id_session`. Elles portent les relations métier de table et de siège à partir
de `id_joueur`.

## Sécurité et contrats

Les mutations protégées exigent :

```http
Authorization: Bearer <jeton_session>
```

Le lobby valide que la session existe, qu'elle n'est pas expirée et qu'elle
appartient au `id_joueur` concerné par l'opération.

Les endpoints publics ont un comportement distinct :

- `POST /api/joueurs` inscrit un joueur ;
- `POST /api/sessions` crée une nouvelle session ;
- `POST /api/sessions/{id_session}/heartbeat` renouvelle une session existante
  ou refuse une session expirée.

OpenAPI doit rester cohérent avec cette exigence : les mutations protégées
doivent déclarer l'en-tête `Authorization` requis.

## Limites actuelles

Le système ne fait pas encore les choses suivantes :

- pas de websocket ;
- pas d'expulsion automatique du siège à l'expiration de session ;
- pas de politique avancée de libération de siège ;
- une mécanique maison de migration SQL existe, mais elle reste volontairement
  simple et doit être appliquée explicitement sur les volumes existants.

Ces limites sont volontaires pour ce lot. La présence technique ne doit pas
devenir une règle implicite d'abandon métier.

## Règle importante

Ne jamais coder :

```text
session expirée => retirer joueur de la table
```

Coder plutôt :

```text
session expirée => reconnexion requise
```

Toute évolution de libération de siège doit être une règle métier explicite,
documentée et testée séparément de l'expiration de session.
