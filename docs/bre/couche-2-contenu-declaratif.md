# Couche 2 — contenu déclaratif des skins poweruser

## 1. Intention

Ce document explore la couche 2 du modèle de skins poweruser du jeu **Conseil des ministres**.

La couche 1 a permis de formaliser le guide général du scénario : identité, parent, présentation, paramètres simples et conditions générales.

La couche 2 vise le contenu jouable :

- cartes ;
- événements ;
- messages.

L’objectif n’est pas encore d’implémenter toute la mécanique. L’objectif est d’éprouver les hypothèses d’architecture sur :

- l’héritage ;
- la surcharge ;
- la validation ;
- la publication ;
- le versionnement ;
- la refactorisation assistée.

Cette couche est un bon banc d’essai parce qu’elle force à traiter les vrais problèmes de composition : ajout, remplacement, retrait, conflit, diagnostic et publication résolue.

---

## 2. Hypothèse structurante

L’hypothèse privilégiée est la suivante :

> Une skin overlay est un artefact de création.
> Une skin publiée est un artefact résolu, validé et versionné.
> L’héritage est résolu au moment de la publication, non au runtime.

Cela signifie :

- le poweruser travaille dans un brouillon ou une candidate overlay ;
- l’overlay exprime seulement ce qu’il personnalise ;
- la publication lit l’overlay et son parent ;
- la publication résout l’héritage ;
- la publication produit une skin autonome, validée et versionnée ;
- le runtime consomme la skin publiée sans devoir recomposer dynamiquement l’héritage.

Formule synthétique :

```text
brouillon overlay
  → diagnostic créateur
candidate overlay
  → publication = résolution héritage + validation + versionnement
skin publiée résolue
  → runtime simple
```

---

## 3. Cycle de vie d’une skin

Une skin peut exister dans trois états.

| État | Emplacement recommandé | Statut | Rôle |
|---|---|---|---|
| Brouillon | dossier externe ou espace monté Docker | non versionné | élaboration et diagnostic créateur |
| Candidate | branche dédiée ou espace de validation | testée | revue avant publication |
| Publiée | `services/cabinet/skins/<skin_id>/` ou catalogue officiel futur | versionnée | skin intégrée au projet |

`services/cabinet/skins/` n’est pas l’espace naturel de brouillon. C’est l’espace des skins intégrées ou publiées.

La destination publiée ne devrait pas être choisie librement par le poweruser. Elle devrait être dérivée par la commande de publication à partir de `skin.id` et de la politique du projet.

---

## 4. Pourquoi explorer la couche 2 maintenant

La couche 1 est trop simple pour trancher les décisions d’héritage.

La couche 2 révèle les enjeux réels :

- ajouter un élément ;
- remplacer un élément hérité ;
- retirer un élément hérité ;
- détecter les collisions d’identifiants ;
- diagnostiquer les changements ;
- publier un résultat résolu ;
- conserver la traçabilité ;
- préparer la refactorisation si le parent évolue.

Les cartes, événements et messages sont assez simples pour être compréhensibles, mais assez riches pour éprouver l’architecture.

---

## 5. Familles de contenu

### 5.1 Cartes

Les cartes définissent les actions ou leviers politiques disponibles aux joueurs.

Une carte peut contenir :

- `id` ;
- `nom` ;
- `type` ;
- `copies` ;
- `cout_attention` ;
- `cout_cp` ;
- `description` ;
- `effets`.

Exemple de carte résolue :

```yaml
- id: MES_PLAN_SOCIAL
  nom: Plan social
  type: mesure
  copies: 2
  cout_attention: 1
  cout_cp: 1
  description: >
    Améliore l’axe social au prix d’une dépense supplémentaire.
  effets:
    - op: axes.delta
      axe: social
      delta: 2
    - op: eco.delta_depenses
      delta: 1
```

### 5.2 Événements

Les événements définissent les chocs externes ou les circonstances qui affectent le mandat.

Un événement peut contenir :

- `id` ;
- `nom` ;
- `poids` ;
- `description` ;
- `effets`.

Exemple :

```yaml
- id: EVT_CRISE_ENERGETIQUE
  nom: Crise énergétique mondiale
  poids: 1
  description: >
    Une hausse brutale des prix de l’énergie fragilise l’économie.
  effets:
    - op: axes.delta
      axe: economique
      delta: -2
    - op: eco.delta_depenses
      delta: 1
```

### 5.3 Messages

Les messages rendent la skin compréhensible pour le joueur.

