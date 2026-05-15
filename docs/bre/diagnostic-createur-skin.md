# Diagnostic Créateur De Skin

## Objectif

Ce parcours permet à un créateur de skin de vérifier qu’un overlay
`skin.yaml` est lisible et compréhensible sans écrire de test Python.

Le diagnostic actuel ne modifie pas le jeu. Il affiche ce que la skin déclare
et ce qui reste hérité.

Il sait aussi résumer les fichiers optionnels de contenu déclaratif de couche 2
lorsqu’ils existent dans l’overlay : `cartes.yaml`, `evenements.yaml` et
`messages.yaml`. Ce résumé reste un diagnostic : il ne publie pas la skin et ne
rend pas l’overlay jouable.

Pour créer une nouvelle skin overlay pas à pas, voir
`docs/bre/creer-une-skin-bre.md`.
Pour la suite du modèle, notamment le contenu déclaratif et la publication
résolue, voir `docs/bre/couche-2-contenu-declaratif.md`.
Pour vérifier qu’un overlay peut devenir une candidate publiable, voir
`docs/bre/validation-skin-candidate.md`.

## Exécuter Le Diagnostic Dans Docker

Le service Docker à utiliser est `api-moteur`, car son image contient le paquet
Python `services`.

Le diagnostic ne dépend pas de Kafka ni du `rules-service`. La commande
recommandée évite donc de démarrer les dépendances avec `--no-deps`.

La commande doit respecter le même choix d’environnement que le reste du projet :
fichier env, nom de projet Compose et overlay Compose. Ne pas lancer une
commande Docker Compose nue sur MaisonNeuve, car MaisonNeuve peut aussi héberger
la production actuelle issue de `main`.

### Diagnostiquer Une Skin Brouillon Montée

Pour une skin en brouillon, ne pas reconstruire l’image Docker à chaque
modification. Monter explicitement le dossier de travail dans le conteneur et
lire le fichier `skin.yaml` par `--skin-yaml` :

```bash
docker compose --env-file .env.dev.example -p cabinet-dev-test \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps \
  -v "$PWD/<chemin-vers-la-skin>:/skin-a-tester" \
  api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin \
  --skin-yaml /skin-a-tester/skin.yaml
```

Cette forme est recommandée pour l’essai créateur : la skin peut vivre dans un
répertoire externe, dans un espace de travail non versionné ou dans une branche
de validation. Le conteneur lit le fichier monté sans dépendre du contenu copié
dans l’image lors du build.

La commande par identifiant de skin reste pertinente pour les skins déjà
présentes dans l’image, notamment les skins publiées dans
`services/cabinet/skins/`.

Si une skin vient d’être ajoutée ou renommée dans `services/cabinet/skins/`,
reconstruire l’image `api-moteur` avant de la diagnostiquer par identifiant.

### Diagnostiquer L’exemple Couche 2 Intégré

L’exemple contrôlé `exemple_mandat_climat_overlay` contient `skin.yaml`,
`cartes.yaml`, `evenements.yaml` et `messages.yaml`.

```bash
docker compose --env-file .env.dev.example -p cabinet-dev-test \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin exemple_mandat_climat_overlay
```

Cette commande sert à vérifier que le diagnostic affiche les contenus
déclaratifs présents dans une skin intégrée à l’image.

### Développement MaisonNeuve

```bash
docker compose --env-file .env.dev -p cabinet-dev \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin exemple_mandat_austerite_overlay
```

Par chemin explicite :

```bash
docker compose --env-file .env.dev -p cabinet-dev \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin \
  --skin-yaml services/cabinet/skins/exemple_mandat_austerite_overlay/skin.yaml
```

Préparation attendue si `.env.dev` n’existe pas encore :

```bash
cp .env.dev.example .env.dev
docker network create cabinet_dev_net
```

Si le réseau existe déjà, Docker signale simplement qu’il est déjà présent.

### MaisonLinux Ou Validation Stable

Utiliser l’environnement MaisonLinux lorsque la validation doit être faite dans
la stack LAN stable :

```bash
docker compose --env-file .env.maisonlinux -p cabinet-maisonlinux \
  -f docker-compose.yml -f docker-compose.maisonlinux.yml \
  run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin exemple_mandat_austerite_overlay
```

La préparation de `.env.maisonlinux` et du réseau
`cabinet_maisonlinux_net` est décrite dans `docs/execution-docker.md`.

### Production MaisonNeuve

La production actuelle MaisonNeuve roule depuis `main` avec son `.env`
historique. Ne pas utiliser la branche de travail `feature/bre-poweruser-skin`
pour lancer ce diagnostic contre la production, sauf procédure de déploiement
explicite.

## Commande Locale Développeur

La même commande peut être lancée localement avec l’environnement virtuel :

```bash
.venv/bin/python -m services.cabinet.outils.diagnostiquer_skin exemple_mandat_austerite_overlay
```

## Exemple De Sortie

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

Contenus déclaratifs de couche 2 :
- cartes.yaml : absent
- evenements.yaml : absent
- messages.yaml : absent

Limite actuelle :
Ce diagnostic lit l’overlay déclaratif.
La fusion complète des familles héritées n’est pas encore implémentée.
La publication résolue de la skin n’est pas encore implémentée.
```

Pour `exemple_mandat_climat_overlay`, la même section affiche les fichiers
présents, la valeur `heriter`, les cartes ou événements ajoutés, remplacés ou
retirés, ainsi que les clés de messages personnalisées.

## Interpréter Le Résultat

`Champs déclarés` liste uniquement les champs présents dans le fichier
`skin.yaml` inspecté.

`Familles héritées` indique les familles que l’overlay ne redéfinit pas encore
et qui restent portées par la skin parente.

`Contenus déclaratifs de couche 2` indique seulement ce que l’overlay déclare
dans ses fichiers optionnels. Les opérations `ajouter`, `remplacer` et
`retirer` ne sont pas encore résolues avec la skin parente.

La fusion complète des familles héritées n’est pas exécutée dans cet incrément.
La publication résolue n’est pas encore implémentée. `config.py` et `regles.py`
restent en place.

## Validation Développeur

Les tests automatisés restent nécessaires pour l’ingénierie :

```bash
.venv/bin/python -m pytest services/cabinet/tests/test_diagnostiquer_skin_cli.py -q
.venv/bin/python -m pytest services/cabinet/tests/test_skin_yaml.py -q
.venv/bin/python -m pytest services/cabinet/tests -q
```

## Étape Suivante : Validation Candidate

Après le diagnostic créateur, la commande suivante vérifie les erreurs locales
qui empêcheraient une publication fiable :

```bash
docker compose --env-file .env.dev.example -p cabinet-dev-test \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.valider_skin_candidate exemple_mandat_climat_overlay
```

Cette validation ne publie pas la skin et ne résout pas l’héritage.
