# Créer Une Skin BRE Poweruser

Point d’entrée recommandé de la documentation BRE :
[`README.md`](README.md).

## Objectif

Cette recette explique comment créer une skin BRE déclarative de niveau 1 :
personnaliser le guide général du scénario.

L’approche cible n’est pas de copier toute une skin existante. Elle consiste à
créer une skin overlay, déclarer sa skin parente dans `skin.yaml`, puis vérifier
ce qui est déclaré et ce qui reste hérité.

L’exemple contrôlé du dépôt est :

```text
services/cabinet/skins/exemple_mandat_austerite_overlay/skin.yaml
```

Un gabarit minimal à copier est fourni dans :

```text
docs/bre/templates/skin-overlay/
```

Ce gabarit est un point de départ de niveau 1. Il ne devient utilisable qu’après
copie dans un espace brouillon ou dans une branche candidate, puis remplacement
de tous les marqueurs `A_REMPLACER_*`.

## Processus Recommandé

Une skin poweruser peut passer par trois états.

| État | Emplacement recommandé | Statut | Objectif |
| --- | --- | --- | --- |
| Brouillon | Répertoire externe ou répertoire de travail monté dans Docker | Non versionné | Élaboration et diagnostic créateur |
| Candidate | Branche dédiée ou espace de validation | Testée | Revue avant intégration |
| Publiée | `services/cabinet/skins/<skin_id>/` ou catalogue officiel futur | Versionnée | Skin intégrée au projet |

`services/cabinet/skins/` est l’espace des skins intégrées au projet. Ce n’est
pas l’espace naturel de brouillon.

## Niveau 1 — Guide Général Du Scénario

Au niveau 1, un créateur de skin peut personnaliser :

- l’identifiant technique ;
- le nom affiché ;
- la version ;
- la difficulté ;
- le pitch ;
- quelques paramètres simples.

Le reste reste hérité de la skin parente. Pour le moment, la parente provisoire
recommandée est `debut_mandat_bre`.

## 1. Créer Le Dossier Overlay Brouillon

Créer un dossier dédié dans un espace de travail. Par exemple, hors du dépôt :

```text
../skins-brouillon/mon_scenario_overlay/
```

Ou dans un espace non versionné de travail. Le dossier ne doit pas contenir une
copie complète de la skin parente. Pour ce premier niveau, le fichier attendu
est seulement :

```text
../skins-brouillon/mon_scenario_overlay/skin.yaml
```

## 2. Copier Le Gabarit

Copier le gabarit dans le nouveau dossier :

```bash
cp docs/bre/templates/skin-overlay/skin.yaml \
  ../skins-brouillon/mon_scenario_overlay/skin.yaml
```

Le gabarit contient des marqueurs explicites à remplacer :

```text
A_REMPLACER_ID_SKIN
A_REMPLACER_NOM_SKIN
A_REMPLACER_PITCH_DU_SCENARIO
```

## 3. Adapter `skin.yaml`

Exemple adapté :

```yaml
skin:
  id: mon_scenario_overlay
  herite_de: debut_mandat_bre
  nom: Mon scénario politique
  version: v1
  difficulte: intermediaire

presentation:
  pitch: >
    Le cabinet gouverne dans un contexte politique particulier.
    Certaines décisions deviennent plus coûteuses ou plus sensibles.

parametres:
  capital_politique_initial: 3
```

Champs importants :

- `skin.id` : identifiant technique, identique au dossier de skin ;
- `skin.herite_de` : skin parente héritée ;
- `skin.nom` : nom lisible ;
- `skin.version` : version de la skin ;
- `skin.difficulte` : indication de difficulté ;
- `presentation.pitch` : court texte d’intention ;
- `parametres.*` : premiers paramètres simples déclarés par l’overlay.

## 4. Diagnostiquer La Skin Dans Docker

La commande doit respecter la stratégie d’environnements du projet :
`--env-file`, nom de projet Compose et overlays Compose explicites.

Pour une skin brouillon, monter explicitement le dossier dans Docker. Cette
forme évite de reconstruire l’image `api-moteur` après chaque modification de
`skin.yaml` :

```bash
docker compose --env-file .env.dev -p cabinet-dev \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps \
  -v "$PWD/../skins-brouillon/mon_scenario_overlay:/skin-a-tester" \
  api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin \
  --skin-yaml /skin-a-tester/skin.yaml
```

Pour valider la documentation avec les fichiers versionnés :

```bash
docker compose --env-file .env.dev.example -p cabinet-dev-test \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps \
  -v "$PWD/../skins-brouillon/mon_scenario_overlay:/skin-a-tester" \
  api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin \
  --skin-yaml /skin-a-tester/skin.yaml
```

