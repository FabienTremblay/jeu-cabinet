# Règles Déclaratives YAML BRE

## Objectif

BRE T23 introduit une première règle métier modifiable par configuration de
skin : la validation et le coût de `programme.engager_carte`.

La règle vit dans le skin :

```text
services/cabinet/skins/debut_mandat_bre/regles/validation_cartes.yaml
```

Un créateur de skin peut ajuster les conditions et les coûts sans modifier :

- l'UI ;
- le noyau `services/cabinet/moteur/` ;
- le code Java du `rules-service`.

Dans cette branche, l'interprétation YAML est faite côté Python par le proxy
BRE. Le `rules-service` reste le routeur Java ; Drools/DMN n'est pas introduit.

## Exemple

```yaml
version: 1

validation_cartes:
  - id: engager_carte_cout_standard
    op: programme.engager_carte
    conditions:
      - champ: joueur.attention_dispo
        operateur: ">="
        valeur: carte.cout_attention
      - champ: joueur.capital_politique
        operateur: ">="
        valeur: carte.cout_cp
    cout:
      - op: joueur.attention.delta
        delta: -carte.cout_attention
      - op: joueur.capital.delta
        delta: -carte.cout_cp
```

## Ce Qui Est Modifiable

Le créateur de skin peut modifier :

- les seuils de condition ;
- les champs comparés ;
- les coûts appliqués ;
- les opérations de coût produites.

Exemples :

- remplacer `valeur: carte.cout_attention` par `valeur: 3` ;
- augmenter `delta: -carte.cout_attention` vers `delta: -3` ;
- ajouter une condition sur `joueur.capital_politique`.

## Ce Qui Reste Dans Le Noyau

Le noyau conserve :

- l'état de partie ;
- les joueurs, mains et cartes ;
- l'application des commandes produites ;
- les invariants génériques du jeu.

Le noyau ne connaît pas la logique déclarative du coût des cartes.

## Ce Qui Reste Dans Le Rules-Service

Le `rules-service` reste le point de routage BRE et le moteur cible pour les
autres décisions. Pour T23, la validation des cartes du skin
`debut_mandat_bre` est interprétée côté Python dans le proxy BRE afin de
démontrer rapidement le modèle déclaratif sans introduire Drools/Kogito.

## Limites Du Mini-Interpréteur

Le mini-interpréteur supporte seulement :

- sélection par `op` ;
- chemins simples comme `joueur.attention_dispo` ou `carte.cout_cp` ;
- opérateur `>=` ;
- valeurs numériques ou références simples ;
- deltas numériques ou références négatives comme `-carte.cout_attention`.

Il ne supporte pas encore :

- expressions booléennes composées ;
- listes de règles concurrentes ;
- priorités ;
- messages configurables ;
- effets de carte autres que les coûts.

Une migration future vers le `rules-service` ou vers Drools/DMN devra préserver
le contrat fonctionnel démontré ici : une skin modifie son comportement par
configuration déclarative.
