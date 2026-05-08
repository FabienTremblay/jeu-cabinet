# exécution locale — environnement de développement

Ce document décrit comment lancer et utiliser le projet **jeu Cabinet** en environnement local à l’aide de `docker compose`.

L’objectif est de fournir un environnement reproductible incluant :
- le noyau applicatif,
- les services API,
- Kafka (KRaft, broker unique),
- le registry de schémas,
- le moteur de règles (BRE),
- Traefik comme point d’entrée.

---

## postes de travail

Le développement courant se fait depuis **MaisonNeuve**. Cette machine sert à
éditer le code, lancer les tests unitaires et générer les contrats lorsque les
dépendances Python/Node/Java sont disponibles localement.

L’hôte Docker cible est **MaisonLinux**. Les commandes `docker compose`,
`make up`, `make down`, `make logs`, `make ps` et l’inspection des conteneurs
doivent être exécutées sur MaisonLinux, sauf si Docker est explicitement lancé
sur MaisonNeuve pour un essai local.

Ne pas supposer que Docker est disponible sur MaisonNeuve.

---

## prérequis

- docker (20+ recommandé)
- plugin Docker Compose v2 (`docker compose`)
- make (optionnel mais recommandé)
- ports locaux disponibles (voir plus bas)

---

## configuration

### fichier `.env`

Le projet utilise un fichier `.env` chargé par Docker Compose.

1. copier le fichier d’exemple :

```bash
cp .env.example .env
```

2. ajuster au besoin :
- domaine (`TRAEFIK_DOMAIN`)
- ports exposés
- mots de passe (postgres, kafka-ui)
- politique par défaut des timeouts de partie côté lobby :
  - `LOBBY_TIMEOUT_PARTIE_ACTIF`
  - `LOBBY_TIMEOUT_PARTIE_DELAI_INACTIVITE_SECONDES`

> ⚠️ le fichier `.env` **ne doit pas** être versionné.

Ces valeurs sont appliquées à chaque nouvelle table. La partie recevra plus tard
une copie effective de cette configuration au lancement via :
- l'événement Kafka `PartieLancee` sur `cabinet.parties.evenements` ;
- la commande Kafka `partie.creer` sur `cab.commands` ;
- le champ HTTP `configuration_partie` de `POST /parties`.

Le noyau conserve cette copie dans `Etat.configuration_partie`. Le worker
`commande_moteur` utilise ensuite cette politique effective pour surveiller
l'inactivité, produire `partie.terminer` sur `cab.commands` avec la raison
`TIMEOUT_INACTIVITE`, puis synchroniser le lobby après l'événement domaine
`cab.D600.partie.terminer` publié sur `cab.events`.

---

## démarrage rapide

Sur MaisonLinux, à la racine du dépôt :

```bash
docker compose up --build
```

ou en arrière-plan :

```bash
docker compose up -d --build
```

Les services démarrent dans l’ordre défini par les dépendances Docker.

---

## services principaux

### traefik

- rôle : reverse-proxy et routage HTTP
- ports :
  - HTTP : `${TRAEFIK_HTTP_PORT}` (ex. 80)
  - API Traefik : `${TRAEFIK_API_PORT}`

Traefik est configuré par `docker-compose.yml` :
- le provider Docker est activé (`--providers.docker=true`) ;
- les routes applicatives sont déclarées par les labels `traefik.*` des services ;
- les fichiers `docker/traefik/` restent des exemples ou supports de configuration statique, mais ne sont pas la source active du routage courant.

---

### postgres

- utilisé par le lobby et la persistance métier
- ports : `${POSTGRES_PORT}`
- scripts d’initialisation : `sql/`

Bases créées :
- `postgres` (par défaut)
- `jeu` (métier)

---

### kafka (KRaft)

- broker unique en mode KRaft (sans Zookeeper)
- ports :
  - broker : `${KAFKA_PLAINTEXT_PORT}`
  - controller : `${KAFKA_CONTROLLER_PORT}`

La création automatique des topics est **désactivée**.

#### initialisation des topics

Après le démarrage du stack :

```bash
scripts/bootstrap-topics.sh
```

Les topics sont définis via la variable :

```env
TOPICS=cab.commands,cab.events,cabinet.joueurs.evenements,cabinet.tables.evenements,cabinet.parties.evenements
```

---

### kafka ui (optionnel)

- interface web de visualisation Kafka
- accès via Traefik :
  - `https://kafka.${TRAEFIK_DOMAIN}`

Authentification :
- utilisateur : `${KAFKA_UI_USERNAME}`
- mot de passe : `${KAFKA_UI_PASSWORD}`

---

### registry (apicurio)

- stockage des schémas (avro / jsonschema)
- port : `${REGISTRY_HTTP_PORT}`
- accès via Traefik :
  - `https://registry.${TRAEFIK_DOMAIN}`

---

### rules-service (bre)

- moteur de règles (Java)
- port interne : `8081`
- accès via Traefik :
  - `https://rules.${TRAEFIK_DOMAIN}`

Utilisé par le noyau via :

```env
CAB_RULES_BRE_URL=http://rules-service:8081
```

---

### services applicatifs

Les principaux services Python sont :

- `lobby` : gestion des tables et joueurs
- `api_moteur` : façade HTTP du moteur
- `cabinet` : noyau de jeu
- `ui_etat_joueur` : projections dédiées à l’UI
- `adapter-evenements` : pont Kafka
- `commande_moteur` : exécution des commandes

Pour le lancement d'une partie, le flux local attendu est :

1. le lobby publie `PartieLancee` avec `politique_timeout_partie` si la table en porte une ;
2. `adapter-evenements` copie cette politique dans la commande `partie.creer` ;
3. `commande_moteur` appelle `POST /parties` avec `configuration_partie.politique_timeout_partie` ;
4. `api_moteur` transmet cette configuration au noyau, qui la conserve dans `Etat.configuration_partie` ;
5. `commande_moteur` surveille l'inactivité à partir des événements `cab.events` ;
6. si le délai effectif est dépassé, `commande_moteur` produit `partie.terminer` sur `cab.commands` ;
7. le moteur termine la partie, publie `cab.D600.partie.terminer` sur `cab.events`, puis `commande_moteur` synchronise la table lobby associée.

Les détails opératoires du timeout sont dans `docs/architecture/timeout-parties.md`.

Chaque service dispose de son propre `Dockerfile` et de tests unitaires.

---

## scripts utiles

### reset kafka

```bash
./reset_kafka.sh
```

- supprime les données Kafka
- nécessite un redémarrage du stack

---

### initialisation rules-service

```bash
./init_rules_services.sh
```

- prépare l’environnement du moteur de règles
- utile lors des changements de version BRE

---

## arrêt et nettoyage

Arrêt simple :

```bash
docker compose down
```

Arrêt avec suppression des volumes :

```bash
docker compose down -v
```

> ⚠️ supprime les données postgres et kafka.

---

## diagnostic

### logs

```bash
docker compose logs -f
```

Ou par service :

```bash
docker compose logs -f rules-service
```

---

### état des conteneurs

```bash
docker compose ps
```

---

## remarques

- l’environnement local est conçu pour **le développement et l’expérimentation**, pas la production
- certaines configurations (sécurité, persistance, TLS) sont volontairement simplifiées
- les ports et domaines sont entièrement configurables via `.env`

---

## prochaines extensions possibles

- profils Docker Compose (dev / test / minimal)
- scripts de smoke tests automatisés
- documentation e2e (flux lobby → partie → fin)
