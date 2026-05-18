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

## Catalogue initial des actions

La skin Python historique `services/cabinet/skins/debut_mandat` montre trois
familles à ne pas mélanger :

- actions demandées par un joueur ou l’interface pendant une attente ;
- commandes moteur ou effets produits ;
- signaux, attentes et chorégraphie de phase.

Le niveau 3 de `validation_actions.yaml` concerne d’abord les actions joueur
déclarables. Les autres opérations peuvent inspirer des coûts ou effets, mais
ne deviennent pas automatiquement des actions déclarables.

### Actions joueur déclarables

Ces opérations sont observées dans les procédures d’attente de `debut_mandat`.
Elles constituent le premier noyau plausible de règles d’action déclaratives.

#### `programme.engager_carte`

Intention : engager une carte de la main d’un joueur dans le programme du
cabinet.

Niveau de complexité poweruser : simple, puis conditionnelle.

Champs de contexte admissibles :

- `joueur.attention_dispo` ;
- `joueur.capital_politique` ;
- `joueur.main` ;
- `carte.id` ;
- `carte.cout_attention` ;
- `carte.cout_cp` ;
- `etat.phase` ;
- `etat.sous_phase` ;
- `attente.type`.

Conditions plausibles :

- la carte existe ;
- la carte est dans la main du joueur ;
- le joueur dispose de l’attention requise ;
- le joueur dispose du capital politique requis ;
- l’attente courante autorise l’engagement de carte.

Coûts ou effets plausibles :

- `joueur.attention.delta` ;
- `joueur.capital.delta` ;
- ajout de la carte au programme, par une commande moteur dédiée ou par le
  mécanisme runtime existant.

Messages de refus typiques :

- attention insuffisante ;
- capital politique insuffisant ;
- carte absente de la main ;
- action non disponible dans cette attente.

Limites ou points à décider :

- le déplacement exact de la carte vers le programme reste une responsabilité
  runtime ;
- le registre final doit décider si `main` est consultable directement ou via
  un champ dérivé plus simple.

#### `programme.retirer_carte`

Intention : retirer une carte déjà engagée dans le programme pendant la phase de
confection.

Niveau de complexité poweruser : simple.

Champs de contexte admissibles :

- `joueur.id` ;
- `carte.id` ;
- `programme.cartes` ;
- `etat.phase` ;
- `etat.sous_phase` ;
- `attente.type`.

Conditions plausibles :

- la carte est dans le programme ;
- le joueur est autorisé à retirer cette carte ;
- l’attente courante autorise le retrait.

Coûts ou effets plausibles :

- retour de la carte vers la main ou retrait du programme par le runtime ;
- remboursement éventuel de coûts si une règle l’autorise.

Messages de refus typiques :

- carte absente du programme ;
- joueur non autorisé ;
- retrait non disponible dans cette attente.

Limites ou points à décider :

- la règle de propriété d’une carte engagée doit être explicitée avant de
  généraliser cette action.

#### `joueur.vote.set`

Intention : enregistrer le vote d’un joueur habilité sur le programme.

Niveau de complexité poweruser : conditionnelle.

Champs de contexte admissibles :

- `joueur.peut_voter` ;
- `joueur.vote` ;
- `programme.verdict` ;
- `etat.phase` ;
- `etat.sous_phase` ;
- `attente.type`.

Conditions plausibles :

- le joueur a le droit de vote ;
- l’attente courante est de type `VOTE` ;
- la valeur du vote est dans le domaine autorisé ;
- le vote n’est pas déjà verrouillé.

Coûts ou effets plausibles :

- mise à jour du vote du joueur ;
- confirmation éventuelle par `attente.joueur_recu`.

Messages de refus typiques :

- joueur non habilité à voter ;
- valeur de vote invalide ;
- vote fermé.

Limites ou points à décider :

- le calcul du verdict global ne relève pas du niveau 3 minimal ; il appartient
  à la résolution politique.

#### `attente.joueur_recu`

Intention : indiquer qu’un joueur a terminé sa réponse pour une attente donnée.

Niveau de complexité poweruser : simple.

Champs de contexte admissibles :

- `joueur.id` ;
- `attente.type` ;
- `attente.joueurs_attendus` ;
- `attente.joueurs_recus` ;
- `etat.phase` ;
- `etat.sous_phase`.

Conditions plausibles :