Ils peuvent servir à :

- expliquer les phases ;
- expliquer les refus d’action ;
- produire un récit ;
- contextualiser une fin de partie ;
- personnaliser le ton du scénario.

Exemple :

```yaml
messages:
  programme_ouvert: >
    Le programme du cabinet est ouvert.

  capital_politique_insuffisant: >
    Cette action exige davantage de capital politique.

  crise_multiple: >
    Le gouvernement tombe sous l’effet de crises simultanées.
```

---

## 6. Syntaxe overlay proposée

Une skin overlay ne devrait pas recopier tout le contenu parent. Elle devrait indiquer ses opérations.

### 6.1 Cartes

```yaml
cartes:
  heriter: true

  ajouter:
    - id: MES_TRANSITION_CLIMATIQUE
      nom: Transition climatique
      type: mesure
      copies: 2
      cout_attention: 2
      cout_cp: 1
      description: >
        Investir dans la transition écologique.
      effets:
        - op: axes.delta
          axe: environnement
          delta: 2
        - op: eco.delta_depenses
          delta: 1

  remplacer:
    - id: MES_PLAN_SOCIAL
      cout_cp: 2
      description: >
        Le plan social est maintenu, mais devient plus coûteux politiquement
        dans un contexte de tension budgétaire et climatique.

  retirer:
    - MES_BAISSE_IMPOTS
```

### 6.2 Événements

```yaml
evenements:
  heriter: true

  ajouter:
    - id: EVT_CANICULE_HISTORIQUE
      nom: Canicule historique
      poids: 2
      description: >
        Une canicule prolongée met la pression sur les services publics.
      effets:
        - op: axes.delta
          axe: environnement
          delta: -2
        - op: axes.delta
          axe: social
          delta: -1
        - op: eco.delta_depenses
          delta: 1
```

### 6.3 Messages

Les messages peuvent être fusionnés par clé.

```yaml
messages:
  programme_ouvert: >
    Le programme climatique du cabinet est ouvert.

  capital_politique_insuffisant: >
    Cette mesure exige un capital politique plus élevé dans le contexte climatique.
```

---

## 7. Sémantique d’héritage

### 7.1 Collections par identifiant

Les cartes et événements sont des collections par `id`.

L’overlay doit utiliser des opérations explicites :

| Opération | Sens |
|---|---|
| `heriter: true` | conserver la collection parente |
| `ajouter` | ajouter un nouvel élément |
| `remplacer` | remplacer ou surcharger un élément hérité |
| `retirer` | retirer un élément hérité |

### 7.2 Messages par clé

Les messages sont une table clé-valeur.

La sémantique cible est la fusion par clé :

- une clé absente dans l’overlay est héritée ;
- une clé présente dans l’overlay remplace la clé parente ;
- une nouvelle clé est ajoutée.

### 7.3 Remplacement partiel ou complet

Pour les collections complexes, il faudra décider si `remplacer` signifie :

1. remplacement complet de l’élément ;
2. remplacement partiel champ par champ.

Hypothèse privilégiée pour la couche 2 :

> `remplacer` applique une surcharge champ par champ, tout en conservant les champs hérités non redéfinis.

Exemple :

Parent :

```yaml
- id: MES_PLAN_SOCIAL
  nom: Plan social
  type: mesure
  copies: 2
  cout_attention: 1
  cout_cp: 1
```

Overlay :

```yaml
remplacer:
  - id: MES_PLAN_SOCIAL
    cout_cp: 2
```

Résultat publié :

```yaml
- id: MES_PLAN_SOCIAL
  nom: Plan social
  type: mesure
  copies: 2
  cout_attention: 1
  cout_cp: 2
```

Cette décision devra être validée avant implémentation.

---

## 8. Publication résolue

La publication devrait produire une skin autonome.

Exemple : `mandat_climat@1.0.0`.

### 8.1 `skin.yaml` publié

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
    Le cabinet gouverne sous pression climatique accrue.
```

### 8.2 `cartes.yaml` publié

```yaml
cartes:
  - id: MES_PLAN_SOCIAL
    nom: Plan social
    type: mesure
    copies: 2
    cout_attention: 1
    cout_cp: 2
    description: >
      Le plan social est maintenu, mais devient plus coûteux politiquement
      dans un contexte de tension budgétaire et climatique.
    effets:
      - op: axes.delta
        axe: social
        delta: 2
      - op: eco.delta_depenses
        delta: 1

  - id: MES_TRANSITION_CLIMATIQUE
    nom: Transition climatique
    type: mesure
    copies: 2
    cout_attention: 2
    cout_cp: 1
    description: >
      Investir dans la transition écologique.
    effets:
      - op: axes.delta
        axe: environnement
        delta: 2
      - op: eco.delta_depenses
        delta: 1
