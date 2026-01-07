# Contrats UI – Conseil des ministres

Ce document fige les contrats d’API utilisés par l’UI-web.

Il couvre trois services :

1. Service **Lobby**
2. Service **Moteur-API**
3. Service **UI – État joueur** (worker Kafka)

L’objectif est que le front consomme **uniquement** ce qui est décrit ici.  
Toute évolution côté backend doit préserver ce contrat ou être accompagnée d’une mise à jour de ce document.

---

## 1. Service Lobby

### 1.1. Base

- **Titre**: Service Lobby
- **Version**: 0.1.0
- **Base path**: `""` (les endpoints sont préfixés par `/api` pour les ressources métier)

L’UI utilise le Lobby pour :

- inscription / connexion du joueur
- lister les joueurs visibles
- lister / créer / rejoindre des tables
- se déclarer prêt
- lancer une partie

---

### 1.2. Authentification

#### POST `/api/joueurs` – Inscription

Crée un nouveau joueur.

**Request body – `DemandeInscription`**

```jsonc
{
  "nom": "string",
  "alias": "string",
  "courriel": "string (email)",
  "mot_de_passe": "string"
}

**Response – ReponseInscription

```jsonc
{
  "id_joueur": "string",
  "nom": "string",
  "alias": "string",
  "courriel": "string (email)"
}
L’UI stocke au minimum id_joueur, alias, courriel dans un contexte.

POST /api/sessions – Connexion
Authentifie un joueur existant.

Request body – DemandeConnexion

```jsonc
{
  "courriel": "string (email)",
  "mot_de_passe": "string"
}
**Response – ReponseConnexion

```jsonc
{
  "id_joueur": "string",
  "nom": "string",
  "alias": "string",
  "courriel": "string (email)",
  "jeton_session": "string"
}
L’UI stocke id_joueur, alias, courriel, et éventuellement jeton_session
(ex : pour l’envoyer en header si on sécurise les appels plus tard).

1.3. Joueurs visibles
GET /api/joueurs/lobby – Lister joueurs visibles dans le lobby
Retourne les joueurs présents / visibles dans le lobby.

**Response – ReponseListeJoueursLobby

```jsonc
{
  "joueurs": [
    {
      "id_joueur": "string",
      "nom": "string",
      "alias": "string|null",
      "courriel": "string (email)"
    }
  ]
}
Utilisé pour afficher la colonne “joueurs dans le lobby” dans l’UI.

1.4. Tables
POST /api/tables – Créer une table
Request body – DemandeCreationTable

```jsonc
{
  "id_hote": "string",          // id_joueur
  "nom_table": "string",
  "nb_sieges": 4,               // int
  "mot_de_passe_table": "string|null",
  "skin_jeu": "string|null"     // ex. "minimal"
}
**Response – ReponseTable

```js
{
  "id_table": "string",
  "nom_table": "string",
  "nb_sieges": 4,
  "id_hote": "string",
  "statut": "string",           // ex. "en_preparation", "en_jeu", etc.
  "skin_jeu": "string|null"
}
GET /api/tables – Lister les tables
Paramètre optionnel :

statut: string|null – permet de filtrer sur un statut (ex. "en_preparation")

**Response – ReponseListeTables

```js
{
  "tables": [
    {
      "id_table": "string",
      "nom_table": "string",
      "nb_sieges": 4,
      "id_hote": "string",
      "statut": "string",
      "skin_jeu": "string|null"
    }
  ]
}
Utilisé dans la page Lobby pour afficher les tables disponibles / en cours.

GET /api/tables/{id_table}/joueurs – Lister les joueurs assis à une table
Path param

id_table: string

**Response – ReponseListeJoueursTable

```jsonc
{
  "id_table": "string",
  "joueurs": [
    {
      "id_joueur": "string",
      "nom": "string",
      "alias": "string|null",
      "courriel": "string (email)",
      "role": "hote" | "invite",
      "pret": true
    }
  ]
}
Utilisé par l’écran Table pour afficher la liste des joueurs, leurs rôles et leur statut “prêt”.

POST /api/tables/{id_table}/joueurs – Rejoindre la table
Path param

id_table: string

Request body – DemandePriseSiege

```jsonc
{
  "id_joueur": "string",
  "role": "hote" | "invite"   // default: "invite"
}
**Response – ReponseJoueurSiege

```jsonc
{
  "id_table": "string",
  "id_joueur": "string",
  "role": "hote" | "invite",
  "statut_table": "string"   // ex. "en_preparation"
}
Utilisé lors du clic “Rejoindre cette table” dans l’UI.

POST /api/tables/{id_table}/joueurs/pret – Se déclarer prêt
Path param

id_table: string

Request body – DemandeJoueurPret

```jsonc
{
  "id_joueur": "string"
}
**Response – ReponseTable

```jsonc
{
  "id_table": "string",
  "nom_table": "string",
  "nb_sieges": 4,
  "id_hote": "string",
  "statut": "string",
  "skin_jeu": "string|null"
}
L’UI met à jour l’état de la table et, en pratique, se fie surtout au service ui-état pour
détecter le lancement effectif de la partie.

POST /api/tables/{id_table}/lancer – Lancer la partie
Path param

id_table: string

Request body – DemandeLancerPartie

```js
{
  "id_hote": "string"   // id du joueur hôte lançant la partie
}
**Response – ReponsePartieLancee

