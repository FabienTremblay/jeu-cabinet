# Modèle d’héritage des skins poweruser

## 1. Intention

Ce document définit le modèle cible pour la création de skins poweruser dans le jeu **Conseil des ministres**.

Il décrit une direction d’architecture et de documentation. Ce modèle n’est pas encore entièrement implémenté dans le dépôt actuel.

État d’implémentation actuel : le dépôt sait maintenant lire un fichier `skin.yaml` minimal pour une skin overlay, reconnaître `skin.id`, `skin.herite_de`, `skin.nom`, `skin.version` et `skin.difficulte`, puis produire un diagnostic lisible des champs déclarés et des familles héritées. Cette étape ne remplace pas encore `config.py`, ne supprime pas `regles.py` et n’implémente pas la fusion complète des familles de règles, cartes, événements, phases ou procédures.

Ce diagnostic est exposé par la commande :

```bash
python -m services.cabinet.outils.diagnostiquer_skin uat_mandat_austerite_overlay
```

La recette UAT Docker est documentée dans `docs/bre/uat-createur-skin.md`.
La recette pas-à-pas de création d’une skin overlay de niveau 1 est documentée
dans `docs/bre/creer-une-skin-bre.md`.
Le gabarit minimal de skin overlay est fourni dans
`docs/bre/templates/skin-overlay/`.

Une skin n’est pas seulement un habillage visuel. Elle est un scénario jouable qui spécialise le moteur générique en définissant :

- l’identité du scénario ;
- le guide général du jeu ;
- les paramètres de départ ;
- le matériel disponible ;
- les conditions de victoire et d’échec ;
- les règles d’action ;
- les cartes et événements ;
- la narration ;
- les procédures offertes aux joueurs ;
- éventuellement la chorégraphie complète de la partie.

L’objectif poweruser est de permettre à un créateur de skin de partir d’un scénario fonctionnel existant, d’en hériter, puis de personnaliser progressivement seulement les parties qu’il assume.

Formule directrice :

> Le moteur sait exécuter une partie.
> La skin dit quelle partie on joue.

---

## 2. Décision d’architecture

Le modèle cible repose sur une logique d’héritage et de surcharge.

Une skin fille peut déclarer :

```yaml
skin:
  id: mandat_austerite
  herite_de: debut_mandat_bre
```

Cela signifie :

- la skin fille reprend tout ce que fournit la skin parente ;
- elle ne redéfinit que ce qu’elle souhaite personnaliser ;
- les éléments non redéfinis sont hérités ;
- les éléments redéfinis suivent une sémantique explicite de remplacement, fusion, ajout, retrait ou surcharge.

À terme, la skin parente de référence devrait être :

```text
base_conseil_ministres
```

Tant que cette base n’existe pas, la skin de référence provisoire est :

```text
debut_mandat_bre
```

## 3. Abandon des versions antérieures comme contrat cible

Les versions précédentes de skins et de fichiers BRE doivent être comprises comme des étapes de preuve de concept.

Elles ne constituent pas un contrat à maintenir indéfiniment.

Le modèle défini ici devient la direction cible.

Conséquences :

- il n’est pas requis de préserver toutes les conventions antérieures ;
- les prototypes existants peuvent être adaptés ;
- la documentation doit progressivement être alignée sur ce modèle ;
- les anciennes approches par copie complète de skin sont tolérées pour expérimentation, mais ne sont pas l’expérience cible ;
- l’expérience cible est l’héritage déclaratif et la surcharge progressive.

## 4. Définition générale d’une skin

Une skin est une couche fonctionnelle de scénario.

Elle définit ce qui est propre à un scénario donné :

- le monde politique ;
- les ressources ;
- les axes ;
- les cartes ;
- les événements ;
- les objectifs collectifs ;
- les objectifs individuels ;
- les règles politiques ;
- les messages narratifs ;
- les procédures offertes aux joueurs ;
- les conditions de fin.

Le moteur fournit les capacités génériques :

- créer une partie ;
- maintenir l’état ;
- appliquer des commandes ;
- gérer les joueurs ;
- gérer les cartes ;
- gérer les attentes ;
- gérer le programme ;
- gérer les votes ;
- journaliser ;
- exposer l’état à l’UI.

La skin ne devrait pas réimplémenter le moteur.

