# Timeout des parties

Ce document décrit le mécanisme opératoire de timeout d'inactivité des parties :
comportement métier, flux événementiel, contrats Kafka, limites actuelles et
commandes utiles en développement local.

## Comportement métier

Une partie peut recevoir une politique de timeout effective au moment de son
lancement. Cette politique est copiée depuis la table du lobby et devient la
référence de la partie.

La politique effective est portée par `politique_timeout_partie` :

```json
{
  "version": 1,
  "active": true,
  "delai_inactivite_secondes": 3600
}
```

Règles métier appliquées :

- si la politique est absente, la partie n'est pas surveillée ;
- si `active` vaut `false`, la partie n'est pas surveillée ;
- si `delai_inactivite_secondes` est absent ou invalide, la partie est ignorée
  par la surveillance et l'anomalie est journalisée ;
- si aucune activité moteur n'est observée pendant le délai configuré, une
  commande `partie.terminer` est produite avec la raison `TIMEOUT_INACTIVITE` ;
- la partie est ensuite terminée par le moteur via la logique existante
  `Etat.appliquer_commandes([{"op": "partie.terminer", ...}])` ;
- la raison `TIMEOUT_INACTIVITE` est conservée dans `Etat.raison_fin` et dans
  l'événement domaine `cab.D600.partie.terminer`.

Le délai métier n'est pas codé en dur dans le worker de surveillance. Il provient
de la politique effective transmise au lancement de partie.

## Architecture événementielle

Le mécanisme traverse quatre responsabilités séparées :

1. `services/lobby` définit la politique de timeout de la table.
2. `services/adapter-evenements` transforme l'événement lobby en commande moteur.
3. `services/commande_moteur` exécute les commandes Kafka et surveille
   l'inactivité.
4. `services/api_moteur` et `services/cabinet` terminent effectivement la partie
   et publient l'événement domaine.

### Lancement et propagation de la politique

Flux nominal :

1. Le lobby lance une partie et publie `PartieLancee` sur
   `cabinet.parties.evenements`.
2. `PartieLancee` contient `politique_timeout_partie` si la table porte une
   politique effective.
3. `adapter-evenements` produit une commande `partie.creer` sur `cab.commands`.
4. `commande_moteur` reçoit `partie.creer`, appelle `POST /parties` et transmet
   la politique dans `configuration_partie.politique_timeout_partie`.
5. `api_moteur` transmet cette configuration au noyau.
6. `Etat.configuration_partie` conserve la copie effective.
7. `commande_moteur` enregistre la partie dans son registre de surveillance
   mémoire si la politique est active et valide.

### Activité et surveillance

`commande_moteur` écoute aussi les événements moteur sur `cab.events`.

Pour chaque événement portant l'identifiant de partie (`aggregate_id`, ou à
défaut `data.partie_id` / `payload.partie_id`), le worker met à jour
`derniere_activite_at` de la partie surveillée.

Quand un événement `op_code == "partie.terminer"` est observé sur `cab.events`,
le worker retire la partie du registre de surveillance.

La boucle principale de `commande_moteur` vérifie périodiquement les parties
surveillées. L'intervalle technique de vérification est configurable par :

```env
SURVEILLANCE_INACTIVITE_INTERVALLE_SECONDES=5
```

Cet intervalle ne remplace pas le délai métier. Le délai métier reste
`politique_timeout_partie.delai_inactivite_secondes`.

La surveillance peut être désactivée techniquement par :

```env
SURVEILLANCE_INACTIVITE_ACTIF=0
```

### Terminaison par timeout

Quand le délai est dépassé :

1. `commande_moteur` produit une commande `partie.terminer` sur `cab.commands`.
2. Cette commande porte `raison = "TIMEOUT_INACTIVITE"`.
3. Le même worker consomme ensuite `partie.terminer`.
4. Il appelle `POST /parties/{id_partie}/terminer` sur `api_moteur`.
5. `api_moteur` appelle `PartieManager.terminer`.
6. `PartieManager.terminer` réutilise la logique du moteur :
   `Etat.appliquer_commandes([{"op": "partie.terminer", "raison": ...}])`.