```jsonc
{
  "id_partie": "string"
}
C’est principalement le worker Kafka + ui-état qui signalera au front que
la partie est réellement en cours (ancrage sur partie).

GET /api/skins – Lister les skins
**Response – ReponseListeSkins

```jsonc
{
  "skins": [
    {
      "id_skin": "string",
      "nom": "string",
      "description": "string|null"
    }
  ]
}
Utilisé éventuellement dans l’UI pour proposer le choix de skin lors de la création d’une table.

# 2. Service Moteur-API
## 2.1. Base

Titre: API Moteur - Conseil des ministres

Version: 1.0.0

L’UI consomme principalement :

la lecture du state complet d’une partie

la soumission des actions de jeu d’un joueur

(optionnel, côté UI-web actuel) la création d’une partie directement

Des headers optionnels sont disponibles :

x-correlation-id: string|null

Idempotency-Key (pour /actions)

## 2.2. Lire l’état d’une partie
GET /parties/{partie_id}/etat – Lire l’état

Path param

partie_id: string

**Response – ReponseEtat

{
  "partie_id": "string",
  "etat": {
    // objet JSON arbitraire, dépend de la skin,
    // mais stable pour l’UI minimal :
    // - phase / sous_phase / tour
    // - joueurs + cartes
    // - programme
    // - axes & capital
    // - historique
  }
}


L’UI ne repose que sur le contenu de etat. Les clés attendues côté front
sont documentées dans un autre fichier (contrat d’état de partie par skin).

2.3. Soumettre une action
POST /parties/{partie_id}/actions – Soumettre une action

Path param

partie_id: string

Headers (optionnels)

Idempotency-Key: string|null

x-correlation-id: string|null

Request body – RequeteAction

{
  "acteur": "string",        // id_joueur
  "type_action": "string",   // ex. "VOTE_POUR", "joueur.jouer_carte"
  "donnees": {               // payload libre (dict)
    // clés dépendantes de l’action
  }
}


**Response – 202 ReponseEtat

{
  "partie_id": "string",
  "etat": {
    // état mis à jour, même forme que GET /etat
  }
}


L’UI peut :

soit utiliser cet etat pour mise à jour immédiate,

soit simplement s’en remettre au service ui-état (Kafka) pour refléter la mise à jour,
en se basant sur les marqueurs pour déclencher un GET /etat.

2.4. (Optionnel) Créer une partie

Dans la plupart des cas, la création de partie sera faite via le service Lobby.
Pour référence :

POST /parties – Créer une partie

Request body – RequetePartie

{
  "partie_id": "string|null",
  "nom": "string",
  "joueurs": {             // map id_joueur -> pseudo
    "J000001": "Georges",
    "J000002": "Fabien"
  },
  "seed": 12345|null,
  "skin_jeu": "string|null",  // "minimal" par défaut
  "options": {}               // dict optionnel
}


**Response – ReponseEtat (voir plus haut).

3. Service UI – État joueur (worker Kafka)
3.1. Base

Titre: Service UI - Etat joueur

Version: 0.1.0

Ce service est un projecteur :
il consomme les événements Kafka et expose, par joueur, une projection de :

sa position dans le système (lobby / table / partie),

le résumé de la partie (phase/sous-phase/tour),

les actions disponibles,

un journal recentré sur lui,

des marqueurs pour détecter les changements.

C’est l’API pivot de l’UI-web.

3.2. Lire la situation d’un joueur
GET /ui/joueurs/{joueur_id}/situation – Lire situation

Path param

joueur_id: string

**Response – SituationJoueurDTO

{
  "version": 1,
  "joueur_id": "string",

  "ancrage": {
    "type": "lobby" | "table" | "partie",
    "table_id": "string|null",
    "partie_id": "string|null"
  },

  "etat_partie": {
    "phase": "string|null",
    "sous_phase": "string|null",
    "tour": 1   // integer|null
  },

  "actions_disponibles": [
    {
      "code": "string",                 // ex. "VOTE_POUR"
      "label": "string",                // ex. "Voter POUR le programme"
      "payload": {},                    // dict libre, par défaut {}
      "requires_confirmation": false    // bool, défaut false
    }
  ],

  "journal_recent": [
    {
      "event_id": "string|null",
      "occurred_at": "2025-12-03T13:45:12Z", // ISO 8601
      "category": "string|null",
      "severity": "string|null",
      "message": "string"
    }
  ],

  "marqueurs": {
    "partie": "2025-12-03T13:45:12Z|null",
    "actions": "2025-12-03T13:46:00Z|null",
    "info_axes": "2025-12-03T13:46:30Z|null",
    "info_cartes": "2025-12-03T13:47:00Z|null"
  }
}

3.3. Utilisation côté UI

Routing automatique :

si ancrage.type === "partie" → rediriger vers /jeu

si ancrage.type === "table" → /tables/{table_id}

sinon → /lobby

Assistant de tour (panneau 2) :

actions_disponibles alimente les boutons des décisions possibles.

Un clic sur un bouton déclenche un POST /parties/{partie_id}/actions :

acteur = joueur_id

type_action = action.code (ou mapping selon convention)

donnees = action.payload

Détection des changements :

marqueurs.partie :

change quand l’état de la partie a évolué → déclenche un GET /parties/{id}/etat.

marqueurs.actions :

change quand les actions disponibles pour ce joueur changent → déclenche un
rafraîchissement de la liste d’actions (et éventuellement le focus sur le panneau “Assistant”).

marqueurs.info_axes, marqueurs.info_cartes :

utilisés pour recharger des informations détaillées si nécessaire (ex: axes, définitions de cartes).
