# Architecture Fonctionnelle BRE

## Intention

La démonstration BRE `poweruser skin` sépare progressivement trois niveaux :

- le noyau Cabinet conserve l'état et applique les commandes ;
- le `rules-service` Java reste le point d'entrée BRE et le routeur des moteurs ;
- le skin porte les règles ajustables par configuration.

Le terme BRE désigne ici la capacité fonctionnelle de déléguer ou configurer
des règles hors du noyau. Il ne signifie pas encore Drools/Kogito.

## Découpage Actuel

Pour `debut_mandat_bre` et ses skins dérivées :

- `analyse_skin` route vers la bonne famille de règles ;
- `etat_min` expose les facts minimaux ;
- `validation_cartes.yaml` décrit la validation et les coûts de carte ;
- un mini-interpréteur Python applique cette règle ;
- `mandat_fragile` démontre qu'une skin peut remplacer ce YAML pour changer le
  comportement sans changer l'UI, le noyau ou le Java.

## Responsabilités

### BRE Fonctionnel

Le BRE fonctionnel regroupe le contrat de routage, les facts minimaux et le
point où les règles externes au noyau sont appliquées.

### Règles Déclaratives De Skin

Les fichiers `regles/*.yaml` appartiennent aux skins. Ils portent les choix
modifiables par un créateur de skin.

### Interpréteur YAML Python Actuel

L'interpréteur Python est une étape pragmatique de démonstration. Il prouve le
modèle déclaratif sans imposer un moteur de règles complet.

### Rules-Service Java

Le `rules-service` conserve le routage et les endpoints BRE. Il n'a pas reçu de
code spécifique à `mandat_fragile`.

### Piste Future Drools/DMN

Drools/DMN reste une option future pour industrialiser ou centraliser
l'interprétation des règles. Cette branche ne l'introduit pas.

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

Le scénario complet est décrit dans `docs/bre/demo-poweruser-bre.md`.