Elle devrait plutôt produire ou configurer des décisions que le moteur sait exécuter.

## 5. Structure cible d’une skin

Une skin complète pourrait prendre cette forme :

```text
services/cabinet/skins/<skin_id>/
  skin.yaml
  axes.yaml
  ressources.yaml
  cartes.yaml
  evenements.yaml
  messages.yaml

  regles/
    validation_actions.yaml
    fin_partie.yaml
    resolution_programme.yaml
    capital_structurel.yaml
    economie.yaml
    opposition.yaml

  procedures/
    programme.yaml
    vote.yaml
    perturbation.yaml

  README.md
```

Une skin fille n’a pas besoin de fournir tous ces fichiers.

Une skin fille minimale pourrait seulement contenir :

```text
services/cabinet/skins/mandat_austerite/
  skin.yaml
  regles/
    validation_actions.yaml
```

Le reste serait hérité de la skin parente.

Un exemple UAT minimal existe dans :

```text
services/cabinet/skins/uat_mandat_austerite_overlay/skin.yaml
```

Il sert à valider la lecture et le diagnostic d’un overlay. Il ne constitue pas encore une migration des skins existantes vers le modèle complet.

La preuve de concept actuelle utilise encore le fichier `regles/validation_cartes.yaml` pour valider `programme.engager_carte`. Le nom cible `regles/validation_actions.yaml` généralise cette intention à plusieurs actions. Pendant la transition, `validation_cartes.yaml` doit être compris comme le premier cas spécialisé de la future famille `validation_actions`.

## 6. Couche 1 — guide général du scénario

La première couche poweruser doit agir comme un guide général du jeu.

Elle répond aux questions suivantes :

- Quel scénario joue-t-on ?
- Quel est son contexte ?
- Quel est son matériel ?
- Quelles sont les ressources initiales ?
- Quelles sont les conditions de victoire et d’échec ?
- Quelles sont les conditions collectives ?
- Quelles sont les conditions individuelles ?
- De quelle skin hérite-t-on ?

Exemple cible :

```yaml
skin:
  id: mandat_austerite
  herite_de: debut_mandat_bre
  nom: Mandat d’austérité
  version: v1
  difficulte: intermediaire

presentation:
  pitch: >
    Le cabinet entre en fonction dans un contexte budgétaire tendu.
    Chaque mesure exige davantage de capital politique.

  intention: >
    Faire sentir la rareté politique. Gouverner reste possible,
    mais chaque engagement coûte cher.

  public_cible: >
    Joueurs ayant déjà joué le scénario de début de mandat.

materiel:
  joueurs:
    min: 2
    max: 5

  axes:
    heriter: true

  cartes:
    heriter: true

  evenements:
    heriter: true

parametres:
  nb_tours_max: 7
  main_initiale: 5
  attention_par_tour: 3
  capital_politique_initial: 3
  capital_collectif_initial: 0
  capital_opposition_initial: 2

conditions_collectives:
  victoire:
    - id: mandat_complete
      description: Le cabinet termine le mandat sans crise multiple.

  echec:
    - id: crise_multiple
      description: Le gouvernement tombe si deux axes ou plus sont en crise.

conditions_individuelles:
  score:
    - id: capital_final
      description: Chaque joueur marque selon son capital politique final.

    - id: contribution_programme
      description: Bonus selon les cartes adoptées provenant du joueur.
```

Cette couche mélange volontairement trois types d’information :

- présentation descriptive ;
- paramètres exécutables ;
- objectifs et conditions de réussite.

La documentation doit toutefois distinguer clairement ces trois usages.

## 7. Présentation descriptive, paramètres exécutables et règles exécutables

Une skin contient des informations de natures différentes.

### 7.1 Présentation descriptive

Ces éléments aident le joueur ou le créateur de skin à comprendre le scénario.

Exemples :

```yaml
presentation:
  pitch: >
    Le cabinet entre en fonction dans un contexte budgétaire tendu.

  intention: >
    Faire sentir la rareté politique.
```

Ces champs ne modifient pas directement la mécanique, mais ils orientent la conception.

### 7.2 Paramètres exécutables

Ces éléments modifient directement la partie.

Exemples :

```yaml
parametres:
  nb_tours_max: 7
  capital_politique_initial: 3
```

### 7.3 Règles exécutables

Ces éléments expriment des conditions, coûts, effets ou transitions.

