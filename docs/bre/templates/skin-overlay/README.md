# Gabarit De Skin Overlay BRE

Ce dossier est un modèle à copier pour créer une skin BRE poweruser de niveau 1.
Il ne représente pas une skin jouable par défaut.

Le niveau 1 couvre seulement le guide général du scénario : identité, parent,
nom, version, difficulté, pitch et quelques paramètres simples.

Ne pas placer ce dossier directement dans `services/cabinet/skins/` sans copie
et personnalisation. Les marqueurs `A_REMPLACER_*` doivent tous être remplacés.

## Usage

Copier le contenu de ce dossier dans une nouvelle skin :

```text
services/cabinet/skins/<id_de_la_skin>/
```

Puis remplacer les marqueurs dans `skin.yaml` :

- `A_REMPLACER_ID_SKIN` ;
- `A_REMPLACER_NOM_SKIN` ;
- `A_REMPLACER_PITCH_DU_SCENARIO`.

## Après Copie

1. Copier le dossier vers `services/cabinet/skins/<id_skin>/`.
2. Renommer le dossier avec l’identifiant technique de la skin.
3. Remplacer `A_REMPLACER_ID_SKIN` par le même identifiant.
4. Remplacer `A_REMPLACER_NOM_SKIN` par le nom lisible de la skin.
5. Ajuster `A_REMPLACER_PITCH_DU_SCENARIO`.
6. Supprimer ou ajuster les paramètres d’exemple.
7. Lancer le diagnostic Docker.

## Héritage

Le gabarit hérite de `debut_mandat_bre` :

```yaml
skin:
  herite_de: debut_mandat_bre
```

Cette parente est provisoire en attendant la future base
`base_conseil_ministres`.

La skin overlay doit personnaliser seulement les champs qu’elle assume. Les
autres familles restent héritées de la skin parente.

## Limites Actuelles

La fusion complète des familles héritées n’est pas encore implémentée.

Le diagnostic lit `skin.yaml`, affiche les champs déclarés et affiche les
familles héritées. Il ne rend pas encore la skin jouable par héritage complet.

Au niveau 1, ne pas modifier :

- `config.py` ;
- `regles.py` ;
- l’UI ;
- le `rules-service`.

Les fichiers comme `regles/validation_actions.yaml`, `messages.yaml`,
`cartes.yaml` ou `evenements.yaml` appartiennent à des niveaux plus avancés et
ne font pas partie de ce gabarit.

## Diagnostic Après Copie

En développement MaisonNeuve :

```bash
docker compose --env-file .env.dev -p cabinet-dev \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin <id_skin>
```

Pour valider avec les fichiers versionnés :

```bash
docker compose --env-file .env.dev.example -p cabinet-dev-test \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin <id_skin>
```

La sortie doit afficher la skin, son parent, les champs déclarés et les familles
héritées.