- une attente est active ;
- le joueur est attendu ;
- le type d’attente correspond à la procédure en cours ;
- le joueur n’a pas déjà confirmé.

Coûts ou effets plausibles :

- marquer le joueur comme reçu pour l’attente courante.

Messages de refus typiques :

- aucune attente active ;
- joueur non attendu ;
- confirmation déjà reçue ;
- type d’attente incohérent.

Limites ou points à décider :

- la transition qui suit la complétion de l’attente relève de la chorégraphie,
  pas de la validation d’action niveau 3.

### Commandes moteur et effets produits

Les opérations suivantes sont observées dans `debut_mandat` comme commandes ou
effets produits. Elles peuvent être admissibles dans `couts` ou `effets`, selon
un registre contrôlé, mais elles ne sont pas automatiquement des actions joueur.

- `joueur.attention.delta` ;
- `joueur.capital.delta` ;
- `capital_collectif.delta` ;
- `axes.delta` ;
- `eco.delta_depenses` ;
- `eco.delta_recettes` ;
- `eco.delta_dette` ;
- `programme.reset` ;
- `programme.rejeter` ;
- `programme.verdict.set` ;
- `joueur.vote_droit.set` ;
- `journal` ;
- `tour.increment` ;
- `partie.terminer` ;
- `evt.piocher` ;
- `evt.executer` ;
- `joueur.piocher` ;
- `deck.defausser_main` ;
- `opposition.capital.delta` ;
- `opposition.data.set` ;
- `opposition.data.delta` ;
- `analyse.data.set`.

Une règle d’action peut produire certaines de ces commandes, mais seulement si
la commande est autorisée pour l’action concernée. Par exemple,
`programme.engager_carte` peut produire des coûts joueur, mais ne devrait pas
déclencher librement une fin de partie.

### Signaux, attentes et chorégraphie

Les éléments suivants relèvent surtout de la chorégraphie du jeu ou du niveau 5,
pas du niveau 3 minimal :

- signaux de phase comme `signal.init_tour`, `signal.programme_ouvert`,
  `signal.vote_ouvert`, `signal.resolution_programme`, `signal.fin_tour` ;
- types d’attente comme `ENGAGER_CARTE`, `VOTE`, `PERTURBATION_VOTE` ;
- transitions de sous-phase ;
- arbitrage politique complet ;
- résolution du programme ;
- perturbations avancées du vote.

Ces éléments pourront inspirer des niveaux ultérieurs, mais ils ne doivent pas
être absorbés trop tôt par `validation_actions.yaml`.

## Registre initial des champs contrôlés

Les chemins de champs doivent être contrôlés par action. Le registre initial
peut commencer avec les chemins suivants :

- `joueur.attention_dispo` ;
- `joueur.capital_politique` ;
- `joueur.peut_voter` ;
- `carte.id` ;
- `carte.cout_attention` ;
- `carte.cout_cp` ;
- `programme.verdict` ;
- `etat.phase` ;
- `etat.sous_phase` ;
- `etat.tour` ;
- `attente.type`.

Pour le niveau 3 minimal, le registre doit surtout couvrir :

- `programme.engager_carte` ;
- `programme.retirer_carte` ;
- `joueur.vote.set` ;
- `attente.joueur_recu`.

Chaque action devrait exposer seulement les familles de champs nécessaires à sa
validation. Cette règle évite que `validation_actions.yaml` devienne un accès
libre à tout l’état interne du jeu.

## Leçons tirées de la skin Python debut_mandat

La skin Python historique `debut_mandat` montre un précédent complet du modèle
de jeu. Elle mélange volontairement, dans du code Python, plusieurs niveaux qui
doivent être séparés dans le modèle déclaratif :

1. validation d’une action joueur ;
2. production de coûts ou d’effets ;
3. chorégraphie complète d’une phase ou d’une résolution politique.

T35 concerne surtout les deux premiers niveaux :

- vérifier qu’une action joueur est possible ;
- produire des coûts ou effets simples et contrôlés.

La chorégraphie complète, comme l’ouverture des phases, la résolution du
programme, les perturbations avancées du vote ou l’arbitrage politique global,
appartient à un palier ultérieur de complexité poweruser.

Cette séparation protège la progression de complexité : un créateur peut
personnaliser des règles d’action sans devoir comprendre toute la mécanique de
phase et de résolution.

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