7. Le moteur produit l'événement domaine `cab.D600.partie.terminer`.
8. `api_moteur` publie cet événement sur `cab.events`.
9. `commande_moteur` consomme cet événement et appelle le lobby pour terminer
   la table associée à `id_partie`.

## Idempotence

L'idempotence est assurée à deux niveaux.

Côté surveillance :

- chaque partie surveillée porte `commande_timeout_produite` ;
- dès qu'une commande de timeout est publiée, ce flag empêche une republication
  par la même instance du worker ;
- la commande porte une clé déterministe :

```text
timeout-inactivite:{id_partie}
```

Cette clé est placée dans `commande.idempotency_key` et `meta.idempotency_key`.

Côté moteur :

- `PartieManager.terminer` retourne l'état existant sans réappliquer
  `partie.terminer` si la partie est déjà terminée ;
- un second appel HTTP de terminaison ne republie donc pas un nouvel événement
  domaine `cab.D600.partie.terminer`.

Limite importante : le registre de surveillance est en mémoire. Après
redémarrage du worker, les flags mémoire sont perdus. La clé d'idempotence reste
stable, mais il n'existe pas encore de stockage durable des timeouts produits.

## Contrats Kafka

Les contrats Kafka du mécanisme sont versionnés en JSON Schema dans
`contrats/jsonschema/kafka/`.

### `PartieLancee`

Chemin :

```text
contrats/jsonschema/kafka/lobby/EvenementPartieLancee.schema.json
```

Topic :

```text
cabinet.parties.evenements
```

Producteur :

```text
services/lobby
```

Consommateur :

```text
services/adapter-evenements
```

Champs importants :

- `type = "PartieLancee"`
- `id_table`
- `id_partie`
- `joueurs`
- `skin_jeu`
- `politique_timeout_partie`

`politique_timeout_partie` est optionnel pour préserver la compatibilité avec
les parties créées avant l'introduction de la politique.

### Commande `partie.creer`

Chemin :

```text
contrats/jsonschema/kafka/commande_moteur/CommandePartieCreer.schema.json
```

Topic :

```text
cab.commands
```

Producteur :

```text
services/adapter-evenements
```

Consommateur :

```text
services/commande_moteur
```

Champs importants :

- `table_id`
- `commande.op = "partie.creer"`
- `commande.id_partie`
- `commande.joueurs`
- `commande.skin_jeu`
- `commande.politique_timeout_partie`
- `meta`

Si `commande.politique_timeout_partie` est absent, `commande_moteur` crée la
partie mais n'active pas la surveillance d'inactivité.

### Commande `partie.terminer`

Chemin :

```text
contrats/jsonschema/kafka/commande_moteur/CommandePartieTerminer.schema.json
```

Topic :

```text
cab.commands
```

Producteur :

```text
services/commande_moteur
```

Consommateur :

```text
services/commande_moteur
```

Champs importants :

- `table_id`
- `commande.op = "partie.terminer"`
- `commande.id_partie`
- `commande.raison = "TIMEOUT_INACTIVITE"`
- `commande.idempotency_key`
- `meta.source = "commande_moteur.surveillance_inactivite"`
- `meta.idempotency_key`
- `meta.derniere_activite_at`
- `meta.delai_inactivite_secondes`

Cette commande est produite par la surveillance et réinjectée dans le topic de
commandes pour suivre le même chemin d'exécution que les autres commandes
moteur.

### Événement domaine `cab.D600.partie.terminer`

Topic :

```text
cab.events
```

Producteur :

```text
services/api_moteur
```

Consommateurs actuels :

```text
services/commande_moteur
services/ui_etat_joueur
```

Champs structurants de l'enveloppe domaine :

- `event_type = "cab.D600.partie.terminer"`
- `op_family = "D600"`
- `op_code = "partie.terminer"`
- `aggregate_type = "partie"`
- `aggregate_id = id_partie`
- `data.raison = "TIMEOUT_INACTIVITE"`

