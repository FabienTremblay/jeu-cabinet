# le-cabinet — pile jeu BPM/Events/Rules

Stack Docker pour un jeu orienté **processus** (Camunda 7 + DMN), **événements** (Kafka KRaft, topics gérés), **schémas** (Apicurio Registry, stockage `kafkasql`), **règles** (squelette Kogito/Drools), **observabilité** (healthchecks, Kafka-UI) & **reverse-proxy** (Traefik).

## Prérequis
- Ubuntu récent
- Docker Engine + Docker Compose plugin
- Ports locaux libres (cf. `.env.example`)

## Démarrage
1. Copier `.env.example` en `.env` et **changer les mots de passe**.
2. `make up`
3. Vérifier l’état: `make ps` et `make logs`

## Tests de santé
- **Postgres**: healthcheck intégré
- **Kafka**: healthcheck via `kafka-topics.sh --list`
- **Kafka-UI**: `http://localhost:8082/actuator/health`
- **Apicurio**: `./scripts/registry-check.sh` → doit renvoyer `200`
- **Camunda**: `http://localhost:8088/engine-rest/engine` (JSON)
- **Rules-service** (squelette): `http://localhost:8081/q/health` → `UP` (selon image)

## Consoles (par défaut locales)
- Camunda (Tomcat/Welcome/REST): `http://localhost:8088`
- Kafka UI: `http://localhost:8082`
- Apicurio Registry: `http://localhost:8080` (API `GET /apis/registry/v2`)

## Topics initiaux
Créer les 7 topics:
```sh
make topics