Pour une skin déjà présente dans l’image ou publiée dans
`services/cabinet/skins/`, la commande par identifiant reste disponible :

```bash
docker compose --env-file .env.dev.example -p cabinet-dev-test \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin exemple_mandat_austerite_overlay
```

Cette commande utilise l’exemple contrôlé du dépôt. Pour votre propre
skin, remplacer `exemple_mandat_austerite_overlay` par l’identifiant déclaré dans
`skin.id` seulement lorsque la skin est déjà présente dans l’image ou publiée
dans `services/cabinet/skins/`.

Un second exemple contrôlé, `exemple_mandat_climat_overlay`, montre le niveau 2
avec `cartes.yaml`, `evenements.yaml` et `messages.yaml` :

```bash
docker compose --env-file .env.dev.example -p cabinet-dev-test \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin exemple_mandat_climat_overlay
```

Variante locale développeur :

```bash
.venv/bin/python -m services.cabinet.outils.diagnostiquer_skin mon_scenario_overlay
```

## 5. Interpréter La Sortie

Sortie attendue pour l’exemple contrôlé :

```text
Skin : exemple_mandat_austerite_overlay
Nom : Mandat d’austérité — overlay exemple
Version : v1
Difficulté : intermediaire
Hérite de : debut_mandat_bre

Champs déclarés :
- skin.id
- skin.herite_de
- skin.nom
- skin.version
- skin.difficulte
- presentation.pitch
- parametres.capital_politique_initial

Familles héritées :
- cartes
- événements
- règles
- phases
- procédures

Limite actuelle :
Ce diagnostic lit l’overlay déclaratif.
La fusion complète des familles héritées n’est pas encore implémentée.
```

`Champs déclarés` montre ce que le fichier `skin.yaml` contient réellement.

`Familles héritées` montre ce que la skin overlay ne redéfinit pas encore.

## Ce Qui Est Implémenté Maintenant

Le diagnostic actuel :

- lit `skin.yaml` ;
- affiche les champs déclarés ;
- affiche les familles héritées ;
- résume les contenus déclaratifs de couche 2 si `cartes.yaml`,
  `evenements.yaml` ou `messages.yaml` existent ;
- indique clairement la limite de fusion.

Le diagnostic actuel ne fait pas encore ceci :

- fusionner toutes les familles héritées ;
- remplacer `config.py` ;
- remplacer `regles.py` ;
- migrer les cartes, événements, phases ou procédures.

## Niveaux D’Audace

Le modèle complet est décrit dans
`docs/bre/modele-heritage-skin-poweruser.md`.
La couche 2 sur le contenu déclaratif, les candidates et la publication résolue
est décrite dans `docs/bre/couche-2-contenu-declaratif.md`.

Résumé :

- niveau 1 : guide général du scénario ;
- niveau 2 : contenu ;
- niveau 3 : règles d’action ;
- niveau 4 : résolution politique ;
- niveau 5 : chorégraphie.

Commencer au niveau 1 permet de valider l’identité et l’intention d’une skin
avant d’assumer des règles plus complexes.

## Pièges Fréquents

- oublier `skin.id` ;
- oublier `skin.herite_de` ;
- confondre overlay et copie complète ;
- croire que l’héritage complet est déjà exécuté ;
- modifier `config.py` trop tôt ;
- modifier `regles.py` trop tôt ;
- utiliser une commande Docker sans `--env-file` ni overlays Compose ;
- diagnostiquer une skin brouillon par identifiant alors qu’elle n’est pas dans
  l’image Docker.

La copie complète d’une skin existante reste utile seulement pour des
expérimentations ou des essais créateur de transition. Elle n’est pas
l’expérience cible.

## Critères De Réussite Du Diagnostic Créateur

La recette est réussie si :

- le diagnostic affiche la bonne skin ;
- le parent est bien identifié ;
- les champs déclarés sont visibles ;
- les familles héritées sont visibles ;
- la limite de fusion non implémentée est explicite.

## Suite

Après validation du niveau 1, le passage en candidate peut se faire dans une
branche dédiée ou un espace de revue. L’intégration dans
`services/cabinet/skins/` vient seulement au moment de publier la skin dans le
projet.

Avant toute publication future, lancer la validation candidate :

```bash
docker compose --env-file .env.dev.example -p cabinet-dev-test \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.valider_skin_candidate exemple_mandat_climat_overlay
```

Le contrat de cette validation est documenté dans
`docs/bre/validation-skin-candidate.md`.
