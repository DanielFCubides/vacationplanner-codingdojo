COMPOSE ?= docker compose
PROJECT ?= vacationplanner-codingdojo
OBS_NETWORK := $(PROJECT)_observability

MAIN_FILES := --project-directory . -f compose.yml -f docker/compose.dependencies.yml
ALL_FILES := --project-directory . -f compose.yml -f docker/compose.dependencies.yml -f docker/compose.observability.yml
TEST_FILES := --project-directory . -f docker/compose.tests.yml
OBS_FILES := --project-directory . -f docker/compose.observability.yml

.DEFAULT_GOAL := help

.PHONY: help up build observability tests vacation-planner flight-service exec logs down stop restart ps config run network

network:
	@docker network inspect $(OBS_NETWORK) >/dev/null 2>&1 || docker network create $(OBS_NETWORK)

help:
	@printf '%s\n' \
		'Usage: make <target>' \
		'' \
		'Targets:' \
		'  up                  Start all services in detached mode' \
		'  build [SERVICE=x]   Build all main services or one main service' \
		'  observability       Start the observability stack in detached mode' \
		'  tests [SERVICE=x]   Run all tests or a specific service test suite' \
		'  vacation-planner     Start fe-client, auth-service, postgres, vacation-planner' \
		'  flight-service       Start flight-service, redis, selenium' \
		'  exec SERVICE=x       Open bash in a supported service' \
		'  logs [SERVICE=x]    Follow logs for main or observability services' \
		'  down [SERVICE=x]    Stop and remove all services or one service' \
		'  stop [SERVICE=x]    Stop all services or one service' \
		'  restart [SERVICE=x] Restart all services or one service' \
		'  run SERVICE=x       Run a service in detached mode' \
		'  ps                  Show stack status' \
		'  config              Render the combined compose config'

up: network
	$(COMPOSE) -p $(PROJECT) $(ALL_FILES) up -d

observability: network
	$(COMPOSE) -p $(PROJECT) $(OBS_FILES) up -d

build:
	@if [ -n "$(strip $(SERVICE))" ]; then \
		case "$(SERVICE)" in \
			auth-service|vacation-planner|flight-service|recommendations|fe-client) \
				$(COMPOSE) -p $(PROJECT) $(MAIN_FILES) build $(if $(filter 1 true yes on,$(NO_CACHE)),--no-cache,) $(SERVICE) ;; \
			*) \
				printf '%s\n' 'SERVICE must be one of: auth-service, vacation-planner, flight-service, recommendations, fe-client' >&2; \
				exit 1 ;; \
		esac; \
	else \
		$(COMPOSE) -p $(PROJECT) $(MAIN_FILES) build $(if $(filter 1 true yes on,$(NO_CACHE)),--no-cache,); \
	fi

tests:
	@if [ -n "$(strip $(SERVICE))" ]; then \
		case "$(SERVICE)" in \
			vacation-planner) runner=vacation-planner-tests ;; \
			flight-service) runner=flight-scrapper-tests ;; \
			*) \
				printf '%s\n' 'SERVICE must be vacation-planner or flight-service' >&2; \
				exit 1 ;; \
		esac; \
		$(COMPOSE) -p $(PROJECT) $(TEST_FILES) up -d $$runner; \
	else \
		$(COMPOSE) -p $(PROJECT) $(TEST_FILES) up -d; \
	fi

vacation-planner: network
	$(COMPOSE) -p $(PROJECT) $(MAIN_FILES) up -d fe-client auth-service postgres vacation-planner

flight-service: network
	$(COMPOSE) -p $(PROJECT) $(MAIN_FILES) up -d flight-service redis-cache redis-ui selenium-hub node-1 node-2

exec:
	@if [ -n "$(strip $(SERVICE))" ]; then \
		case "$(SERVICE)" in \
			flight-service|vacation-planner|postgres|redis-cache|auth-service) \
				$(COMPOSE) -p $(PROJECT) $(MAIN_FILES) exec $(SERVICE) bash ;; \
			*) \
				printf '%s\n' 'SERVICE is required and must be one of: flight-service, vacation-planner, postgres, redis-cache, auth-service' >&2; \
				exit 1 ;; \
		esac; \
	else \
		printf '%s\n' 'SERVICE is required and must be one of: flight-service, vacation-planner, postgres, redis-cache, auth-service' >&2; \
		exit 1; \
	fi

logs:
	@if [ -n "$(strip $(SERVICE))" ]; then \
		case "$(SERVICE)" in \
			otel-collector|tempo|prometheus|grafana|loki) \
				$(COMPOSE) -p $(PROJECT) $(OBS_FILES) logs -f $(SERVICE) ;; \
			*) \
				$(COMPOSE) -p $(PROJECT) $(MAIN_FILES) logs -f $(SERVICE) ;; \
		esac; \
	else \
		$(COMPOSE) -p $(PROJECT) $(MAIN_FILES) logs -f; \
	fi

down:
	@if [ -n "$(strip $(SERVICE))" ]; then \
		case "$(SERVICE)" in \
			observability) $(COMPOSE) -p $(PROJECT) $(OBS_FILES) down ;; \
			*) $(COMPOSE) -p $(PROJECT) $(MAIN_FILES) rm -sf $(SERVICE) ;; \
		esac; \
	else \
		$(COMPOSE) -p $(PROJECT) $(ALL_FILES) down; \
	fi

stop:
	@if [ -n "$(strip $(SERVICE))" ]; then \
		case "$(SERVICE)" in \
			observability) $(COMPOSE) -p $(PROJECT) $(OBS_FILES) stop ;; \
			*) $(COMPOSE) -p $(PROJECT) $(MAIN_FILES) stop $(SERVICE) ;; \
		esac; \
	else \
		$(COMPOSE) -p $(PROJECT) $(ALL_FILES) stop; \
	fi

restart:
	@if [ -n "$(strip $(SERVICE))" ]; then \
		case "$(SERVICE)" in \
			observability) $(COMPOSE) -p $(PROJECT) $(OBS_FILES) restart ;; \
			*) $(COMPOSE) -p $(PROJECT) $(MAIN_FILES) restart $(SERVICE) ;; \
		esac; \
	else \
		$(COMPOSE) -p $(PROJECT) $(ALL_FILES) restart; \
	fi

run: network
	@if [ -n "$(strip $(SERVICE))" ]; then \
		$(COMPOSE) -p $(PROJECT) $(MAIN_FILES) up -d $(SERVICE); \
	else \
		printf '%s\n' 'SERVICE is required. Example: make run SERVICE=auth-service' >&2; \
		exit 1; \
	fi

ps:
	$(COMPOSE) -p $(PROJECT) $(ALL_FILES) ps

config:
	$(COMPOSE) -p $(PROJECT) $(ALL_FILES) config
