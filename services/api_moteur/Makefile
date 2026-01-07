COMPOSE?=docker-compose
SVC=api-moteur

.PHONY: build up down logs restart curl-health smoke

build:
	$(COMPOSE) build $(SVC)

up:
	$(COMPOSE) up -d $(SVC)

down:
	$(COMPOSE) stop $(SVC)

logs:
	$(COMPOSE) logs -f $(SVC)

restart: down up logs

curl-health:
	curl -sS http://api.cabinet.localhost/health | jq .

smoke:
	curl -sS http://api.cabinet.localhost/version | jq .
