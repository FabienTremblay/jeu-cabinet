# Inventaire Des Skins Et Overlays D’élaboration

Ce document classe les dossiers actuellement présents dans
`services/cabinet/skins/` afin d’éviter de confondre skins publiées, fixtures de
test, démonstrateurs et exemples contrôlés.

Il s’agit d’un inventaire documentaire. Cette passe ne déplace et ne supprime
aucune skin.

## Décision Générale

`services/cabinet/skins/` contient aujourd’hui plusieurs catégories :

- skins historiques ou fonctionnelles du noyau Cabinet ;
- fixtures utilisées par les tests ;
- démonstrateurs BRE ;
- overlays d’exemple pour le diagnostic poweruser.

Aucune skin issue du parcours overlay n’est encore une skin publiée résolue. La
publication résolue reste conçue dans
[`publication-skin-resolue.md`](publication-skin-resolue.md), mais non
implémentée.

## Synthèse

| Dossier | Statut proposé | Rôle actuel | Action recommandée |
| --- | --- | --- | --- |
| `minimal` | fixture de test noyau | base légère pour tests Cabinet | conserver pour l’instant |
| `debut_mandat` | skin historique fonctionnelle | scénario Python de départ | conserver pour compatibilité |
| `Mandat_difficile` | démonstrateur historique à clarifier | variante ancienne, nom non normalisé | documenter puis décider plus tard |
| `debut_mandat_bre` | référence provisoire BRE | base de démonstration BRE actuelle | conserver comme référence provisoire |
| `mandat_fragile` | démonstrateur poweruser historique | prouve une différence par YAML | conserver tant que la preuve T24 sert |
| `exemple_mandat_austerite_overlay` | exemple contrôlé niveau 1 | diagnostic `skin.yaml` | conserver comme exemple/test |
| `exemple_mandat_climat_overlay` | exemple contrôlé couche 2 | diagnostic contenu + validation candidate | conserver comme exemple/test |

## Détail Par Skin Ou Overlay

### `minimal`

Statut : fixture de test noyau.

Rôle :

- fournit une skin compacte pour les tests du noyau Cabinet ;
- utilisée par plusieurs tests de phases, cartes, decks, actions et manager ;
- n’est pas une démonstration BRE poweruser.

Utilisation par les tests : oui.

Décision actuelle :

- rester dans `services/cabinet/skins/` ;
- ne pas déplacer dans cette passe ;
- ne pas présenter comme skin publiée poweruser.

Action future possible :

- clarifier plus tard si les fixtures de test doivent rester dans
  `services/cabinet/skins/` ou être isolées dans un espace de tests.

### `debut_mandat`

Statut : skin historique fonctionnelle.

Rôle :

- scénario de départ Python ;
- sert de base à `debut_mandat_bre` ;
- conserve la compatibilité avec le fonctionnement Cabinet existant.

Utilisation par les tests : indirecte via `debut_mandat_bre` et usages
historiques.

Décision actuelle :

- rester dans `services/cabinet/skins/` ;
- ne pas confondre avec une skin publiée issue du modèle overlay ;
- servir de référence historique tant que la migration déclarative n’est pas
  terminée.

Action future possible :

- déterminer si elle devient une base officielle, est remplacée par
  `base_conseil_ministres`, ou reste une skin historique.

### `Mandat_difficile`

Statut : démonstrateur historique à clarifier.

Rôle :

- variante ancienne de skin ;
- le nom de dossier utilise une majuscule et ne suit pas les conventions récentes
  de `skin_id` ;
- n’est pas intégré au parcours BRE poweruser actuel.

Utilisation par les tests : aucune référence directe identifiée dans les tests
Cabinet ciblés.

Décision actuelle :

- ne pas déplacer ni supprimer dans cette passe ;
- ne pas présenter comme skin publiée ;
- la classer comme artefact historique à revoir.

Action future possible :

- décider si elle doit être supprimée, renommée, migrée ou déplacée vers un
  espace d’archives/exemples.

### `debut_mandat_bre`

Statut : référence provisoire BRE.

