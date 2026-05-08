# Execution Docker

Ce document decrit la cible Docker propre de la branche `essai-codex`.

Le fichier `docker-compose.yml` est le socle commun. Il ne publie pas de ports
hote et ne porte pas de domaines applicatifs. Les decisions d'exposition reseau
sont isolees dans des overlays:

| Environnement | Fichiers Compose | Fichier env | Role |
| --- | --- | --- | --- |
| Developpement MaisonNeuve | `docker-compose.yml` + `docker-compose.dev.yml` | `.env.dev` | travail local et tests avec ports non privilegies |
| Prod actuelle MaisonNeuve | branche `main` | `.env` historique sur MaisonNeuve | production existante jusqu'a migration validee |
| MaisonLinux / LAN stable | `docker-compose.yml` + `docker-compose.maisonlinux.yml` | `.env.maisonlinux` | futur hote Docker stable sur le LAN |
| Production publique future | `docker-compose.yml` + `docker-compose.prod.yml` | `.env.prod` | exposition publique stricte |

## Principe De Separation

- `docker-compose.yml` contient les services, reseaux internes, volumes,
  dependances, variables applicatives et healthchecks.
- Les overlays declarent les ports hote, les routes Traefik et les choix de
  diagnostic propres a l'environnement.
- `STACK_ID` prefixe les routers, middlewares et services Traefik pour eviter
  les collisions entre stacks.
- `STACK_NETWORK` est utilise par Traefik via `traefik.docker.network` et par
  la contrainte provider.
- Le provider Docker de Traefik filtre les conteneurs avec:

```text
Label(`cabinet.stack`,`<STACK_ID>`)
```

Chaque service porte aussi le label `cabinet.stack=<STACK_ID>`.

Le reseau Docker est externe. Avant un premier lancement, creer le reseau cible:

```bash
docker network create cabinet_dev_net
```

Adapter le nom au fichier `.env` utilise.

## Developpement MaisonNeuve

Le developpement ne monopolise pas `80` ou `443`.

Ports publies par `.env.dev.example`:

| Service | Port hote | Port conteneur | Remarque |
| --- | ---: | ---: | --- |
| Traefik HTTP | `18080` | `80` | acces applicatif |
| Traefik HTTPS | `18443` | `443` | essais TLS locaux si necessaire |
| Traefik API | `127.0.0.1:18085` | `8080` | dashboard/ping dev |
| Postgres | `127.0.0.1:15432` | `5432` | diagnostic local |
| Kafka broker | `127.0.0.1:19092` | `9092` | diagnostic local |
| Kafka controller | `127.0.0.1:19093` | `9093` | diagnostic local |
| Kafka UI | `127.0.0.1:18082` | `8080` | outil local |
| Apicurio | `127.0.0.1:18086` | `8080` | outil local |
| Rules service | `127.0.0.1:18081` | `8081` | diagnostic local |
| Lobby | `127.0.0.1:18083` | `8080` | diagnostic local |

Validation:

```bash
docker compose --env-file .env.dev.example -p cabinet-dev-test -f docker-compose.yml -f docker-compose.dev.yml config --quiet
```

Lancement:

```bash
cp .env.dev.example .env.dev
docker network create cabinet_dev_net
docker compose --env-file .env.dev -p cabinet-dev -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

Arret:

```bash
docker compose --env-file .env.dev -p cabinet-dev -f docker-compose.yml -f docker-compose.dev.yml down
```

## Prod Actuelle MaisonNeuve Depuis Main

MaisonNeuve heberge actuellement la production existante issue de `main`.
Cette production ne doit pas dependre des overlays de la branche `essai-codex`
tant que la migration n'est pas validee.

Retour arriere ou redemarrage de la prod actuelle:

```bash
git fetch
git switch main
docker compose up -d --build
```

Si un fichier env doit etre reconstruit, utiliser les secrets locaux reels de
MaisonNeuve. Le fichier `.env.maisonneuve-prod.example` de `essai-codex` sert
uniquement d'aide-memoire documentaire et ne remplace pas le `.env` production.

## MaisonLinux / LAN Stable

MaisonLinux est le futur hote Docker cible pour une stack stable LAN. Par
defaut, `.env.maisonlinux.example` expose Traefik sur `8080/8443` pour eviter
de reserver `80/443`. Si MaisonLinux devient l'entree LAN dediee, modifier
uniquement `.env.maisonlinux`:

```env
TRAEFIK_HTTP_PORT=80
TRAEFIK_HTTPS_PORT=443
```

Ports publies par defaut:

| Service | Port hote | Port conteneur | Remarque |
| --- | ---: | ---: | --- |
| Traefik HTTP | `8080` | `80` | entree LAN |
| Traefik HTTPS | `8443` | `443` | entree LAN TLS |
| Traefik API | `127.0.0.1:8085` | `8080` | diagnostic local hote |

Les services applicatifs et outils passent par Traefik. Postgres, Kafka,
Apicurio, rules-service et lobby ne publient pas de ports directs dans cet
overlay.

Validation:

```bash
docker compose --env-file .env.maisonlinux.example -p cabinet-maisonlinux-test -f docker-compose.yml -f docker-compose.maisonlinux.yml config --quiet
```

Lancement cible:

```bash
cp .env.maisonlinux.example .env.maisonlinux
docker network create cabinet_maisonlinux_net
docker compose --env-file .env.maisonlinux -p cabinet-maisonlinux -f docker-compose.yml -f docker-compose.maisonlinux.yml up -d --build
```

## Production Publique Future

La production publique future est plus stricte:

- seuls `80:80` et `443:443` sont publies;
- aucun port direct Postgres, Kafka, Kafka UI, Apicurio, rules-service ou lobby;
- pas de dashboard Traefik insecure;
- routes publiques uniquement sur l'entrypoint `websecure`;
- TLS active sur les routers publics.

Ports publies par `.env.prod.example`:

| Service | Port hote | Port conteneur |
| --- | ---: | ---: |
| Traefik HTTP | `80` | `80` |
| Traefik HTTPS | `443` | `443` |

Avant une production reelle, fournir la configuration TLS Traefik concrete
certificats, ACME ou configuration dynamique geree par l'infrastructure. Le
compose cible declare les routers TLS, mais ne commit pas de secrets ni de
certificats.

Validation:

```bash
docker compose --env-file .env.prod.example -p cabinet-prod-test -f docker-compose.yml -f docker-compose.prod.yml config --quiet
```

Lancement futur:

```bash
cp .env.prod.example .env.prod
docker network create cabinet_prod_net
docker compose --env-file .env.prod -p cabinet-prod -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## Notes Operatoires

Les topics Kafka restent ceux du projet:

```env
TOPICS=cab.commands,cab.events,cabinet.joueurs.evenements,cabinet.tables.evenements,cabinet.parties.evenements
```

Le mecanisme de timeout de partie n'est pas modifie par cette separation Docker.
Les variables `LOBBY_TIMEOUT_PARTIE_ACTIF` et
`LOBBY_TIMEOUT_PARTIE_DELAI_INACTIVITE_SECONDES` restent documentees dans les
fichiers env d'exemple.
Les details fonctionnels restent dans `docs/architecture/timeout-parties.md`.

Les contrats OpenAPI et JSON Schema ne sont pas affectes: la separation porte
sur l'orchestration, les ports hote, les domaines et le routage Traefik.
