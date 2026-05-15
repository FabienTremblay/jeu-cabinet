# Skin Poweruser BRE

## Objectif

La skin `mandat_fragile` démontre qu'un créateur de skin peut changer une règle
de jeu par configuration déclarative, sans changement spécifique dans l'UI, le
noyau Cabinet, le Java ou le `rules-service`.

Pour une démonstration pas à pas, voir `docs/bre/demo-poweruser-bre.md`.
Pour créer une nouvelle skin overlay, voir `docs/bre/creer-une-skin-bre.md`.

## Créer Une Skin Dérivée

L’approche cible est maintenant l’overlay déclaratif avec `skin.yaml`. La copie
complète d’une skin existante reste utile seulement pour les expérimentations ou
les essais créateur de transition.

Le premier niveau de création est documenté dans
`docs/bre/creer-une-skin-bre.md`.

L’exemple historique `mandat_fragile` suit encore une structure de skin Cabinet
classique :

```text
services/cabinet/skins/mandat_fragile/
├── __init__.py
├── config.py
├── regles.py
└── regles/
    └── validation_cartes.yaml
```

Dans cette forme historique, `config.py` peut dériver d'une skin existante et
ajuster les paramètres du contexte de jeu, par exemple le capital politique
initial.

`regles/validation_cartes.yaml` porte les règles ajustables par un créateur de
skin. Pour une nouvelle création, préférer l’approche overlay documentée dans la
recette T27.

## Exemple Mandat Fragile

Dans `debut_mandat_bre`, une carte dont la définition indique :

```json
{
  "cout_attention": 1,
  "cout_cp": 1
}
```

est acceptée avec `attention_dispo = 1` et `capital_politique = 1`.

Dans `mandat_fragile`, la règle YAML exige deux points d'attention :

```yaml
conditions:
  - champ: joueur.attention_dispo
    operateur: ">="
    valeur: 2
cout:
  - op: joueur.attention.delta
    delta: -2
```

La même action est donc refusée avec `attention_dispo = 1`, puis acceptée avec
`attention_dispo = 2` en produisant un coût d'attention de `-2`.

## Ce Que Le Créateur Peut Modifier

- les conditions dans `validation_cartes.yaml` ;
- les coûts produits ;
- les paramètres de skin dans `skin.yaml` pour l’approche overlay ;
- les textes descriptifs de la skin.

## Ce Qui Ne Change Pas

L'UI continue de consommer `actions_disponibles` et d'envoyer les actions sans
connaître `mandat_fragile`.

Le noyau continue de porter l'état et d'appliquer les commandes.

Le `rules-service` reste le point d'entrée BRE et le routeur général. Aucun code
Java spécifique à `mandat_fragile` n'est ajouté.

## Limites

La démonstration reste volontairement centrée sur `programme.engager_carte`.
Le mini-interpréteur YAML ne remplace pas un moteur de règles complet.
Drools/DMN reste une piste future, hors périmètre de cette branche.
