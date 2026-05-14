# Créer Une Skin BRE Poweruser

## Objectif

Cette recette explique comment créer une skin BRE déclarative de niveau 1 :
personnaliser le guide général du scénario.

L’approche cible n’est pas de copier toute une skin existante. Elle consiste à
créer une skin overlay, déclarer sa skin parente dans `skin.yaml`, puis vérifier
ce qui est déclaré et ce qui reste hérité.

L’exemple contrôlé du dépôt est :

```text
services/cabinet/skins/uat_mandat_austerite_overlay/skin.yaml
```

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

## 1. Créer Le Dossier Overlay

Créer un dossier dédié sous `services/cabinet/skins/` :

```text
services/cabinet/skins/mon_scenario_overlay/
```

Le dossier ne doit pas contenir une copie complète de la skin parente. Pour ce
premier niveau, le fichier attendu est seulement :

```text
services/cabinet/skins/mon_scenario_overlay/skin.yaml
```

## 2. Créer `skin.yaml`

Exemple minimal :

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

## 3. Diagnostiquer La Skin Dans Docker

La commande doit respecter la stratégie d’environnements du projet :
`--env-file`, nom de projet Compose et overlays Compose explicites.

En développement MaisonNeuve :

```bash
docker compose --env-file .env.dev -p cabinet-dev \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin uat_mandat_austerite_overlay
```

Pour valider la documentation avec les fichiers versionnés :

```bash
docker compose --env-file .env.dev.example -p cabinet-dev-test \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin uat_mandat_austerite_overlay
```

Variante locale développeur :

```bash
.venv/bin/python -m services.cabinet.outils.diagnostiquer_skin uat_mandat_austerite_overlay
```

## 4. Interpréter La Sortie

Sortie attendue pour l’exemple contrôlé :

```text
Skin : uat_mandat_austerite_overlay
Nom : Mandat d’austérité — overlay UAT
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
- indique clairement la limite de fusion.

Le diagnostic actuel ne fait pas encore ceci :

- fusionner toutes les familles héritées ;
- remplacer `config.py` ;
- remplacer `regles.py` ;
- migrer les cartes, événements, phases ou procédures.

## Niveaux D’Audace

Le modèle complet est décrit dans
`docs/bre/modele-heritage-skin-poweruser.md`.

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
- utiliser une commande Docker sans `--env-file` ni overlays Compose.

La copie complète d’une skin existante reste utile seulement pour des
expérimentations ou des UAT de transition. Elle n’est pas l’expérience cible.

## Critères De Réussite UAT

La recette est réussie si :

- le diagnostic affiche la bonne skin ;
- le parent est bien identifié ;
- les champs déclarés sont visibles ;
- les familles héritées sont visibles ;
- la limite de fusion non implémentée est explicite.

## Suite

Après validation du niveau 1, le prochain incrément naturel est le gabarit de
skin overlay de T28. Il doit réduire les erreurs de copie en montrant les champs
à remplacer plutôt qu’en dupliquant une skin complète.
