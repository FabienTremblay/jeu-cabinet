# Contrat De Routage BRE

## Objectif

Le routage entre le proxy Python Cabinet et `rules-service` repose sur un bloc unique :

```json
{
  "analyse_skin": {
    "skin": "debut_mandat_bre",
    "version": "v1"
  }
}
```

Ce bloc est la source principale de routage. Les champs historiques comme
`skin` ou `version_regles` peuvent encore être lus par les DTO Java pour
compatibilité, mais ils ne doivent pas choisir le moteur.

Ce contrat concerne le point d'entrée BRE Java. Les règles déclaratives YAML de
skin peuvent ensuite être appliquées par le proxy Python dans cette preuve de
concept, sans changer le routage.

## Règle De Routage Actuelle

`rules-service` route vers le moteur de démonstration v1 seulement si :

- `analyse_skin.skin == "debut_mandat_bre"` ;
- `analyse_skin.version == "v1"`.

Toute autre combinaison route explicitement vers le moteur mock.

Le service démarre en mode `cab.rules.engine=routing`. Le mode `mock` reste
disponible par configuration explicite pour les tests ou diagnostics, mais il
ne doit pas être le mode par défaut de la démonstration BRE.

## Payload Minimal

Les endpoints BRE doivent recevoir au minimum :

```json
{
  "analyse_skin": {
    "skin": "debut_mandat_bre",
    "version": "v1"
  },
  "etat_min": {},
  "joueurs": {},
  "axes": {},
  "trace": {}
}
```

Pour `/rules/eval/valider-usage-carte`, le payload contient aussi `cmd`.

## Compatibilité

`version_regles` n'est plus une source de routage. Une requête qui ne fournit
que `version_regles: "debut_mandat_bre.v1"` sans `analyse_skin` doit tomber sur
le mock, afin d'éviter un routage implicite ou ambigu.
