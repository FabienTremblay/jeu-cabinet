# UAT Créateur De Skin

## Objectif

Ce parcours UAT permet à un créateur de skin de vérifier qu’un overlay
`skin.yaml` est lisible et compréhensible sans écrire de test Python.

Le diagnostic actuel ne modifie pas le jeu. Il affiche ce que la skin déclare
et ce qui reste hérité.

## Exécuter Le Diagnostic Dans Docker

Le service Docker à utiliser est `api-moteur`, car son image contient le paquet
Python `services`.

Le diagnostic ne dépend pas de Kafka ni du `rules-service`. La commande
recommandée évite donc de démarrer les dépendances.

Dans l’environnement MaisonNeuve ou dans une stack locale déjà configurée, les
variables Compose comme `STACK_NETWORK` et `STACK_ID` doivent être fournies par
l’environnement de déploiement :

```bash
docker compose run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin uat_mandat_austerite_overlay
```

Par chemin explicite :

```bash
docker compose run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin \
  --skin-yaml services/cabinet/skins/uat_mandat_austerite_overlay/skin.yaml
```

Dans un environnement local nu, si Compose signale que `STACK_NETWORK` n’est pas
défini, charger d’abord les variables habituelles de la stack ou les fournir
explicitement avec un réseau Docker utilisateur existant.

## Commande Locale Développeur

La même commande peut être lancée localement avec l’environnement virtuel :

```bash
.venv/bin/python -m services.cabinet.outils.diagnostiquer_skin uat_mandat_austerite_overlay
```

## Exemple De Sortie

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

## Interpréter Le Résultat

`Champs déclarés` liste uniquement les champs présents dans le fichier
`skin.yaml` inspecté.

`Familles héritées` indique les familles que l’overlay ne redéfinit pas encore
et qui restent portées par la skin parente.

La fusion complète des familles héritées n’est pas exécutée dans cet incrément.
`config.py` et `regles.py` restent en place.

## Validation Développeur

Les tests automatisés restent nécessaires pour l’ingénierie :

```bash
.venv/bin/python -m pytest services/cabinet/tests/test_diagnostiquer_skin_cli.py -q
.venv/bin/python -m pytest services/cabinet/tests/test_skin_yaml.py -q
.venv/bin/python -m pytest services/cabinet/tests -q
```
