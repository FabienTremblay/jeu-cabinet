# Publication Résolue D’une Skin

Point d’entrée recommandé de la documentation BRE :
[`README.md`](README.md).

## Objectif

Ce document définit le processus cible de publication résolue d’une skin
poweruser.

Il s’agit d’une conception. Aucune commande `publier_skin` n’est encore
implémentée dans le dépôt.

Hypothèse retenue :

> Une skin overlay est un artefact de création.
> Une skin publiée est un artefact résolu, validé et versionné.
> L’héritage est résolu au moment de la publication, pas au runtime.

## Cycle De Vie

Une skin suit trois états.

| État | Rôle | Emplacement typique |
| --- | --- | --- |
| Brouillon | élaboration par le créateur | dossier externe ou montage Docker |
| Candidate | overlay validé et prêt pour revue | branche dédiée ou espace de validation |
| Publiée | artefact autonome, résolu et versionné | `services/cabinet/skins/<skin_id>/` ou catalogue futur |

Le brouillon et la candidate expriment uniquement les personnalisations. La skin
publiée contient le résultat complet attendu par le runtime.

## Future Commande `publier_skin`

La commande cible pourrait ressembler à ceci :

```bash
python -m services.cabinet.outils.publier_skin \
  --skin-dir /chemin/vers/candidate \
  --version 1.0.0
```

La commande devra :

1. lire la candidate overlay ;
2. exécuter la validation candidate ;
3. lire la skin parente ;
4. valider les opérations dépendantes du parent ;
5. résoudre l’héritage ;
6. produire une skin publiée autonome ;
7. écrire `publication.yaml` ;
8. dériver la destination depuis `skin.id` et la politique du projet ;
9. refuser les cas invalides sans modifier la destination.

La commande sera non interactive par défaut. Les modes de remplacement ou de
mise à jour d’une publication existante devront être explicites.

## Destination Publiée

Le créateur ne choisit pas librement la destination publiée.

La destination est dérivée par le système. À court terme, elle peut être :

```text
services/cabinet/skins/<skin_id>/
```

À plus long terme, elle peut être une entrée de catalogue officiel.

Ce principe évite :

- les doublons de destination ;
- les publications dans des emplacements arbitraires ;
- les divergences entre `skin.id`, le dossier et la découverte runtime ;
- les scripts locaux difficiles à reproduire.

## Structure Cible D’une Skin Publiée

Exemple indicatif :

```text
services/cabinet/skins/mandat_climat/
  skin.yaml
  cartes.yaml
  evenements.yaml
  messages.yaml
  publication.yaml
```

La skin publiée est autonome : elle ne devrait pas exiger de recomposer
l’héritage au runtime.

Exemple de `skin.yaml` publié :

```yaml
skin:
  id: mandat_climat
  nom: Mandat climatique
  version: 1.0.0
  difficulte: intermediaire
  herite_de: null
  heritage_resolu: true

presentation:
  pitch: >
    Le cabinet gouverne sous pression climatique.
```

Les fichiers `cartes.yaml`, `evenements.yaml` et `messages.yaml` publiés
contiennent les contenus résolus : éléments hérités conservés, ajouts appliqués,
remplacements appliqués et retraits retirés.

## `publication.yaml`

`publication.yaml` trace la publication. Il doit permettre de comprendre et de
reproduire le résultat.

Structure cible :

```yaml
publication:
  skin_id: mandat_climat
  version: 1.0.0
  statut: publiee
  heritage_resolu: true

  publie_le: "2026-05-15T00:00:00Z"
  publicateur: non_renseigne

  parent:
    skin_id: debut_mandat_bre
    version: v1
    hash: sha256:PARENT_HASH_FUTUR

  overlay:
    skin_id: mandat_climat
    version: 0.1.0
    hash: sha256:OVERLAY_HASH_FUTUR

  resultat:
    hash: sha256:RESULTAT_HASH_FUTUR

  destination:
    type: dossier
    chemin: services/cabinet/skins/mandat_climat

  operations_appliquees:
    cartes:
      ajoutees:
        - MES_TRANSITION_CLIMATIQUE
      remplacees:
        - MES_PLAN_SOCIAL
      retirees:
        - MES_BAISSE_IMPOTS

    evenements:
      ajoutees:
        - EVT_CANICULE_HISTORIQUE
      remplacees:
        - EVT_CRITIQUE_OPPOSITION
      retirees:
        - EVT_SONDAGE_FAVORABLE

    messages:
      personnalises:
        - programme_ouvert
        - capital_politique_insuffisant

  validations_passees:
    skin_yaml: ok
    marqueurs_a_remplacer: ok
    ids_uniques: ok
    parent_existe: ok
    operations_parent: ok
    effets_connus: ok
    axes_connus: ok
    destination: ok
```

Les champs `hash` sont indiqués comme futurs. Ils permettront de figer la
traçabilité lorsque la publication sera implémentée.

`publicateur` peut rester `non_renseigne` dans les premiers incréments. La
publication ne doit pas dépendre immédiatement d’un système d’identité complet.

## Conditions De Refus

La publication doit refuser au minimum :

- candidate invalide ;
- parent introuvable ;
- version publiée absente ;
- marqueurs `A_REMPLACER_*` restants ;
- destination déjà existante sans mode remplacement explicite ;
- conflit d’id ;
- opération `ajouter` visant un id déjà hérité ;
- opération `remplacer` visant un id inexistant ;
- opération `retirer` visant un id inexistant ;
- effets non reconnus ;
- axes référencés inconnus ;
- incohérence entre `skin.id` et la destination dérivée.

Un refus ne doit pas laisser de publication partielle.

## Catalogue

Un catalogue explicite n’est pas obligatoire à court terme.

La découverte par dossiers ou packages reste acceptable pendant la transition.
Toutefois, la publication doit être encapsulée dans une commande afin de pouvoir
ajouter plus tard un catalogue sans changer le geste du créateur.

À terme, le catalogue pourrait enregistrer :

- `skin_id` ;
- version publiée ;
- chemin ou paquet ;
- statut ;
- date de publication ;
- parent ;
- compatibilité moteur ;
- hash de publication.

## Refactorisation Future

Une skin publiée ne change pas automatiquement lorsque sa skin parente évolue.

C’est voulu : la publication doit être reproductible. Si le parent évolue, le
créateur pourra rejouer son overlay source sur un parent plus récent.

Une future commande de refactorisation pourrait comparer :

- l’ancien parent ;
- le nouveau parent ;
- l’overlay source ;
- la publication existante.

Elle devra signaler :

- changements héritables ;
- conflits ;
- règles ou cartes remplacées à revoir ;
- décisions manuelles nécessaires.

## Ménage Futur Des Skins D’élaboration

Les exemples et overlays d’élaboration ne sont pas tous destinés à devenir des
skins publiées.

Avant de merger ou de stabiliser la branche, il faudra décider quoi faire des
skins d’exemple :

- conserver celles qui servent de tests et de documentation ;
- déplacer les brouillons hors de `services/cabinet/skins/` si nécessaire ;
- publier seulement des skins résolues ;
- documenter clairement les exemples non jouables.

Ce ménage doit être fait séparément de la conception de publication.

## Limites Actuelles

Cette passe ne fournit pas encore :

- commande `publier_skin` ;
- résolution effective de l’héritage ;
- calcul de hash ;
- écriture de `publication.yaml` ;
- catalogue ;
- migration des skins existantes ;
- nettoyage des exemples.

La prochaine étape technique sera de découper une implémentation minimale de
publication sans modifier le runtime avant que la structure publiée soit
stabilisée.
