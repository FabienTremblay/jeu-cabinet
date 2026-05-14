# Gabarit De Skin Overlay BRE

Ce dossier est un modèle à copier pour créer une skin BRE poweruser de niveau 1.
Il ne représente pas une skin jouable par défaut.

## Usage

Copier le contenu de ce dossier dans une nouvelle skin :

```text
services/cabinet/skins/<id_de_la_skin>/
```

Puis remplacer les marqueurs dans `skin.yaml` :

- `A_REMPLACER_ID_SKIN` ;
- `A_REMPLACER_NOM_SKIN` ;
- `A_REMPLACER_PITCH_DU_SCENARIO`.

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

Au niveau 1, ne pas modifier :

- `config.py` ;
- `regles.py` ;
- l’UI ;
- le `rules-service`.

## Diagnostic Après Copie

En développement MaisonNeuve :

```bash
docker compose --env-file .env.dev -p cabinet-dev \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin <id_de_la_skin>
```

Pour valider avec les fichiers versionnés :

```bash
docker compose --env-file .env.dev.example -p cabinet-dev-test \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin <id_de_la_skin>
```

La sortie doit afficher la skin, son parent, les champs déclarés et les familles
héritées.