```

`MES_BAISSE_IMPOTS` est absente parce qu’elle a été retirée.

### 8.3 `evenements.yaml` publié

```yaml
evenements:
  - id: EVT_CRISE_ENERGETIQUE
    nom: Crise énergétique mondiale
    poids: 1
    description: >
      Une hausse brutale des prix de l’énergie fragilise l’économie.
    effets:
      - op: axes.delta
        axe: economique
        delta: -2
      - op: eco.delta_depenses
        delta: 1

  - id: EVT_CANICULE_HISTORIQUE
    nom: Canicule historique
    poids: 2
    description: >
      Une canicule prolongée met la pression sur les services publics.
    effets:
      - op: axes.delta
        axe: environnement
        delta: -2
      - op: axes.delta
        axe: social
        delta: -1
      - op: eco.delta_depenses
        delta: 1
```

### 8.4 `messages.yaml` publié

```yaml
messages:
  programme_ouvert: >
    Le programme climatique du cabinet est ouvert.

  capital_politique_insuffisant: >
    Cette mesure exige un capital politique plus élevé dans le contexte climatique.

  crise_multiple: >
    Le gouvernement tombe sous l’effet de crises simultanées.
```

---

## 9. Métadonnées de publication

Une publication devrait produire un fichier de traçabilité.

Nom proposé :

```text
publication.yaml
```

Exemple :

```yaml
publication:
  skin_id: mandat_climat
  version: 1.0.0
  statut: publiee
  heritage_resolu: true

  parent:
    skin_id: debut_mandat_bre
    version: v1
    hash: sha256:PARENT_HASH_EXEMPLE

  overlay:
    skin_id: mandat_climat
    version: 0.1.0
    hash: sha256:OVERLAY_HASH_EXEMPLE

  resultat:
    hash: sha256:RESULTAT_HASH_EXEMPLE

  operations:
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
      remplacees: []
      retirees: []

    messages:
      remplaces:
        - programme_ouvert
        - capital_politique_insuffisant

  validations:
    yaml: ok
    marqueurs_a_remplacer: ok
    ids_uniques: ok
    references_effets: ok
    parent_resolu: ok
```

`publication.yaml` n’est pas seulement informatif. Il devient un outil futur pour :

- reproduire la publication ;
- expliquer la provenance ;
- comparer avec une nouvelle version du parent ;
- préparer une refactorisation assistée.

---

## 10. Validation avant publication

La publication doit refuser les cas incohérents.

Exemples de validations :

| Validation | Raison |
|---|---|
| aucun marqueur `A_REMPLACER_*` | éviter de publier un gabarit non personnalisé |
| parent existe | éviter un héritage cassé |
| id unique | éviter collisions de cartes ou événements |
| `ajouter` ne vise pas un id existant | éviter ambiguïté |
| `remplacer` vise un id existant | éviter surcharge sans cible |
| `retirer` vise un id existant | éviter suppression fantôme |
| effets reconnus | éviter des commandes inexécutables |
| axes référencés existants | éviter des effets incohérents |
| YAML valide | éviter erreur de parsing |
| version publiée définie | assurer la traçabilité |

Ces validations devraient appartenir à une future commande de publication ou de validation de candidate.

---

## 11. Versionnement

La publication doit gérer les versions.

### 11.1 Version overlay

L’overlay peut avoir sa propre version de travail :

```yaml
skin:
  id: mandat_climat
  version: 0.1.0
```

### 11.2 Version publiée

La publication produit une version stable :

```yaml
publication:
  version: 1.0.0
```

### 11.3 Version du parent

La publication doit enregistrer la version du parent :

```yaml
parent:
  skin_id: debut_mandat_bre
  version: v1
```

### 11.4 Hashs

Les hashs permettent de figer la traçabilité :

- hash du parent ;
- hash de l’overlay ;
- hash du résultat publié.

Cela permet de savoir si une refactorisation est nécessaire lorsque le parent évolue.

---

## 12. Refactorisation assistée

Si l’héritage est résolu à la publication, une skin publiée ne change pas automatiquement lorsque son parent évolue.

C’est souhaitable pour la reproductibilité, mais cela crée un besoin futur :

> aider le créateur à rejouer son overlay sur une nouvelle version du parent.

Commande future possible :

```bash
python -m services.cabinet.outils.refactoriser_skin \
  --overlay /skins-candidates/mandat_climat \
  --nouveau-parent debut_mandat_bre@v2
