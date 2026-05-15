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

## Migrations SQL Sur Base Existante

Les scripts montes dans `/docker-entrypoint-initdb.d/` sont executes seulement
lors de l'initialisation d'un volume Postgres vide. Ils servent a creer une base
neuve. Les evolutions rejouables sur une base existante passent par la
mecanique de migrations maison.

La table applicative `schema_migrations` suit les migrations appliquees:

- `version` : identifiant stable, par exemple `001` ;
- `nom` : nom du fichier SQL applique ;
- `applique_le` : date d'application.

Les migrations vivent dans `sql/migrations/` et sont appliquees dans l'ordre
lexicographique par `sql/apply-migrations.sh`. Chaque migration doit rester
idempotente autant que possible (`create table if not exists`,
`create index if not exists`, etc.).

Sur une base neuve, le script d'init Postgres applique aussi les migrations
apres `sql/01-init-jeu.sql`. Sur une base existante, relancer explicitement le
script de migrations.

Ne pas utiliser `docker compose down -v` pour forcer la relecture de
`sql/01-init-jeu.sql`: cette commande supprime les volumes et detruit les
donnees locales.

### Application Sur MaisonLinux

Verifier d'abord que la stack est demarree :

```bash
docker compose --env-file .env.maisonlinux -p cabinet-maisonlinux -f docker-compose.yml -f docker-compose.maisonlinux.yml ps
```

Appliquer les migrations :

```bash
docker compose --env-file .env.maisonlinux -p cabinet-maisonlinux -f docker-compose.yml -f docker-compose.maisonlinux.yml exec postgres /opt/sql/apply-migrations.sh
```

Controler les migrations appliquees :

```bash
docker compose --env-file .env.maisonlinux -p cabinet-maisonlinux -f docker-compose.yml -f docker-compose.maisonlinux.yml exec postgres psql -U jeu -d jeu -c "select version, nom, applique_le from schema_migrations order by version"
```

### Application En Developpement Local

Avec l'overlay de developpement :

```bash
docker compose --env-file .env.dev -p cabinet-dev -f docker-compose.yml -f docker-compose.dev.yml exec postgres /opt/sql/apply-migrations.sh
```

Equivalent Makefile :

```bash
make migrate-dev
```

Controler ensuite :

```bash
docker compose --env-file .env.dev -p cabinet-dev -f docker-compose.yml -f docker-compose.dev.yml exec postgres psql -U jeu -d jeu -c "select version, nom, applique_le from schema_migrations order by version"
```

### Exemple `lobby_sessions`

La migration `sql/migrations/001_lobby_sessions.sql` cree la table
`lobby_sessions` sur une base existante :

```sql
create table if not exists lobby_sessions (
  id_session text primary key,
  id_joueur text not null references lobby_joueurs(id_joueur),
  statut text not null check (statut in ('active', 'absente', 'expiree')),
  dernier_heartbeat timestamptz not null,
  expire_le timestamptz not null,
  cree_le timestamptz not null default now(),
  maj_le timestamptz not null default now()
);

create index if not exists idx_lobby_sessions_id_joueur
  on lobby_sessions(id_joueur);

create index if not exists idx_lobby_sessions_statut_expire
  on lobby_sessions(statut, expire_le);
```

Controler l'existence de la table :

```bash
docker compose --env-file .env.maisonlinux -p cabinet-maisonlinux -f docker-compose.yml -f docker-compose.maisonlinux.yml exec postgres psql -U jeu -d jeu -c "\\d lobby_sessions"
```

### Fusion De Branche Vers `main`

Avant de fusionner une branche qui ajoute une migration SQL :

1. verifier que le fichier `sql/migrations/<version>_<nom>.sql` est present ;
2. verifier que `docker-compose.yml` monte `sql/apply-migrations.sh` et
   `sql/migrations/` dans le conteneur Postgres ;
3. appliquer les migrations sur un environnement de developpement ;
4. rejouer le script une seconde fois pour valider l'idempotence ;
5. documenter dans l'issue les commandes executees et le resultat.

Apres fusion sur une base MaisonLinux existante, appliquer explicitement :

```bash
docker compose --env-file .env.maisonlinux -p cabinet-maisonlinux -f docker-compose.yml -f docker-compose.maisonlinux.yml exec postgres /opt/sql/apply-migrations.sh
```

Equivalent Makefile :

```bash
make migrate-maisonlinux
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

Logs utiles pour diagnostiquer le timeout:

```bash
docker compose logs -f moteur-commands
docker compose logs -f api-moteur
docker compose logs -f lobby
docker compose logs -f adapter-evenements
```

Les details fonctionnels et la discipline par couche restent dans
`docs/architecture/timeout-parties.md`. Le parcours UI est documente dans
`docs/ui/flux-auth-lobby-table.md`.

La separation Docker ne change pas les contrats OpenAPI et JSON Schema: elle
porte sur l'orchestration, les ports hote, les domaines et le routage Traefik.

## Diagnostic BRE Poweruser

Le diagnostic créateur des skins poweruser utilise le service `api-moteur`, car son
image contient le package Python `services`.

La commande doit suivre la même stratégie d'environnement que les autres
commandes Docker du projet : `--env-file`, `-p` et overlays Compose explicites.
Exemple en développement MaisonNeuve :

```bash
docker compose --env-file .env.dev -p cabinet-dev \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin exemple_mandat_austerite_overlay
```

`--no-deps` évite de démarrer Kafka, Postgres ou `rules-service`. Le diagnostic
lit seulement le fichier `skin.yaml` de l'overlay.

La commande par identifiant consulte `donnees/cabinet/skins/catalogue.yaml`.
Après ajout ou renommage d'une entrée de catalogue ou d'un overlay sous
`donnees/cabinet/skins/`, reconstruire donc `api-moteur` avant de diagnostiquer
cette skin par identifiant.

Pour une skin en brouillon qui n’est pas encore copiée dans l’image
`api-moteur`, monter explicitement le dossier et utiliser `--skin-yaml` :

```bash
docker compose --env-file .env.dev -p cabinet-dev \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm --no-deps \
  -v "$PWD/<chemin-vers-la-skin>:/skin-a-tester" \
  api-moteur \
  python -m services.cabinet.outils.diagnostiquer_skin \
  --skin-yaml /skin-a-tester/skin.yaml
```
