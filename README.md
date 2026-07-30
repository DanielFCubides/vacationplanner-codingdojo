[![Build Status](https://github.com/DanielFCubides/vacationplanner-codingdojo/actions/workflows/docker-image.yml/badge.svg)](https://github.com/DanielFCubides/vacationplanner-codingdojo/actions)

# Vacation Planner

A microservices system for planning vacations — aggregating flights, stays, activities, and recommendations.

## Services

| Service | Port | Description |
|---|---|---|
| `auth-service` | 8000 | Authentication service |
| `vacation-planner` | 8001 | Trip management and stay scraping |
| `flight-service` | 8002 | Flight search (REST / gRPC / GraphQL) |
| `recommendations` | — | Recommendation engine |
| `fe-client` | 3001 | React frontend |

## Running with Make

Requires Docker Desktop (or Docker Engine with the Compose plugin) and `make`.

List all available targets:

```sh
make help
```

### Start services

Start the complete application and observability stack in detached mode:

```sh
make up
```

Start only the vacation planner group: frontend, authentication, PostgreSQL, and vacation planner:

```sh
make vacation-planner
```

Start only the flight service group: flight service, Redis, and Selenium Grid:

```sh
make flight-service
```

Start only the observability services (OpenTelemetry Collector, Tempo, Loki, Prometheus, and Grafana):

```sh
make observability
```

### Build services

Build every main application service:

```sh
make build
```

Build one service, optionally without the Docker build cache:

```sh
make build SERVICE=flight-service
make build SERVICE=flight-service NO_CACHE=true
```

### Tests

Start all test containers:

```sh
make tests
```

Start the test container for a single service:

```sh
make tests SERVICE=vacation-planner
make tests SERVICE=flight-service
```

### Inspect and manage services

```sh
# Show container status and render the resolved Compose configuration.
make ps
make config

# Follow all application logs or one service's logs.
make logs
make logs SERVICE=flight-service
make logs SERVICE=tempo

# Open a Bash shell in a supported service.
make exec SERVICE=flight-service

# Start, stop, restart, or remove one service.
make run SERVICE=auth-service
make stop SERVICE=auth-service
make restart SERVICE=auth-service
make down SERVICE=auth-service

# Stop and remove the complete stack, including observability services.
make down
```
