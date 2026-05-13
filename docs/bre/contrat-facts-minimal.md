# Contrat Facts Minimal BRE

## Rôle De `etat_min`

`etat_min` transporte les données métier minimales dont le BRE a besoin pour
évaluer une action sans dépendre de l'état Python complet.

Pour BRE T22, le périmètre stabilisé est volontairement limité à
`programme.engager_carte`.

## Champs Minimaux

```json
{
  "etat_min": {
    "phase": "tour",
    "sous_phase": "conseil",
    "tour": 1,
    "joueurs": {
      "J1": {
        "id": "J1",
        "attention_dispo": 2,
        "capital_politique": 3,
        "main": ["MES_PLAN_SOCIAL"]
      }
    },
    "cartes_def": {
      "MES_PLAN_SOCIAL": {
        "id": "MES_PLAN_SOCIAL",
        "type": "mesure",
        "cout_attention": 1,
        "cout_cp": 1
      }
    }
  }
}
```

## Conventions De Nommage

- joueur : `attention_dispo`, pas `attention` ;
- joueur : `capital_politique` ;
- joueur : `main` contient les identifiants des cartes en main ;
- carte : `cout_attention` ;
- carte : `cout_cp`, pas `cout_capital`.

## Payload BRE

Le payload complet garde aussi :

- `analyse_skin` pour le routage ;
- `joueurs` au niveau racine pour compatibilité avec le schéma commun ;
- `axes` et `trace` comme objets extensibles.

`rules-service` lit prioritairement `etat_min.joueurs` et
`etat_min.cartes_def`.

## Limites Actuelles

- Seule l'action `programme.engager_carte` est couverte.
- Les effets métier détaillés des cartes ne sont pas interprétés ici.
- BRE T23 ajoute une première règle déclarative YAML pour la validation et les
  coûts de carte du skin `debut_mandat_bre`.
- Le contrat reste minimal et ne remplace pas les contrats publics HTTP/Kafka.
