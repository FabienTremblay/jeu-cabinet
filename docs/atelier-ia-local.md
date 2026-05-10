# Atelier IA local

## Contexte

L'atelier fonctionne localement sous l'utilisateur Linux `atelierdev`, dans le dépôt `~/workspace/jeu-cabinet`.

La branche de travail est `essai-codex`. Aucun travail ne doit être effectué directement sur `main`.

## Rôles

Codex est l'agent principal pour analyser, planifier, modifier et tester.

Aider est disponible comme outil local via la commande `aider-lm`.

## Usage d'Aider

Le modèle local Aider le plus concluant est `qwen2.5-coder-3b-instruct`.

Aider doit être limité à des micro-modifications ciblées, sur un seul fichier ou un très petit nombre de fichiers.

Aider ne doit être lancé qu'après validation humaine explicite. Pour une tâche adaptée à Aider, la commande exacte et le prompt exact doivent être proposés avant exécution.

## Discipline Git

Tout diff doit être inspecté avant commit.

Aucun push ne doit être fait sans validation humaine.
