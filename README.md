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

## Local configuration

Before starting the stack, create the configuration files below. All values are
dummy development examples, including connection strings and credentials. Replace
them with values for your environment and never commit real secrets.

Create a root `.env` for Docker Compose:

```env
# Flight service
SERVER=rest

# Auth service and Keycloak
KEYCLOAK_SERVER_URL=https://keycloak.example.test
KEYCLOAK_CLIENT_ID=auth-service
KEYCLOAK_REALM_NAME=vacation-planner
KEYCLOAK_REDIRECT_URI=http://localhost:8002/auth/login
FRONTEND_URL=http://localhost:3001

# Redis
REDIS_HOST=redis-cache
REDIS_PORT=6379
REDIS_DB=0

# OpenTelemetry logs
OTEL_SERVICE_NAME=auth-service
OTEL_EXPORTER_LOGS_ENDPOINT=http://otel-collector:4318/v1/logs

# Vacation planner database
DATABASE_HOST=postgres
DATABASE_USER=vacation
DATABASE_NAME=vacation_planner
DATABASE_ECHO=false

# Vacation planner optional settings
MIN_DELAY_ATTEMPT=60
MIN_FAILURE_ATTEMPTS=3
KEYCLOAK_BASE_URL=https://keycloak.example.test
KEYCLOAK_REALM=vacation-planner
LOG_LEVEL=INFO
LOG_FILE=
```

Create `fe-client/.env.development` for the frontend:

```env
VITE_KEYCLOAK_URL=https://keycloak.example.test
VITE_KEYCLOAK_REALM=vacation-planner
VITE_KEYCLOAK_CLIENT_ID=auth-service
VITE_KEYCLOAK_REDIRECT_URI=http://localhost:8002/auth/login
VITE_KEYCLOAK_SCOPES=openid profile email
VITE_AUTH_BACKEND_URL=http://localhost:8002

# Optional mock-login configuration
VITE_DEMO_DIRECT_USERNAME=demo-direct
VITE_DEMO_DIRECT_PASSWORD=demo123
VITE_DEMO_STANDARD_USERNAME=demo-oauth
VITE_DEMO_STANDARD_PASSWORD=demo123
VITE_MOCK_LOGIN_DELAY=1000
VITE_MOCK_TOKEN_DELAY=800
VITE_MOCK_LOGOUT_DELAY=500
VITE_INSTANT_MOCK_RESPONSES=false
```

Create the `secrets` directory and these files:

```text
# secrets/keycloak_client_secret_key
dummy-keycloak-client-secret

# secrets/redis_password
dummy-redis-password

# secrets/postgres_password
dummy-postgres-password
```

Docker Compose mounts the Keycloak and Redis secrets for `auth-service`, the
Redis secret for `flight-service`, and the PostgreSQL password secret for
`vacation-planner`. The planner constructs its database connection from
`DATABASE_HOST`, `DATABASE_USER`, `DATABASE_NAME`, and `postgres_password`.
PostgreSQL reads the same password from the mounted secret. The
`secrets/.gitignore` file keeps secret files out of Git.

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
