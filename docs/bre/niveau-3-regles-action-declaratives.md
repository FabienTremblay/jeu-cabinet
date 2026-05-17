# Niveau 3 — règles d’action déclaratives

Point d’entrée recommandé de la documentation BRE :
[`README.md`](README.md).

## Statut

Ce document prépare l’issue T35 :
`BRE T35 — Formaliser les règles d’action déclaratives niveau 3`.

Il définit le contrat minimal cible de `regles/validation_actions.yaml` pour le
niveau 3. Ce contrat reste documentaire : il ne remplace pas encore
`validation_cartes.yaml` dans le runtime.

## Principe général à respecter

Les règles d’action déclaratives devront respecter le principe général :
[`Principe directeur — progression de complexité poweruser`](modele-heritage-skin-poweruser.md#principe-directeur--progression-de-complexité-poweruser).

Conséquence pour T35 : `validation_actions.yaml` ne doit pas devenir un langage
complet, un script embarqué ou un moteur de règles généraliste. Il doit rester
un dispositif déclaratif, compréhensible, diagnostiquable et validable par un
créateur de skin qui progresse par paliers.

## Définition d’une action

Une action est identifiée par `op`.

`op` représente une opération métier ou ludique appelée par le runtime. Cette
opération décrit ce que le joueur, le système ou un acteur de jeu cherche à
faire.

Exemples :

- `programme.engager_carte` ;
- `joueur.passer` ;
- `vote.exprimer` ;
- `opposition.jouer_contre_mesure` ;
- `conference_presse.declarer`.

`op` n’identifie pas une règle. Plusieurs règles peuvent viser la même action si
leurs `id` sont distincts et si leur ordre d’application est défini clairement.

## Définition d’une règle d’action

Une règle d’action est identifiée par `id`.

Une règle vise une action avec `op`.

`id` sert à :

- diagnostiquer la règle ;
- valider une candidate ;
- remplacer une règle héritée ;
- retirer une règle héritée ;
- tracer les opérations dans une publication résolue.

`op` ne doit pas servir d’identifiant unique de règle. Il indique seulement
l’action concernée.

## Forme YAML minimale cible

Le format cible de niveau 3 est `regles/validation_actions.yaml`.

Exemple minimal :

```yaml
validation_actions:
  heriter: true

  remplacer:
    - id: engager_carte_cout_standard
      op: programme.engager_carte
      description: Valide et applique le coût d’engagement d’une carte.

      conditions:
        - id: attention_suffisante
          champ: joueur.attention_dispo
          operateur: ">="
          valeur: carte.cout_attention
          sinon: attention_insuffisante

        - id: capital_suffisant
          champ: joueur.capital_politique
          operateur: ">="
          valeur: carte.cout_cp
          sinon: capital_politique_insuffisant

      couts:
        - op: joueur.attention.delta
          delta: -carte.cout_attention

        - op: joueur.capital.delta
          delta: -carte.cout_cp

      messages_refus:
        attention_insuffisante: >
          Cette action exige davantage d’attention disponible.
        capital_politique_insuffisant: >
          Cette action exige davantage de capital politique.
```

Ce format est une cible. Le fichier actuel `validation_cartes.yaml` reste le
support de la démonstration existante tant qu’une migration explicite n’est pas
faite.

## Conditions, coûts et effets

Les sections d’une règle doivent rester lisibles.

- `conditions` : prérequis à satisfaire avant l’action.
- `couts` : effets obligatoires associés au paiement de l’action.
- `effets` : effets immédiats optionnels produits par l’action.

Pour le niveau 3 minimal, `couts` peut être traité comme une catégorie
spécialisée d’effet. La section reste toutefois séparée pour que le créateur de
skin comprenne immédiatement ce qui est payé et ce qui est produit.

## Opérateurs acceptés

Le niveau minimal devrait accepter seulement des opérateurs simples :

- `==`
- `!=`
- `>`
- `>=`
- `<`
- `<=`
- `exists`
- `not_exists`

Les opérateurs suivants sont à discuter ou à reporter :

- `in`
- `not_in`

Le modèle ne doit pas accepter d’expressions arbitraires. Une condition ne doit
pas devenir du code déguisé.

## Chemins de champs

Les chemins de champs doivent appartenir à un registre contrôlé selon l’action.

Exemples de chemins simples :

- `joueur.attention_dispo`
- `joueur.capital_politique`
- `carte.cout_attention`
- `carte.cout_cp`
- `etat.phase`
- `etat.tour`

Chaque `op` devrait éventuellement déclarer les familles de champs autorisées.
Par exemple, `programme.engager_carte` peut autoriser des champs `joueur.*`,
`carte.*` et `etat.*`, sans autoriser toute l’arborescence de l’état.

Cette restriction garde le modèle diagnostiquable et limite les erreurs
silencieuses.

## Héritage des règles d’action

L’héritage se fait par `id` de règle.

- `ajouter` ajoute une nouvelle règle par `id`.
- `remplacer` remplace une règle existante par `id`.
- `retirer` retire une règle existante par `id`.

Le remplacement par `op` est exclu du niveau 3 minimal, car plusieurs règles
peuvent viser la même action.

Plusieurs règles peuvent viser la même `op`, mais seulement si leurs `id` sont
distincts. L’ordre ou la priorité de règles multiples doit être explicite dans
un incrément futur. Il ne doit pas dépendre d’un ordre implicite difficile à
diagnostiquer.

## Messages de refus

Au niveau 3 initial, les messages de refus peuvent être déclarés localement dans
la règle. Cette approche favorise la compréhension immédiate par le créateur.

Plus tard, ces messages pourront être factorisés dans `messages.yaml`.

Une règle doit toujours permettre un diagnostic clair si une condition peut
refuser l’action mais ne fournit pas de clé `sinon`, ou si la clé `sinon` ne
correspond à aucun message connu.

## Validations candidates futures

La validation candidate devrait progressivement ajouter les contrôles suivants :

- `id` obligatoire ;
- `id` unique ;
- `op` obligatoire ;
- `op` connue ou déclarée dans un registre ;
- conditions bien formées ;
- opérateur reconnu ;
- champ reconnu ou plausible selon l’action ;
- valeur compatible ;
- `sinon` présent si la condition peut refuser ;
- message de refus présent ;
- coût ou effet avec `op` reconnue ;
- aucun marqueur `A_REMPLACER_*` ;
- aucune section inconnue ;
- pas de remplacement d’une règle inexistante ;
- pas de retrait d’une règle inexistante.

Les validations qui dépendent de la skin parente peuvent rester différées tant
que la publication résolue n’est pas implémentée.

## Publication résolue

La publication résolue devra produire une version finale des règles d’action.

L’héritage doit être résolu à la publication, pas au runtime. Le runtime devrait
consommer une skin publiée déjà résolue.

`publication.yaml` devra lister les règles :

- ajoutées ;
- remplacées ;
- retirées.

Il devra aussi tracer les validations passées, la version de l’overlay et la
version du parent utilisées pour produire le résultat.

## Migration depuis validation_cartes.yaml

`validation_cartes.yaml` est une preuve fonctionnelle ciblée sur
`programme.engager_carte`.

La migration future vers `validation_actions.yaml` devrait être explicite et
progressive :

- garder `validation_cartes.yaml` tant que le runtime actuel en dépend ;
- documenter l’équivalence entre la règle existante et sa forme cible ;
- ajouter les diagnostics et validations candidates avant tout remplacement ;
- éviter une double source de vérité non documentée.

Le futur `validation_actions.yaml` doit généraliser le modèle sans transformer
la règle actuelle en langage complet.

## Limites de cette passe

Cette passe exclut :

- le runtime ;
- le `rules-service` ;
- `publier_skin` ;
- l’interprétation réelle de `validation_actions.yaml` ;
- un moteur de règles généraliste ;
- Drools ;
- DMN ;
- les scripts ;
- les callbacks ;
- les expressions Python ;
- les boucles.
