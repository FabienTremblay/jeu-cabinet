# Validation D’une Skin Candidate

## Objectif

Ce document définit le premier contrat de validation d’une skin candidate
poweruser.

Une candidate est un overlay assez mûr pour être relu avant publication. Elle
n’est pas encore une skin publiée, résolue ou jouable par héritage complet.

La validation candidate répond à une question différente du diagnostic créateur.

| Étape | Question |
| --- | --- |
| Diagnostic créateur | Qu’est-ce que mon overlay déclare ? |
| Validation candidate | Quelles erreurs empêchent une publication fiable ? |
| Publication résolue | Quel artefact versionné et autonome sera produit ? |

Le processus cible de publication résolue est décrit dans
`docs/bre/publication-skin-resolue.md`.

## Commande

Pour une skin déjà présente dans l’image `api-moteur` :

```bash
docker compose --env-file .env.dev.example -p cabinet-dev-test \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.valider_skin_candidate exemple_mandat_climat_overlay
```

Pour une candidate ou un brouillon monté explicitement :

```bash
docker compose --env-file .env.dev.example -p cabinet-dev-test \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps \
  -v "$PWD/<chemin-vers-la-skin>:/skin-a-tester" \
  api-moteur \
  python -m services.cabinet.outils.valider_skin_candidate \
  --skin-dir /skin-a-tester
```

La commande est non destructive. Elle ne copie pas de fichiers, ne publie pas
la skin, ne modifie pas `services/cabinet/skins/`, ne modifie pas de catalogue
et ne résout pas l’héritage.

## Erreurs Bloquantes Implémentées

### `skin.yaml`

- `skin.id` doit être présent ;
- `skin.herite_de` doit être présent pour une skin overlay ;
- le YAML doit être valide ;
- aucun marqueur `A_REMPLACER_*` ne doit rester ;
- lorsque la validation se fait par identifiant de skin intégré, `skin.id` doit
  correspondre au nom du dossier.

La validation par `--skin-dir` ne force pas le nom du dossier, car une skin
brouillon peut être montée dans Docker sous un alias comme `/skin-a-tester`.

### `cartes.yaml` Et `evenements.yaml`

Pour chaque fichier présent :

- le YAML doit être valide ;
- aucun marqueur `A_REMPLACER_*` ne doit rester ;
- `ajouter` doit contenir une liste ;
- `remplacer` doit contenir une liste ;
- `retirer` doit contenir une liste ;
- un même id ne doit pas être dupliqué dans `ajouter` ;
- un même id ne doit pas être dupliqué dans `remplacer` ;
- un même id ne doit pas être dupliqué dans `retirer` ;
- un même id ne doit pas apparaître dans plusieurs opérations du même fichier.

### `messages.yaml`

Pour le fichier présent :

- le YAML doit être valide ;
- aucun marqueur `A_REMPLACER_*` ne doit rester ;
- le bloc `messages` doit être une table ;
- aucune clé de message ne doit être vide.

## Avertissements Implémentés

Les sections inconnues produisent actuellement un avertissement clair. Elles ne
bloquent pas encore la candidate, parce que le modèle de couche 2 reste en cours
de stabilisation.

Exemples :

- `skin.version` absente ;
- section inconnue au premier niveau de `cartes.yaml` ;
- section inconnue dans le bloc `cartes` ;
- section inconnue au premier niveau de `messages.yaml`.

## Validations Dépendantes Du Parent

Certaines validations ne peuvent pas être complètes tant que le validateur ne
lit pas la skin parente et son contenu résolu.

Elles sont documentées comme validations futures :

- `ajouter` ne doit pas viser un id déjà hérité du parent ;
- `remplacer` doit viser un id existant dans le parent ;
- `retirer` doit viser un id existant dans le parent ;
- les effets référencés doivent être connus ;
- les axes référencés doivent exister.

Ces règles appartiennent à la transition candidate vers publication résolue.

## Exemple De Sortie

```text
Validation skin candidate : exemple_mandat_climat_overlay
Dossier : /app/services/cabinet/skins/exemple_mandat_climat_overlay
Statut : valide

Erreurs bloquantes :
- aucune

Avertissements :
- aucun

Validations futures dépendantes du parent :
- ajouter ne doit pas viser un id déjà hérité du parent
- remplacer doit viser un id existant dans le parent
- retirer doit viser un id existant dans le parent
- les effets référencés doivent être connus
- les axes référencés doivent exister

Limite actuelle :
Cette commande valide la candidate sans publier la skin.
Elle ne résout pas encore l’héritage avec la skin parente.
```

## Critère De Passage

Une candidate peut passer à l’étape de conception de publication lorsque :

- la commande ne signale aucune erreur bloquante ;
- les avertissements sont compris ou corrigés ;
- le créateur accepte que les validations dépendantes du parent restent à faire
  pendant la publication résolue.

Cette étape ne garantit pas encore que la skin publiée sera jouable. Elle
garantit seulement que l’overlay ne contient pas les erreurs locales les plus
fréquentes.

L’étape suivante consiste à publier une skin résolue, versionnée et autonome
selon `docs/bre/publication-skin-resolue.md`.
