# exécution locale — environnement de développement

Ce document décrit comment lancer et utiliser le projet **jeu Cabinet** en environnement local à l’aide de `docker-compose`.

L’objectif est de fournir un environnement reproductible incluant :
- le noyau applicatif,
- les services API,
- Kafka (KRaft, broker unique),
- le registry de schémas,
- le moteur de règles (BRE),
- Traefik comme point d’entrée.

---

## prérequis

- docker (20+ recommandé)
- docker-compose v2
- make (optionnel mais recommandé)
- ports locaux disponibles (voir plus bas)

---

## configuration

### fichier `.env`

Le projet utilise un fichier `.env` chargé par `docker-compose`.

1. copier le fichier d’exemple :

```bash
cp .env.example .env
```

2. ajuster au besoin :
- domaine (`TRAEFIK_DOMAIN`)
- ports exposés
- mots de passe (postgres, kafka-ui)

> ⚠️ le fichier `.env` **ne doit pas** être versionné.

---

## démarrage rapide

À la racine du dépôt :

```bash
docker-compose up --build
```

ou en arrière-plan :

```bash
docker-compose up -d --build
```

Les services démarrent dans l’ordre défini par les dépendances Docker.

---

## services principaux

### traefik

- rôle : reverse-proxy et routage HTTP
- ports :
  - HTTP : `${TRAEFIK_HTTP_PORT}` (ex. 80)
  - API Traefik : `${TRAEFIK_API_PORT}`

Les routes sont définies dans :
- `docker/traefik/traefik.yml`
- `docker/traefik/dynamic/routers.yml`

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
TOPICS=example.topic_one,example.topic_two
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
docker-compose down
```

Arrêt avec suppression des volumes :

```bash
docker-compose down -v
```

> ⚠️ supprime les données postgres et kafka.

---

## diagnostic

### logs

```bash
docker-compose logs -f
```

Ou par service :

```bash
docker-compose logs -f rules-service
```

---

### état des conteneurs

```bash
docker-compose ps
```

---

## remarques

- l’environnement local est conçu pour **le développement et l’expérimentation**, pas la production
- certaines configurations (sécurité, persistance, TLS) sont volontairement simplifiées
- les ports et domaines sont entièrement configurables via `.env`

---

## prochaines extensions possibles

- profils docker-compose (dev / test / minimal)
- scripts de smoke tests automatisés
- documentation e2e (flux lobby → partie → fin)

