# Architecture Fonctionnelle BRE

## Intention

La démonstration BRE `poweruser skin` sépare progressivement trois niveaux :

- le noyau Cabinet conserve l'état et applique les commandes ;
- le `rules-service` reste le point d'entrée BRE et le routeur des moteurs ;
- le skin porte les règles ajustables par configuration.

## Découpage Actuel

Pour `debut_mandat_bre` :

- `analyse_skin` route vers la bonne famille de règles ;
- `etat_min` expose les facts minimaux ;
- `validation_cartes.yaml` décrit la validation et les coûts de carte ;
- un mini-interpréteur Python applique cette règle pour T23.

## Frontières

Le frontend ne change pas : il continue d'afficher les actions disponibles et
d'envoyer les actions choisies.

Le noyau ne change pas : il continue de manipuler l'état et d'appliquer les
commandes.

Le Java n'est pas réécrit : la passe T23 évite volontairement Drools/Kogito et
ne remplace pas l'architecture BRE.

## Suite Prévue

BRE T24 doit démontrer une skin dérivée qui change une règle en modifiant la
configuration, pas le noyau ni l'UI.
