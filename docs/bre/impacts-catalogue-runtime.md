# Impacts Du Catalogue Sur Le Runtime Et Le Lobby

Ce document complète l’inventaire des skins d’élaboration après l’introduction
du catalogue minimal `donnees/cabinet/skins/catalogue.yaml`.

Depuis T34, le catalogue est appliqué par le lobby et par l’entrée HTTP directe
de l’API moteur. Le moteur Cabinet interne conserve encore son chargeur Python
historique.

## Fichiers Inspectés

- `donnees/cabinet/skins/catalogue.yaml`
- `services/cabinet/bre/catalogue_skins.py`
- `services/cabinet/moteur/config_loader.py`
- `services/cabinet/moteur/manager.py`
- `services/api_moteur/app.py`
- `services/api_moteur/schemas.py`
- `services/lobby/services_lobby.py`
- `services/lobby/catalogue_skins.py`
- `services/lobby/schemas.py`
- `services/adapter-evenements/adapter_evenements/worker_adapter.py`
- `services/commande_moteur/worker_moteur.py`
- `services/ui-web/src/pages/LobbyPage.tsx`
- `services/ui-web/src/api/lobbyApi.ts`
- `services/ui-web/src/types/lobby.ts`
- contrats `skin_jeu` HTTP et Kafka dans `contrats/jsonschema/`

## Comportement Actuel

### Moteur Cabinet

Le noyau Cabinet interne ne lit pas encore le catalogue.

`services/cabinet/moteur/config_loader.py` charge une skin par import Python :

```text
services.cabinet.skins.<skin_id>
```

La skin doit fournir :

- `get_config()`
- `get_regles()`

`PartieManager.creer()` reçoit `skin`, appelle `construire_etat()`, puis le
chargeur importe le module Python correspondant. Une entrée catalogue
`source.type: dossier` n’est donc pas chargeable par ce chargeur.

La validation d’exposition est appliquée en amont, dans le lobby et dans l’API
moteur.

### API Moteur

`services/api_moteur/schemas.py` accepte `skin_jeu` dans `RequetePartie`, avec
la valeur par défaut `minimal`.

`services/api_moteur/app.py` valide maintenant `skin_jeu` contre le catalogue
avant d’appeler le `PartieManager`.

Comportement actuel :

- skin absente du catalogue : refus `SKIN_INCONNUE` ;
- skin présente mais `chargeable: false` : refus `SKIN_NON_CHARGEABLE` ;
- skin `chargeable: true` : transmission au chargeur Python historique.

### Lobby Et Création De Table

`services/lobby/services_lobby.py` lit maintenant le catalogue par
`services/lobby/catalogue_skins.py`.

Le catalogue sert à deux endroits :

- `GET /api/skins` retourne seulement les entrées `chargeable: true` ;
- `creer_table()` refuse une valeur `skin_jeu` absente du catalogue ;
- `creer_table()` refuse une valeur `skin_jeu` présente mais
  `chargeable: false`.

Le conteneur `lobby` copie aussi `donnees/` afin de disposer du catalogue au
runtime.

### Propagation Kafka

Le choix de skin est propagé sans réinterprétation :

1. la table conserve `skin_jeu` ;
2. l’événement lobby `PartieLancee` contient `skin_jeu` ;
3. `adapter-evenements` produit une commande `partie.creer` avec `skin_jeu` ;
4. `commande_moteur` envoie `skin_jeu` à `POST /parties`.

Ces composants ne découvrent pas les skins. Ils transportent la valeur choisie.

### UI Web

`services/ui-web/src/pages/LobbyPage.tsx` charge `GET /api/skins`, sélectionne
par défaut la première skin retournée, puis envoie `skin_jeu` lors de la
création d’une table.

L’UI dépend donc de la liste fournie par le lobby. Elle ne devrait pas contenir
de logique propre pour décider si une skin est chargeable.

### Outils CLI

Les outils de diagnostic et de validation candidate utilisent déjà le catalogue
pour résoudre les entrées `source.type: dossier`.

Ils conservent aussi :

- `--skin-yaml` pour diagnostiquer un fichier brouillon monté ;
- `--skin-dir` pour valider un dossier brouillon monté.

Cette utilisation du catalogue reste distincte du runtime jouable : elle permet
de diagnostiquer ou valider des overlays non chargeables sans les rendre
sélectionnables dans le lobby.

## Comportement Appliqué Avec Catalogue

Le catalogue est maintenant la source de gouvernance pour exposer ou refuser les
skins côté lobby et entrée HTTP moteur.

Règle cible :

> Seules les entrées `chargeable: true` devraient être exposées au lobby et
> acceptées lors de la création d’une table.

