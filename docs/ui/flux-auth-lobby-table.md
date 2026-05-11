
# Flux Auth → Lobby → Table → Jeu → Fin (Version complète — Documentation Officielle)

Sources de vérité contractuelles :
- OpenAPI Lobby : `contrats/openapi/lobby.openapi.json`
- OpenAPI API Moteur : `contrats/openapi/api_moteur.openapi.json`
- OpenAPI UI État Joueur : `contrats/openapi/ui_etat_joueur.openapi.json`
- JSON Schema UI : `contrats/jsonschema/http/ui_etat_joueur/`
- Contrats UI transverses : `docs/ui/contracts.md`

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

Le frontend utilise `ui-état-joueur.ancrage` comme source principale de
navigation. Pour une reprise après refresh, retour d’aide, retour accueil/lobby
ou projection UI absente/en retard, il peut utiliser le contexte persistant du
lobby : `GET /api/joueurs/{id_joueur}/contexte`.

---

## 3. Authentification → Lobby

### 3.1. Authentification

Après login :

```json
{
  "version": 1,
  "joueur_id": "J000001",
  "ancrage": { "type": "lobby" },
  "etat_partie": null,
  "actions_disponibles": []
}
```

L’UI se base sur `ancrage.type === "lobby"` pour afficher l’écran Lobby.

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

Dans l’écran de table, les joueurs voient les joueurs présents, la politique de
timeout de la table et marquent leur statut *Prêt*.

### 4.1. Configuration du timeout avant lancement

Le bloc timeout est affiché avant le lancement de la partie.

Visibilité :

- l'hôte voit la politique et les contrôles d'édition ;
- les invités voient la politique, mais ne peuvent pas la modifier.

Règles UI :

- l'UI affiche le délai en minutes/heures compréhensibles ;
- l'API lobby reste exprimée en secondes ;
- lors de la sauvegarde, l'UI convertit vers `delai_inactivite_secondes` ;
- l'UI n'expose pas le champ `version` en édition ;
- l'édition est désactivée si la table n'est plus `ouverte` ou
  `en_preparation`.
- le polling de la table reste actif, mais ne doit pas réafficher l'écran
  `Loading` après le chargement initial ;
- une erreur temporaire de rafraîchissement conserve la dernière table connue,
  afin de ne pas masquer le bloc timeout ;
- pendant que l'hôte édite le formulaire timeout, le polling ne doit pas
  écraser les valeurs locales ni faire perdre le focus.

Le lien d'aide du bloc timeout pointe vers :

```text
/aide?retour=/tables/{id_table}#timeout-partie
```

Le bouton de retour de l'aide revient alors à la table d'origine.

Endpoint utilisé :

```http
PATCH /api/tables/{id_table}/configuration
```

Payload :

```json
{
  "id_hote": "J000001",
  "politique_timeout_partie": {
    "active": true,
    "delai_inactivite_secondes": 3600
  }
}
```

Le réglage s'applique au lancement : le lobby copie la politique effective dans
`PartieLancee`, puis la partie conserve sa propre configuration. Après le
lancement, la configuration de table est verrouillée côté lobby.

### 4.2. Préparation et lancement

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

En reprise de session, l'UI résout d'abord la destination depuis
`ui-état-joueur.ancrage`. Si l'ancrage ne fournit pas de table ou partie
exploitable, elle consulte le contexte lobby. Une partie `TERMINEE` dans
`ui-état-joueur` n'est pas une destination exploitable : elle interdit la
reprojection vers l'ancienne partie, mais ne bloque pas la consultation du
contexte lobby.

- `ouverte` ou `en_preparation` avec `id_table` → `/tables/{id_table}` ;
- `en_cours` avec `id_partie` → `/parties/{id_partie}` ;
- contexte vide ou table terminée → `/lobby`.

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

Pour une partie terminée, le polling ne rebascule plus vers la partie. En
revanche, “retour au lobby” ne signifie pas rester au lobby si le joueur est
encore attaché côté lobby à une table ou partie active : la reprise de contexte
peut alors reprojeter automatiquement vers la destination active.

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

La session lobby est jetable. Si le joueur cesse d’envoyer des heartbeats,
sa session passe à `expiree` et les appels protégés doivent être refusés.
Cette expiration ne retire pas le joueur de sa table : le siège reste lié à
`id_joueur`. Après reconnexion, le lobby renvoie le contexte de reprise pour
retourner à la table ou à la partie active si elle existe encore.

---

## Reprise après expiration de session

À la connexion, le front reçoit `jeton_session` et le conserve pour les appels
protégés. Il envoie automatiquement un heartbeat périodique au lobby.

Si la session expire, le front force la reconnexion. Après reconnexion,
`contexte_reprise` peut rediriger le joueur vers sa table ou sa partie active.
Le siège reste réservé côté lobby tant que la table existe.

Règle d’or : Une session expirée invalide l’accès technique, mais ne détruit
pas le contexte métier du joueur.

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