```

Sortie attendue :

```text
Refactorisation proposée : mandat_climat

Ancien parent :
- debut_mandat_bre@v1

Nouveau parent :
- debut_mandat_bre@v2

Changements héritables :
- cartes ajoutées : 3
- événements ajoutés : 2
- messages corrigés : 4

Conflits :
- MES_PLAN_SOCIAL modifiée dans le parent et remplacée dans l’overlay
- message programme_ouvert modifié dans le parent et remplacé dans l’overlay

Décision requise :
- conserver la version overlay
- accepter la version parent
- fusionner manuellement
```

La refactorisation assistée n’est pas à implémenter maintenant. Elle est une conséquence du modèle de publication résolue.

---

## 13. Événements de gouvernance de skins

Si une skin parente évolue, le système pourra produire des événements de gouvernance destinés aux skins candidates ou publiées concernées.

Exemples :

```text
parent_skin.updated
parent_skin.deprecated
parent_skin.rule_changed
parent_skin.card_added
parent_skin.card_removed
parent_skin.breaking_change
```

Ces événements ne sont pas des événements de jeu. Ils appartiennent à la gouvernance des skins.

Ils pourraient alimenter plus tard :

- un tableau de bord de skins ;
- un rapport de refactorisation ;
- une notification aux mainteneurs ;
- une commande de comparaison.

---

## 14. Impact sur les outils CLI futurs

Les commandes futures pourraient être structurées ainsi :

| Commande | Rôle |
|---|---|
| `diagnostiquer_skin` | lire et expliquer un brouillon ou overlay |
| `valider_skin` | vérifier qu’une candidate peut être publiée |
| `publier_skin` | résoudre l’héritage, versionner et produire une skin publiée |
| `comparer_skins` | comparer parent, overlay et résultat publié |
| `refactoriser_skin` | rejouer un overlay sur un parent plus récent |

La destination de publication ne devrait pas être librement choisie par le poweruser. Elle devrait être dérivée de `skin.id` et de la politique de publication.

À court terme, les skins publiées peuvent continuer d’être découvertes par packages ou dossiers. Un catalogue explicite n’est pas obligatoire maintenant.

Toutefois, encapsuler la publication dans une commande permettra d’ajouter un catalogue plus tard sans changer le geste du créateur.

---

## 15. Questions ouvertes

### 15.1 Où conserver l’overlay source ?

Hypothèse actuelle :

- le poweruser conserve son overlay source dans l’espace candidate ;
- la publication produit une skin résolue ;
- le résultat publié contient les métadonnées nécessaires à la traçabilité.

Question ouverte :

- faut-il aussi archiver une copie de l’overlay source dans la skin publiée ?

### 15.2 Quelle granularité pour le remplacement ?

Pour les cartes et événements, `remplacer` devrait-il :

- remplacer seulement les champs fournis ;
- ou remplacer l’élément complet ?

Hypothèse actuelle :

- surcharge champ par champ.

À confirmer avant implémentation.

### 15.3 Comment gérer les effets non reconnus ?

Les effets comme `axes.delta`, `eco.delta_depenses` ou `joueur.capital.delta` doivent être validés.

Question :

- la liste des opérations valides vient-elle du moteur ?
- d’un schéma partagé ?
- d’un registre de commandes ?

### 15.4 Quelle version pour la skin parente ?

La publication doit figer la version et idéalement le hash du parent.

Question :

- comment versionner les skins parentes historiques qui n’ont pas encore de version formelle ?

### 15.5 Catalogue explicite ou découverte de dossiers ?

À court terme, la découverte par dossiers est suffisante.

Question future :

- quand un catalogue explicite devient-il nécessaire ?

---

## 16. Conclusion

La couche 2 confirme l’intérêt d’une publication résolue.

Les overlays restent légers et lisibles pour le créateur. La publication produit un artefact autonome, validé et versionné pour l’exécution.

Cette séparation permet :

- un runtime plus simple ;
- une validation figée dans le temps ;
- une meilleure reproductibilité ;
- une publication assistée ;
- une future refactorisation accompagnée lorsque les parents évoluent.

La prochaine étape logique sera de transformer cette exploration en incréments : diagnostic enrichi de contenu, validation de candidate, puis publication résolue.