Conséquences :

- `GET /api/skins` liste les entrées `chargeable: true` compatibles avec le
  runtime courant ;
- `POST /api/tables` refuse une skin absente du catalogue ou marquée
  `chargeable: false` ;
- `POST /parties` refuse explicitement une skin absente ou non chargeable avant
  l’import Python ;
- les tests doivent couvrir la liste exposée et le refus d’une skin non
  chargeable.

## Types De Source

### `source.type: module_python`

Cette source correspond au runtime actuel.

Elle pointe vers une skin Python ou hybride importable, par exemple :

```yaml
source:
  type: module_python
  module: services.cabinet.skins.debut_mandat_bre
```

Une entrée de ce type peut être chargeable si :

- le module existe ;
- il fournit `get_config()` et `get_regles()` ;
- elle est marquée `chargeable: true`.

### `source.type: dossier`

Cette source correspond aux artefacts déclaratifs :

- overlay de brouillon ou d’exemple ;
- future skin déclarative résolue ;
- template ;
- contenu qui n’est pas forcément importable comme module Python.

Dans l’état actuel, une entrée `source.type: dossier` ne doit pas être exposée
au runtime sauf si un futur chargeur déclaratif ou une publication résolue
stabilise son format.

## Conséquences Pour Les Exemples

Les overlays contrôlés :

- `exemple_mandat_austerite_overlay`
- `exemple_mandat_climat_overlay`

sont dans `donnees/cabinet/skins/exemples/` et marqués `chargeable: false`.

Ils doivent rester disponibles pour :

- diagnostic créateur ;
- validation candidate ;
- documentation ;
- tests d’outils.

Ils ne doivent pas apparaître dans la liste de skins jouables du lobby, et une
création de table avec ces ids devrait être refusée dans l’incrément futur.

## Conséquences Pour Les Skins Python Ou Hybrides

Les skins Python et hybrides restent temporairement sous
`services/cabinet/skins/`.

Le catalogue peut les référencer avec `source.type: module_python`, sans les
déplacer.

Exemples :

- `minimal` : fixture de test, chargeable pour préserver les tests et le défaut
  historique ;
- `debut_mandat` : skin Python historique chargeable ;
- `debut_mandat_bre` : référence provisoire BRE chargeable ;
- `Mandat_difficile` : historique à clarifier, non chargeable ;
- `mandat_fragile` : démonstrateur poweruser historique, non chargeable dans le
  catalogue.

Le fait qu’une skin Python soit techniquement importable ne devrait plus suffire
à la rendre visible au lobby. La décision d’exposition doit venir du catalogue.

## Risques De Régression À Surveiller

- Le lobby ne possède plus la liste `SKINS_DISPONIBLES` codée en dur. La liste
  vient du catalogue, ce qui peut changer l’ordre et le contenu de `GET
  /api/skins`.
- L’UI choisit la première skin retournée par le lobby. Un changement d’ordre
  peut changer la skin par défaut.
- Des tests peuvent dépendre de `minimal`, `debut_mandat`,
  `Mandat_difficile` ou `debut_mandat_bre` dans la liste actuelle.
- L’API moteur consulte maintenant le catalogue. Une création de partie directe
  avec une skin non chargeable est refusée plus tôt qu’avant.
- Les contrats HTTP et Kafka transportent `skin_jeu` comme chaîne simple. Si
  `GET /api/skins` expose de nouveaux champs de catalogue, les contrats
  `SkinInfo` et `ReponseListeSkins` devront être revus explicitement.
- Les exemples `source.type: dossier` ne sont pas chargeables par le moteur
  actuel. Les exposer au lobby créerait une erreur au lancement de partie.

## Incrément Futur Recommandé

T34 couvre l’application minimale du catalogue par le lobby et la création de
table. Les incréments suivants devraient plutôt porter sur :

```text
Aligner le runtime interne Cabinet sur le catalogue de skins
```

Objectif proposé :

- conserver la compatibilité des appels internes aux tests qui chargent encore
  directement des skins Python/hybrides ;
- décider si `charger_config_et_regles()` doit refuser les skins non
  chargeables ou rester un outil bas niveau ;
- préparer le futur chargeur des skins déclaratives résolues ;
- préciser les impacts contrats si `SkinInfo` expose un jour des métadonnées de
  catalogue supplémentaires.

## Non-Objectifs De Cette Passe

Cette analyse ne modifie pas :

- le lobby ;
- le frontend ;
- l’API de création de table ;
- le moteur Cabinet ;
- le rules-service ;
- les contrats HTTP ou Kafka.

Elle ne rend pas les overlays déclaratifs jouables et n’implémente pas la
publication résolue.
