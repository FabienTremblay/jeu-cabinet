SHELL := /bin/bash

.PHONY: up down logs ps nuke topics build-rules up-rules logs-rules

up:
	docker compose up -d --remove-orphans

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

ps:
	docker compose ps

topics:
	./scripts/bootstrap-topics.sh

nuke:
	docker compose down -v --remove-orphans
	docker volume prune -f

health:
	@echo '--- Traefik ---';  curl -sf http://localhost:${TRAEFIK_API_PORT}/ping && echo OK || echo FAIL
	@echo '--- Kafka-UI ---'; curl -sf http://localhost:${KAFKA_UI_PORT}/actuator/health >/dev/null && echo OK || echo FAIL
	@echo '--- Registry ---'; curl -sf http://localhost:${REGISTRY_HTTP_PORT}/apis/registry/v2 >/dev/null && echo OK || echo FAIL
	@echo '--- Rules ---';   curl -sf http://localhost:${RULES_HTTP_PORT}/q/health >/dev/null && echo OK || echo FAIL

build-rules:
	$(info == Build image rules-service ==)
	docker compose build rules-service

up-rules: build-rules
	docker compose up -d rules-service

logs-rules:
	docker compose logs -f --tail=200 rules-service