Exemple :

```yaml
validation_actions:
  - id: engager_carte_cout_austerite
    op: programme.engager_carte
    conditions:
      - champ: joueur.capital_politique
        operateur: ">="
        valeur: 2
    cout:
      - op: joueur.capital.delta
        delta: -2
```

## 8. Sémantique d’héritage

Chaque famille de fichier ou de section doit avoir une sémantique d’héritage explicite.

| Famille | Sémantique recommandée |
| --- | --- |
| skin | remplacement champ par champ |
| presentation | remplacement champ par champ |
| parametres | remplacement champ par champ |
| materiel | remplacement champ par champ |
| conditions_collectives | fusion ou remplacement explicite |
| conditions_individuelles | fusion ou remplacement explicite |
| messages | fusion par clé |
| cartes | ajout, remplacement ou retrait par id |
| evenements | ajout, remplacement ou retrait par id |
| validation_actions | remplacement par id de règle ou par opération |
| procedures | remplacement prudent par id |
| phases | remplacement explicite seulement |
| transitions | remplacement explicite seulement |
| resolution_programme | remplacement par bloc nommé |
| fin_partie | fusion ou remplacement explicite |
| opposition | fusion ou remplacement explicite selon les blocs |
| economie | remplacement par bloc nommé |

Règle générale : lorsqu’une famille peut être fusionnée ou remplacée, la skin fille doit déclarer explicitement son intention. Aucun remplacement destructif implicite ne devrait être appliqué aux familles complexes.

## 9. Héritage des paramètres simples

Pour les paramètres simples, la skin fille remplace seulement les champs qu’elle fournit.

Parent :

```yaml
parametres:
  nb_tours_max: 7
  main_initiale: 5
  attention_par_tour: 3
  capital_politique_initial: 5
```

Fille :

```yaml
parametres:
  capital_politique_initial: 3
```

Résultat effectif :

```yaml
parametres:
  nb_tours_max: 7
  main_initiale: 5
  attention_par_tour: 3
  capital_politique_initial: 3
```

## 10. Héritage des messages

Les messages sont fusionnés par clé.

Parent :

```yaml
messages:
  programme_ouvert: Le programme du cabinet est ouvert.
  crise_multiple: Le gouvernement tombe sous l’effet de crises simultanées.
```

Fille :

```yaml
messages:
  programme_ouvert: Le programme d’austérité est maintenant sur la table.
```

Résultat effectif :

```yaml
messages:
  programme_ouvert: Le programme d’austérité est maintenant sur la table.
  crise_multiple: Le gouvernement tombe sous l’effet de crises simultanées.
```

## 11. Héritage des collections par id

Les cartes, événements, missions, règles et autres collections doivent être manipulés par id.

Syntaxe cible :

```yaml
cartes:
  heriter: true

  ajouter:
    - id: MES_TRANSITION_VERTE
      nom: Transition verte
      type: mesure
      cout_attention: 2
      cout_cp: 1

  remplacer:
    - id: MES_PLAN_SOCIAL
      cout_attention: 2
      cout_cp: 2

  retirer:
    - MES_BAISSE_IMPOTS
```

Principes :

- `heriter: true` signifie que la collection parente est conservée ;
- `ajouter` insère de nouveaux éléments ;
- `remplacer` remplace ou surcharge un élément existant par id ;
- `retirer` retire un élément hérité ;
- un id dupliqué sans intention explicite doit être considéré comme une erreur de diagnostic.

## 12. Héritage des règles d’action

Les règles d’action peuvent être surchargées par id de règle ou par opération.

Exemple :

```yaml
validation_actions:
  heriter: true

  remplacer:
    - id: engager_carte_cout_standard
      op: programme.engager_carte
      conditions:
        - champ: joueur.attention_dispo
          operateur: ">="
          valeur: carte.cout_attention
        - champ: joueur.capital_politique
          operateur: ">="
          valeur: 2
      cout:
        - op: joueur.attention.delta
          delta: -carte.cout_attention
        - op: joueur.capital.delta
          delta: -2
```

Pour éviter les ambiguïtés, une règle fille devrait idéalement remplacer une règle par son id.

Le remplacement par op peut être permis plus tard, mais doit être diagnostiqué clairement lorsqu’il existe plusieurs règles pour la même opération.

