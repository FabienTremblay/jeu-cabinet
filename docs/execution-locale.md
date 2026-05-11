# Execution Locale

La documentation Docker active est maintenant centralisee dans
`docs/execution-docker.md`.

Pour le developpement sur MaisonNeuve, utiliser l'overlay de developpement:

```bash
cp .env.dev.example .env.dev
docker network create cabinet_dev_net
docker compose --env-file .env.dev -p cabinet-dev -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

MaisonNeuve peut aussi heberger la production actuelle issue de `main`. Ne pas
supposer que MaisonNeuve est uniquement un poste de developpement. Pour
redemarrer la production actuelle, revenir sur `main` et utiliser sa procedure
historique:

```bash
git switch main
docker compose up -d --build
```

Voir `docs/execution-docker.md` pour:

- les commandes completes par environnement;
- la strategie `STACK_ID` / `STACK_NETWORK`;
- les ports exposes;
- le retour arriere MaisonNeuve/main;
- le futur lancement MaisonLinux/LAN stable;
- les contraintes de production publique future.
