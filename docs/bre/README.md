# Documentation BRE Et Skins Poweruser

Ce dossier rassemble la preuve de concept BRE et la trajectoire de skins
poweruser du jeu **Conseil des ministres**.

Il contient à la fois des recettes utilisables, des contrats techniques et des
documents d’architecture cible. Tous les documents ne sont donc pas des guides
opérationnels pour créateur de skin.

## Parcours Par Besoin

### Je veux comprendre rapidement le sujet BRE

Lire dans cet ordre :

1. [`architecture-fonctionnelle-bre.md`](architecture-fonctionnelle-bre.md)
2. [`poweruser-skin.md`](poweruser-skin.md)
3. [`demo-poweruser-bre.md`](demo-poweruser-bre.md)

Ces documents expliquent la démonstration, la séparation entre moteur et skin,
et ce que la preuve actuelle montre déjà.

### Je veux créer une skin

Lire dans cet ordre :

1. [`creer-une-skin-bre.md`](creer-une-skin-bre.md)
2. [`templates/skin-overlay/README.md`](templates/skin-overlay/README.md)
3. [`diagnostic-createur-skin.md`](diagnostic-createur-skin.md)
4. [`validation-skin-candidate.md`](validation-skin-candidate.md)

Ce parcours est le plus court pour un créateur de skin. Il commence par une
skin overlay de niveau 1, puis ajoute le diagnostic et la validation candidate.

### Je veux diagnostiquer une skin

Lire :

- [`diagnostic-createur-skin.md`](diagnostic-createur-skin.md)
- [`validation-skin-candidate.md`](validation-skin-candidate.md)

Le diagnostic répond à la question : « qu’est-ce que mon overlay déclare ? »

La validation candidate répond à la question : « quelles erreurs empêchent une
publication fiable ? »

### Je veux comprendre l’architecture cible

Lire dans cet ordre :

1. [`modele-heritage-skin-poweruser.md`](modele-heritage-skin-poweruser.md)
2. [`couche-2-contenu-declaratif.md`](couche-2-contenu-declaratif.md)
3. [`publication-skin-resolue.md`](publication-skin-resolue.md)
4. [`architecture-fonctionnelle-bre.md`](architecture-fonctionnelle-bre.md)

Ces documents décrivent la direction cible. Ils ne sont pas tous des recettes
directement utilisables par un créateur.

### Je veux savoir quelles skins sont des exemples ou des prototypes

Lire :

- [`inventaire-skins-elaboration.md`](inventaire-skins-elaboration.md)

Cet inventaire classe les dossiers sous `services/cabinet/skins/` et précise
lesquels sont des références provisoires, démonstrateurs, fixtures ou exemples
contrôlés.

### Je veux comprendre la publication future

Lire :

- [`publication-skin-resolue.md`](publication-skin-resolue.md)
- [`validation-skin-candidate.md`](validation-skin-candidate.md)
- [`couche-2-contenu-declaratif.md`](couche-2-contenu-declaratif.md)

La publication résolue est conçue, mais pas encore implémentée.

### Je veux voir les contrats techniques

Lire :

- [`contrat-routage-bre.md`](contrat-routage-bre.md)
- [`contrat-facts-minimal.md`](contrat-facts-minimal.md)
- [`regles-declaratives-yaml.md`](regles-declaratives-yaml.md)
- [`tests-rules-service.md`](tests-rules-service.md)

Ces documents concernent le routage Python vers le rules-service, les facts
minimaux, les règles YAML actuelles et l’exécution des tests Java.

## État Actuel Vs Cible

### Fonctionne maintenant

- diagnostic de `skin.yaml` ;
- diagnostic des contenus déclaratifs de couche 2 :
  `cartes.yaml`, `evenements.yaml`, `messages.yaml` ;
- validation non destructive d’une skin candidate ;
- catalogue minimal `donnees/cabinet/skins/catalogue.yaml` pour exposer les
  skins Python/hybrides et les overlays déclaratifs aux outils ;
- règle YAML déclarative pour `programme.engager_carte` ;
- comparaison démontrée entre skins par configuration YAML.

### Démontré, mais encore limité

- une skin peut changer un comportement métier par YAML ;
- un créateur peut diagnostiquer une skin overlay sans écrire de test Python ;
- une candidate peut être validée localement sans publication.

### Seulement conçu ou documenté

- héritage complet des familles de skin ;
- publication résolue ;
- génération de `publication.yaml` ;
- calcul de hash parent, overlay et résultat ;
- refactorisation assistée si le parent évolue ;
- catalogue futur de skins publiées.

## Termes Importants

- `skin overlay` : skin de création qui déclare seulement ce qu’elle
  personnalise.
- `brouillon` : skin en cours d’élaboration, souvent dans un dossier externe ou
  monté dans Docker.
- `candidate` : overlay assez mûr pour être validé et relu avant publication.
- `publiée` : skin résolue, validée, versionnée et destinée au runtime.
- `diagnostic créateur` : commande qui explique ce que l’overlay déclare.
- `validation candidate` : commande non destructive qui détecte les erreurs
  locales empêchant une publication fiable.
- `publication résolue` : processus futur qui produira une skin autonome à
  partir d’un overlay et de son parent.
- `héritage résolu à la publication` : principe selon lequel le runtime ne
  recompose pas l’héritage dynamiquement.

## Ce Qu’un Créateur De Skin Devrait Lire

Parcours court recommandé :

1. [`creer-une-skin-bre.md`](creer-une-skin-bre.md)
2. [`templates/skin-overlay/README.md`](templates/skin-overlay/README.md)
3. [`diagnostic-createur-skin.md`](diagnostic-createur-skin.md)
4. [`validation-skin-candidate.md`](validation-skin-candidate.md)

Éviter de commencer par `couche-2-contenu-declaratif.md` : ce document est une
note d’architecture, pas une recette de création.

## Ce Qu’un Architecte Ou Développeur Devrait Lire

Parcours recommandé :

1. [`modele-heritage-skin-poweruser.md`](modele-heritage-skin-poweruser.md)
2. [`couche-2-contenu-declaratif.md`](couche-2-contenu-declaratif.md)
3. [`publication-skin-resolue.md`](publication-skin-resolue.md)
4. [`architecture-fonctionnelle-bre.md`](architecture-fonctionnelle-bre.md)
5. Contrats techniques selon le besoin :
   [`contrat-routage-bre.md`](contrat-routage-bre.md),
   [`contrat-facts-minimal.md`](contrat-facts-minimal.md),
   [`regles-declaratives-yaml.md`](regles-declaratives-yaml.md),
   [`tests-rules-service.md`](tests-rules-service.md).

## Attention

- Les documents d’architecture ne sont pas tous des recettes utilisables par un
  créateur de skin.
- Certains documents décrivent des hypothèses ou des cibles non encore
  implémentées.
- La publication résolue n’est pas encore implémentée.
- Aucune CLI ne produit encore automatiquement une skin publiée.
- Les exemples et overlays d’élaboration ne doivent pas être interprétés comme
  des skins publiées sans indication explicite.
- Le classement actuel des skins et overlays est documenté dans
  [`inventaire-skins-elaboration.md`](inventaire-skins-elaboration.md).
- Les overlays déclaratifs contrôlés vivent maintenant sous
  `donnees/cabinet/skins/exemples/`, pas sous `services/cabinet/skins/`.

## Réserves Techniques

- Le rules-service Java doit encore être validé dans un environnement JDK 21.
- La résolution complète d’héritage n’est pas implémentée.
- Les validations dépendantes du parent restent à compléter.
- Le runtime complet n’utilise pas encore le catalogue des skins.
