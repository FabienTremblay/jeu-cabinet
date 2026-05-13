# Architecture Fonctionnelle BRE

## Intention

La démonstration BRE `poweruser skin` sépare progressivement trois niveaux :

- le noyau Cabinet conserve l'état et applique les commandes ;
- le `rules-service` reste le point d'entrée BRE et le routeur des moteurs ;
- le skin porte les règles ajustables par configuration.

## Découpage Actuel

Pour `debut_mandat_bre` et ses skins dérivées :

- `analyse_skin` route vers la bonne famille de règles ;
- `etat_min` expose les facts minimaux ;
- `validation_cartes.yaml` décrit la validation et les coûts de carte ;
- un mini-interpréteur Python applique cette règle ;
- `mandat_fragile` démontre qu'une skin peut remplacer ce YAML pour changer le
  comportement sans changer l'UI, le noyau ou le Java.

## Frontières

Le frontend ne change pas : il continue d'afficher les actions disponibles et
d'envoyer les actions choisies.

Le noyau ne change pas : il continue de manipuler l'état et d'appliquer les
commandes.

Le Java n'est pas réécrit : la passe T23 évite volontairement Drools/Kogito et
ne remplace pas l'architecture BRE.

## Démonstration Poweruser

`mandat_fragile` dérive de `debut_mandat_bre` et rend l'engagement d'une carte
plus exigeant en attention via `regles/validation_cartes.yaml`.