`commande_moteur` utilise cet événement pour arrêter la surveillance locale de
la partie et synchroniser le lobby.

## Contrats HTTP liés

Le worker `commande_moteur` exécute la terminaison par HTTP contre
`api_moteur`.

Endpoint :

```http
POST /parties/{partie_id}/terminer
```

Corps :

```json
{
  "raison": "TIMEOUT_INACTIVITE"
}
```

Schéma :

```text
contrats/jsonschema/http/api_moteur/RequeteTerminerPartie.schema.json
```

Snapshot OpenAPI :

```text
contrats/openapi/api_moteur.openapi.json
```

Le même worker synchronise ensuite le lobby après réception de
`cab.D600.partie.terminer`.

Endpoint lobby :

```http
POST /api/parties/{id_partie}/terminer
```

Corps :

```json
{
  "raison": "TIMEOUT_INACTIVITE"
}
```

Schéma :

```text
contrats/jsonschema/http/lobby/DemandeTerminerPartie.schema.json
```

Snapshot OpenAPI :

```text
contrats/openapi/lobby.openapi.json
```

Le lobby retrouve la table par `id_partie`, passe son statut à `terminee` et
conserve les joueurs selon le contrat de terminaison de table existant. Le modèle
`Table` ne porte pas encore de champ `raison_fin`; la raison est transmise dans
l'appel de synchronisation mais n'est pas persistée côté lobby.

## Limites actuelles

La surveillance de timeout est volontairement minimale.

Limites connues :

- le registre des parties surveillées est en mémoire dans `commande_moteur` ;
- un redémarrage du worker perd les parties surveillées en cours ;
- il n'y a pas encore de rechargement depuis une projection ou une base durable ;
- il n'y a pas de présence joueur ;
- il n'y a pas de websocket ;
- il n'y a pas de heartbeat ;
- la synchronisation lobby marque la table `terminee`, mais ne persiste pas la
  raison de fin car le modèle lobby ne porte pas encore ce champ ;
- la commande Kafka `partie.terminer` est idempotente dans le worker courant et
  côté moteur, mais il n'y a pas encore de table durable d'idempotence ;
- le registry Apicurio n'est pas encore utilisé comme validateur runtime pour
  ces schémas JSON Kafka.

Ce mécanisme ne remplace pas les règles de fin de partie propres aux skins
(`TOURS_MAX`, `CRISE_MULTIPLE`, etc.). Il ajoute seulement une terminaison par
inactivité quand la politique effective le demande.

## MaisonNeuve et MaisonLinux

### MaisonNeuve

MaisonNeuve est le poste de développement courant.

Utilisations recommandées :

- édition du code et de la documentation ;
- exécution des tests unitaires Python avec `.venv` ;
- génération ou vérification des contrats si les dépendances locales sont
  disponibles ;
- inspection de `git status`, `git diff`, `pytest`.

Ne pas supposer que Docker est disponible sur MaisonNeuve.

Commandes typiques :

```bash
.venv/bin/python -m pytest -q services/commande_moteur/tests/test_worker_moteur.py
```

```bash
.venv/bin/python -m pytest -q services/cabinet/tests/test_terminer_partie.py services/api_moteur/tests/test_terminer_partie.py
```

```bash
.git/hooks/pre-commit
```

### MaisonLinux

MaisonLinux est l'hôte Docker cible.

Utilisations recommandées :

- démarrage du stack Docker Compose ;
- inspection des conteneurs ;
- lecture des logs Kafka et services ;
- validation manuelle bout-en-bout.

Commandes typiques :

```bash
docker compose up -d --build
```

```bash
docker compose ps
```

```bash
docker compose logs -f moteur-commands
```

```bash
docker compose logs -f api-moteur
```

```bash
docker compose logs -f adapter-evenements
```

Arrêt :

```bash
docker compose down
```

## Configuration opérationnelle