Rôle :

- skin de démonstration BRE actuelle ;
- base provisoire en attendant une future `base_conseil_ministres` ;
- contient la règle YAML actuelle `regles/validation_cartes.yaml` ;
- utilisée par le contrat de routage, les facts minimaux et les tests de
  chargement BRE.

Utilisation par les tests : oui.

Décision actuelle :

- rester dans `services/cabinet/skins/` ;
- conserver son rôle de référence provisoire BRE ;
- ne pas la considérer comme résultat d’une publication résolue.

Action future possible :

- migrer progressivement vers le modèle cible d’héritage et publication ;
- remplacer à terme son rôle de parent par `base_conseil_ministres`.

### `mandat_fragile`

Statut : démonstrateur poweruser historique.

Rôle :

- skin dérivée de `debut_mandat_bre` ;
- démontre qu’une règle YAML peut modifier le comportement métier sans UI ni
  Java spécifique ;
- correspond à la preuve T24.

Utilisation par les tests : oui.

Décision actuelle :

- rester dans `services/cabinet/skins/` tant que la preuve poweruser s’appuie
  sur elle ;
- documenter qu’elle n’est pas une skin publiée résolue ;
- ne pas la supprimer dans cette passe.

Action future possible :

- la transformer en candidate/published example lorsque `publier_skin` existera ;
- ou la déplacer vers un espace d’exemples si elle cesse d’être nécessaire aux
  tests.

### `exemple_mandat_austerite_overlay`

Statut : exemple contrôlé niveau 1.

Rôle :

- overlay minimal contenant seulement `skin.yaml` ;
- sert à démontrer la lecture de `skin.yaml` et le diagnostic des champs
  déclarés ;
- utilisé dans les tests du diagnostic créateur.

Utilisation par les tests : oui.

Décision actuelle :

- rester dans `services/cabinet/skins/` pour que la commande par identifiant
  fonctionne dans Docker après build ;
- ne pas présenter comme skin publiée ou jouable ;
- préciser qu’il s’agit d’un exemple contrôlé.

Action future possible :

- déplacer vers un espace `fixtures` ou `docs/bre/exemples` si le diagnostic
  sait lire des exemples externes de façon standardisée.

### `exemple_mandat_climat_overlay`

Statut : exemple contrôlé couche 2.

Rôle :

- overlay contenant `skin.yaml`, `cartes.yaml`, `evenements.yaml` et
  `messages.yaml` ;
- sert à démontrer le diagnostic des contenus déclaratifs de couche 2 ;
- sert à valider la commande non destructive de candidate.

Utilisation par les tests : oui.

Décision actuelle :

- rester dans `services/cabinet/skins/` pour soutenir les tests et les commandes
  Docker documentées ;
- ne pas présenter comme skin publiée ou jouable ;
- préciser que la publication résolue n’est pas encore exécutée.

Action future possible :

- devenir un exemple de candidate lorsque `publier_skin` existera ;
- ou être déplacé vers des fixtures documentées si les chemins des tests sont
  adaptés.

## Décisions De Déplacement Différées

Aucun déplacement n’est fait maintenant.

Décisions à reprendre plus tard :

- faut-il créer `services/cabinet/tests/fixtures/skins/` pour les overlays de
  tests ?
- faut-il créer `docs/bre/exemples/` pour les exemples de créateur ?
- faut-il conserver les exemples dans `services/cabinet/skins/` pour la
  validation Docker par identifiant ?
- faut-il archiver ou supprimer `Mandat_difficile` ?
- faut-il définir un marqueur explicite pour distinguer une skin publiée d’un
  overlay d’exemple ?

## Règle De Lecture

Tant que `publication.yaml` n’existe pas et que `heritage_resolu: true` n’est
pas produit par une commande de publication, une skin ou un overlay ne doit pas
être supposé publié.

Les documents de création et diagnostic doivent continuer à parler d’overlays,
de brouillons, de candidates ou d’exemples contrôlés lorsqu’il ne s’agit pas
d’une skin publiée résolue.
