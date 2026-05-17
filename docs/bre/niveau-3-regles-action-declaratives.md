# Niveau 3 — règles d’action déclaratives

Point d’entrée recommandé de la documentation BRE :
[`README.md`](README.md).

## Statut

Ce document prépare l’issue T35 :
`BRE T35 — Formaliser les règles d’action déclaratives niveau 3`.

Il ne définit pas encore l’ensemble du contrat cible de
`regles/validation_actions.yaml`. Cette passe inscrit seulement le principe
directeur général qui devra guider la formalisation du niveau 3.

## Principe général à respecter

Les règles d’action déclaratives devront respecter le principe général :
[`Principe directeur — progression de complexité poweruser`](modele-heritage-skin-poweruser.md#principe-directeur--progression-de-complexité-poweruser).

Conséquence pour T35 : `validation_actions.yaml` ne doit pas devenir un langage
complet, un script embarqué ou un moteur de règles généraliste. Il doit rester
un dispositif déclaratif, compréhensible, diagnostiquable et validable par un
créateur de skin qui progresse par paliers.

## Limites de cette passe

Cette passe ne remplace pas `validation_cartes.yaml`, n’implémente pas
`validation_actions.yaml`, ne modifie pas le runtime et ne touche pas au
`rules-service`.