Variables lobby :

```env
LOBBY_TIMEOUT_PARTIE_ACTIF=true
LOBBY_TIMEOUT_PARTIE_DELAI_INACTIVITE_SECONDES=3600
```

Ces variables définissent la politique par défaut appliquée aux nouvelles
tables. Elles ne sont pas lues directement par le worker de surveillance.

Variables `commande_moteur` :

```env
KAFKA_TOPIC_COMMANDS=cab.commands
KAFKA_TOPIC_EVENTS=cab.events
SURVEILLANCE_INACTIVITE_ACTIF=1
SURVEILLANCE_INACTIVITE_INTERVALLE_SECONDES=5
API_MOTEUR_URL=http://api-moteur:8080
```

Dans `docker-compose.yml`, le service concerné est `moteur-commands`.

Le topic `cab.commands` reçoit :

- `partie.creer` depuis `adapter-evenements` ;
- `partie.terminer` depuis `commande_moteur` quand un timeout est détecté.

Le topic `cab.events` reçoit les événements domaine produits par `api_moteur`.

## Tests utiles

Tests ciblés du worker de commandes et de surveillance :

```bash
.venv/bin/python -m pytest -q services/commande_moteur/tests/test_worker_moteur.py
```

Tests ciblés de la terminaison dans le noyau :

```bash
.venv/bin/python -m pytest -q services/cabinet/tests/test_terminer_partie.py
```

Tests ciblés de l'API moteur :

```bash
.venv/bin/python -m pytest -q services/api_moteur/tests/test_terminer_partie.py
```

Lot minimal du mécanisme timeout :

```bash
.venv/bin/python -m pytest -q \
  services/commande_moteur/tests/test_worker_moteur.py \
  services/cabinet/tests/test_terminer_partie.py \
  services/api_moteur/tests/test_terminer_partie.py
```

Validation syntaxique des contrats JSON :

```bash
.venv/bin/python - <<'PY'
import json
from pathlib import Path

for path in Path("contrats/jsonschema").rglob("*.json"):
    json.loads(path.read_text(encoding="utf-8"))

for path in Path("contrats/openapi").glob("*.json"):
    json.loads(path.read_text(encoding="utf-8"))

print("JSON OK")
PY
```

Hook de commit :

```bash
.git/hooks/pre-commit
```

## Diagnostic manuel

Sur MaisonLinux, les logs principaux sont :

```bash
docker compose logs -f moteur-commands
```

À vérifier dans les logs :

- réception de `partie.creer` ;
- activation de la surveillance avec l'id de partie et le délai ;
- mise à jour d'activité depuis `cab.events` ;
- production d'une commande `partie.terminer` ;
- appel HTTP `POST /parties/{id_partie}/terminer` ;
- publication de `cab.D600.partie.terminer` par `api_moteur`.
- appel HTTP `POST /api/parties/{id_partie}/terminer` vers le lobby.

Exemples de symptômes :

- aucune surveillance : vérifier que `politique_timeout_partie.active` vaut
  `true` et que `delai_inactivite_secondes` est présent ;
- timeout jamais produit : vérifier que `SURVEILLANCE_INACTIVITE_ACTIF` n'est
  pas à `0` et que le délai effectif est bien dépassé ;
- timeout produit plusieurs fois après redémarrage : limite connue du registre
  mémoire, à résoudre par une idempotence durable ;
- partie terminée côté moteur mais table lobby encore active : vérifier les logs
  `moteur-commands` et l'accessibilité HTTP du service `lobby`.

## Évolutions restantes

Les prochaines étapes attendues sont :

- ajouter une idempotence durable si plusieurs instances de `commande_moteur`
  ou des redémarrages doivent être supportés sans doublon ;
- persister la raison de fin côté lobby si le modèle de table évolue pour porter
  ce champ ;
- brancher les schémas Kafka au registry ou à une validation runtime ;
- documenter un scénario bout-en-bout exécuté sur MaisonLinux avec Kafka réel.