## 13. Conditions collectives de victoire et d’échec

Les conditions collectives décrivent la réussite ou l’échec du groupe.

Exemples :

```yaml
conditions_collectives:
  victoire:
    - id: mandat_complete
      description: Le cabinet termine le mandat.
      condition:
        champ: partie.tour
        operateur: ">="
        valeur: partie.nb_tours_max

  echec:
    - id: crise_multiple
      description: Le gouvernement tombe si deux axes ou plus sont en crise.
      condition:
        count:
          source: axes
          where:
            valeur: "<= seuil_crise"
          min: 2
```

Les conditions collectives appartiennent à la skin parce qu’elles expriment le sens politique du scénario.

Le moteur peut fournir l’opération générique :

```yaml
op: partie.terminer
```

Mais la skin décide ce qui constitue une victoire, une crise ou un échec.

## 14. Conditions individuelles

Les conditions individuelles définissent comment les joueurs se distinguent à la fin.

Exemples :

```yaml
conditions_individuelles:
  score:
    - id: capital_final
      description: Chaque joueur marque selon son capital politique final.
      source: joueur.capital_politique

    - id: contribution_programme
      description: Bonus selon les cartes adoptées provenant du joueur.
      source: joueur.cartes_adoptees
      points_par_unite: 1

  titres:
    - id: pilier_du_cabinet
      titre: Pilier du cabinet
      condition:
        champ: joueur.cartes_adoptees
        operateur: ">="
        valeur: 4

    - id: survivant_politique
      titre: Survivant politique
      condition:
        champ: joueur.capital_politique
        operateur: ">="
        valeur: 5
```

Cette distinction permet au jeu d’être semi-coopératif :

- le cabinet peut réussir ou échouer collectivement ;
- les ministres peuvent être évalués individuellement.

## 15. Niveaux d’audace du poweruser

La création de skin doit être progressive.

Un créateur de skin ne devrait pas devoir comprendre toute l’architecture dès le départ.

Le principe de personnalisation à complexité croissante est central : un créateur peut commencer par personnaliser seulement le guide général du scénario, puis assumer progressivement le contenu, les règles d’action, la résolution politique ou la chorégraphie.

### Niveau 1 — personnaliser le guide du scénario

Le poweruser modifie :

- identité ;
- pitch ;
- difficulté ;
- nombre de tours ;
- ressources initiales ;
- conditions générales de victoire et d’échec.

Il hérite de tout le reste.

### Niveau 2 — personnaliser le contenu

Le poweruser modifie :

- cartes ;
- événements ;
- messages.

### Niveau 3 — personnaliser les règles d’action

Le poweruser modifie :

- coûts ;
- conditions ;
- validations ;
- messages de refus ;
- effets immédiats.

### Niveau 4 — personnaliser la résolution politique

Le poweruser modifie :

- résolution du programme ;
- capital collectif ;
- opposition ;
- budget ;
- conditions de fin avancées.

### Niveau 5 — personnaliser la chorégraphie

Le poweruser modifie :

- phases ;
- transitions ;
- attentes ;
- procédures ;
- ordre du tour.

Ce niveau est avancé et doit être documenté avec prudence.

## 16. Documentation progressive attendue

La documentation doit suivre les niveaux d’audace.

Structure cible possible :

```text
docs/bre/creer-une-skin/
  01-personnaliser-le-scenario.md
  02-personnaliser-les-cartes.md
  03-personnaliser-les-regles-action.md
  04-personnaliser-la-resolution.md
  05-personnaliser-la-choregraphie.md
```

Chaque document devrait contenir :

- ce que le poweruser peut changer ;
- les fichiers concernés ;
- ce qu’il ne faut pas changer ;
- un exemple minimal ;
- une commande de validation UAT ;
- les pièges fréquents ;
- les signes indiquant qu’il faut passer au niveau suivant.

## 17. Diagnostic attendu pour une skin héritée

Un outil UAT ou diagnostic devrait pouvoir expliquer ce qui est hérité et ce qui est personnalisé.

Exemple de sortie cible :

```text
Skin : mandat_austerite
Hérite de : debut_mandat_bre

Personnalisé :
- skin.nom
- presentation.pitch
- parametres.capital_politique_initial
- validation_actions.engager_carte_cout_standard

Hérité :
- axes
- cartes
- événements
- procédures
- phases
- résolution du programme
- conditions de fin
```

