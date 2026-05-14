# Démonstration Poweruser BRE

## Ce Qui Est Démontré

La branche `feature/bre-poweruser-skin` démontre qu'une nouvelle skin peut
modifier une règle de jeu par configuration déclarative, sans changement
spécifique dans :

- l'UI ;
- le noyau Cabinet ;
- le Java ;
- le `rules-service`.

La preuve porte sur une action volontairement limitée :

```text
programme.engager_carte
```

## Chemin Fonctionnel

1. Le noyau Cabinet construit l'état de partie.
2. Le proxy BRE produit `analyse_skin` et `etat_min`.
3. `analyse_skin` identifie la skin et la version de règles.
4. `etat_min` contient les facts minimaux : joueur, main, ressources et carte.
5. Le fichier YAML de la skin décrit les conditions et les coûts.
6. Le mini-interpréteur Python applique cette règle pour valider l'action.
7. Le noyau applique ensuite les commandes produites.

## Scénario Comparatif

Même état initial :

```json
{
  "joueur": {
    "id": "J1",
    "attention_dispo": 1,
    "capital_politique": 1,
    "main": ["MES_PLAN_SOCIAL"]
  },
  "carte": {
    "id": "MES_PLAN_SOCIAL",
    "cout_attention": 1,
    "cout_cp": 1
  }
}
```

Action envoyée :

```json
{
  "op": "programme.engager_carte",
  "joueur_id": "J1",
  "carte_id": "MES_PLAN_SOCIAL"
}
```

### `debut_mandat_bre`

Règle :

```yaml
conditions:
  - champ: joueur.attention_dispo
    operateur: ">="
    valeur: carte.cout_attention
```

Résultat :

```text
action acceptée
coût attention: -1
coût capital politique: -1
```

### `mandat_fragile`

Règle :

```yaml
conditions:
  - champ: joueur.attention_dispo
    operateur: ">="
    valeur: 2
cout:
  - op: joueur.attention.delta
    delta: -2
```

Résultat avec le même état :

```text
action refusée
raison: attention_insuffisante
```

Avec `attention_dispo = 2`, l'action est acceptée et produit un coût
d'attention de `-2`.

## Pourquoi C'est Utile

Un créateur de skin peut rendre une variante plus difficile en modifiant un
fichier YAML de skin au lieu de demander un changement UI, noyau ou Java.

La mécanique reste testable :

- tests unitaires du mini-interpréteur ;
- tests comparatifs entre skins ;
- suite Cabinet complète.

## Commandes De Validation

Tests ciblés BRE :

```bash
.venv/bin/python -m pytest \
  services/cabinet/tests/test_regles_declaratives_cartes.py \
  services/cabinet/tests/test_skin_mandat_fragile.py \
  -q
```

Suite Cabinet :

```bash
.venv/bin/python -m pytest services/cabinet/tests -q
```

Vérification syntaxique Python :

```bash
.venv/bin/python -m py_compile \
  services/cabinet/bre/regles_declaratives_cartes.py \
  services/cabinet/bre/regles_bre_proxy.py \
  services/cabinet/skins/debut_mandat_bre/regles.py \
  services/cabinet/skins/mandat_fragile/regles.py
```

Vérification Git :

```bash
git diff --check
```

Tests Java attendus avec JDK 21 :

```bash
cd rules-service
./mvnw test
```

## Limites

- La démonstration couvre seulement `programme.engager_carte`.
- Le mini-interpréteur YAML reste côté Python pour cette preuve de concept.
- Les tests Java doivent encore être validés dans un environnement JDK 21.
- Drools/DMN reste une piste future, pas une dépendance de cette branche.

## Suite Recommandée

1. Valider l'issue #14 avec un JDK 21.
2. Relire la branche comme preuve de concept complète.
3. Décider si l'interpréteur YAML reste côté Python ou migre derrière
   `rules-service` dans une étape ultérieure.