Ce diagnostic est essentiel pour rendre l’héritage compréhensible.

## 18. Impact sur les tickets existants

### T26 — parcours UAT accessible

T26 ne doit pas seulement être une commande de test technique.

Il doit devenir le premier outil de diagnostic poweruser.

Il peut commencer par valider une action de carte, mais sa conception doit rester extensible vers :

- validation d’une action ;
- comparaison de skins ;
- diagnostic des héritages ;
- affichage des règles sources ;
- affichage des facts ;
- affichage des commandes produites.

### T27 — recette pas-à-pas

T27 doit être aligné sur les niveaux d’audace.

La recette ne doit pas seulement dire “copier une skin”.

Elle doit présenter deux approches :

- approche par copie, utile seulement pour les expérimentations ou les UAT de transition ;
- approche cible par héritage déclaratif.

### T28 — gabarit de skin

T28 doit produire un gabarit d’overlay, pas seulement une copie complète.

Le gabarit doit montrer :

- `skin.yaml` ;
- `regles/validation_actions.yaml` ;
- `messages.yaml` ;
- `README.md`.

et expliquer que le reste peut être hérité.

## 19. Questions ouvertes

Certaines décisions doivent encore être précisées avant implémentation complète.

### 19.1 Chargement effectif des héritages

Il faudra décider comment le chargeur combine :

- fichiers Python existants ;
- fichiers YAML déclaratifs ;
- skin parente ;
- skin fille.

### 19.2 Validation de schéma

Il faudra définir des schémas ou validateurs pour éviter les erreurs silencieuses.

Exemples :

- id de skin manquant ;
- parent inexistant ;
- règle remplacée introuvable ;
- carte retirée inexistante ;
- doublon d’id ;
- opérateur non supporté.

### 19.3 Messages de refus

Les règles d’action devraient produire des raisons lisibles.

Exemple :

```yaml
conditions:
  - champ: joueur.capital_politique
    operateur: ">="
    valeur: 2
    sinon: capital_politique_insuffisant
    message: Cette action exige davantage de capital politique.
```

### 19.4 Migration progressive du Python existant

La skin Python classique contient encore beaucoup de logique.

La migration doit être progressive :

- couche 1 ;
- contenu ;
- règles d’action ;
- narration ;
- conditions de fin ;
- résolution ;
- opposition ;
- chorégraphie.

## 20. Feuille de route proposée

### Phase A — formaliser l’héritage

- documenter le modèle ;
- définir `skin.yaml` ;
- définir les règles de fusion/remplacement ;
- produire un exemple papier avec `mandat_austerite`.

Première capacité livrée : lecture de `skin.yaml` et diagnostic minimal d’un overlay. Les règles de fusion/remplacement restent à implémenter.

### Phase B — couche 1 déclarative

- identité ;
- présentation ;
- paramètres initiaux ;
- conditions collectives ;
- conditions individuelles.

### Phase C — diagnostic poweruser

- afficher héritages/personnalisations ;
- valider une action ;
- comparer deux skins.

### Phase D — contenu déclaratif

- cartes ;
- événements ;
- messages.

### Phase E — règles d’action enrichies

- autres actions ;
- messages de refus ;
- opérateurs supplémentaires ;
- diagnostics.

### Phase F — résolution politique

- résolution du programme ;
- budget ;
- capital structurel ;
- fin de partie.

### Phase G — opposition et narration avancée

- missions d’opposition ;
- momentum ;
- lecture politique.

### Phase H — chorégraphie avancée

- phases ;
- transitions ;
- attentes ;
- procédures.

## 21. Conclusion

Le modèle poweruser cible n’est pas la copie complète d’une skin existante.

Le modèle cible est :

une skin fille qui hérite d’un scénario fonctionnel et surcharge progressivement les parties qu’elle assume.

Ce modèle permet :

- une entrée simple pour les créateurs de skin ;
- une complexité croissante ;
- une documentation progressive ;
- une meilleure séparation entre moteur et scénario ;
- une trajectoire claire vers des règles déclaratives plus riches.

La preuve actuelle avec `validation_cartes.yaml` démontre la faisabilité du premier cas spécialisé de validation d’action.

La prochaine maturation consiste à formaliser l’héritage, puis à élargir graduellement les familles de règles déclaratives.
