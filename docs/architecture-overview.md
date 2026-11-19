# Vacation Planner — Architecture Overview

A microservices system for planning vacations, aggregating flights, stays,
activities, and recommendations.

## 1. Architecture summary

The system is a set of independent services orchestrated by Docker Compose,
each owning a domain, a database (where relevant), and a presentation layer.
Services communicate over HTTP (REST) and Kafka. Observability is centralized
through an OpenTelemetry Collector that fans out to Tempo, Prometheus, Loki,
and Grafana.

The codebase follows a layered structure:

- **domain** — entities, value objects, repositories, and use cases.
- **infrastructure** — external integrations (Keycloak, Redis, PostgreSQL,
  Kafka, Selenium) and adapters.
- **presentation** — HTTP/GRPC/GraphQL endpoints and response mapping.

## 2. Main services and responsibilities

| Service | Responsibility |
|---|---|
| `auth-service` | JWT authentication and authorization via Keycloak (OIDC). |
| `vacation-planner` | Trip CRUD, stays, flights, activities, budget, and traveler management. Owns PostgreSQL. |
| `flight-service` | Flight search via external scrapers (Avianca, Google) and feature flags. Supports REST, gRPC, and GraphQL presentations. |
| `recommendations` | Recommendation engine consuming flight events from Kafka. |
| `fe-client` | React frontend with Keycloak OAuth login. |
| `redis-cache` | Caching and pub/sub. |
| `postgres` | Persistent data for vacation-planner. |
| `selenium-hub` / `node-1` / `node-2` | Selenium Grid for flight scraping. |
| Observability stack | OpenTelemetry Collector, Tempo, Prometheus, Loki, Grafana. |

## 3. How services communicate

- **HTTP/REST** — `fe-client` → `auth-service` and `vacation-planner`;
  `fe-client` → `flight-service` (REST, gRPC, or GraphQL depending on the
  `SERVER` env var).
- **Kafka** — `flight-service` publishes flight events; `recommendations`
  consumes them.
- **Redis** — caching and pub/sub between services.
- **PostgreSQL** — vacation-planner persists trips and related entities.
- **Keycloak** — centralized authentication for all services.

## 4. Available endpoints

### `auth-service` (port 8000)

| Method | Path | Description |
|---|---|---|
| `GET` | `/auth/login` | OIDC callback: exchanges the authorization code for tokens, creates a Redis session, sets the `session_id` cookie, and redirects to the frontend. |
| `POST` | `/auth/logout` | Terminates the Keycloak and Redis session and clears the frontend cookie. |
| `GET` | `/auth/silent_check` | Validates the active session and returns user info; performs token introspection and refresh transparently if needed. |
| `GET` | `/{service_path:path}` | Reverse proxy: routes to downstream services (e.g. `/vacation-planner/api/trips`) and injects `Authorization: Bearer <token>` from the session. |
| `GET` | `/health` | Health check. |

### `vacation-planner` (port 8001)

Base path: `/api/trips`. All endpoints require authentication.

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/trips` | Create a new trip (201). |
| `GET` | `/api/trips` | List all trips owned by the current user. |
| `GET` | `/api/trips/{trip_id}` | Get a trip by ID. |
| `PUT` | `/api/trips/{trip_id}` | Update a trip. |
| `PATCH` | `/api/trips/{trip_id}/status` | Update trip status. |
| `DELETE` | `/api/trips/{trip_id}` | Delete a trip. |
| `POST` | `/api/trips/{trip_id}/flights` | Add a flight to a trip (201). |
| `PUT` | `/api/trips/{trip_id}/flights/{flight_id}` | Update a flight. |
| `PATCH` | `/api/trips/{trip_id}/flights/{flight_id}/status` | Update a flight's status. |
| `POST` | `/api/trips/{trip_id}/accommodations` | Add an accommodation (201). |
| `PUT` | `/api/trips/{trip_id}/budget` | Update the trip budget. |
| `POST` | `/api/trips/{trip_id}/activities` | Add an activity (201). |
| `PATCH` | `/api/trips/{trip_id}/accommodations/{accommodation_id}/status` | Update an accommodation's status. |
| `PATCH` | `/api/trips/{trip_id}/activities/{activity_id}/status` | Update an activity's status. |

### `flight-service` (port 8001)

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Health check (also serves the welcome message when the `WELCOME_MESSAGE_FLAG` feature flag is enabled). |
| `POST` | `/get_flights` | Search flights. Body: `{"airline": "...", "search_params": {"origin", "destination", "departure_date", "return_date", "passengers"}}`. |

The service is configured with `SERVER=rest` (default), `grpc`, or `graphql`.

### `recommendations`

Consumes flight events from Kafka and exposes recommendation endpoints (see the service's own documentation).

### `fe-client` (port 3001)

React frontend. Login at `/login`, protected dashboard at `/dashboard`. Supports two OAuth 2.0 flows with Keycloak: direct (resource owner password credentials) and standard (authorization code grant).

## 5. Authentication and authorization

All services authenticate through Keycloak (OIDC). The frontend never handles tokens directly:

1. The user logs in via `fe-client` → `auth-service` (`GET /auth/login`).
2. `auth-service` exchanges the authorization code for tokens and stores the JWT in Redis.
3. A `session_id` cookie is set on the frontend.
4. For downstream requests, the frontend calls `auth-service` with the `session_id` cookie.
5. `auth-service` injects `Authorization: Bearer <token>` into the request and forwards it.
6. Downstream services validate the JWT and use its claims (e.g. `sub`) for authorization.

The frontend also supports a direct OAuth flow (resource owner password credentials) that talks to Keycloak directly.

## 6. Configuration

### Root `.env` (Docker Compose)

| Variable | Default | Purpose |
|---|---|---|
| `SERVER` | `rest` | Flight service presentation: `rest`, `grpc`, or `graphql`. |
| `KEYCLOAK_SERVER_URL` | `https://keycloak.dfcubidesc.com` | Keycloak server URL. |
| `KEYCLOAK_CLIENT_ID` | `auth-service` | Keycloak client ID. |
| `KEYCLOAK_REALM_NAME` | `habit-tracker` | Keycloak realm name. |
| `KEYCLOAK_REDIRECT_URI` | `http://localhost:8000/auth/login` | Redirect URI for the auth service. |
| `FRONTEND_URL` | `http://localhost:3001` | Frontend URL. |
| `REDIS_HOST` | `redis-cache` | Redis host. |
| `REDIS_PORT` | `6379` | Redis port. |
| `REDIS_DB` | `0` | Redis database. |
| `OTEL_SERVICE_NAME_{AUTH,VACATION,FLIGHT}` | service name | Resource name reported per service. |
| `OTEL_EXPORTER_LOGS_ENDPOINT` | `http://otel-collector:4318/v1/logs` | OpenTelemetry logs endpoint. |
| `DATABASE_HOST` | `postgres` | PostgreSQL host. |
| `DATABASE_USER` | `vacation` | PostgreSQL user. |
| `DATABASE_NAME` | `vacation_planner` | PostgreSQL database. |
| `DATABASE_ECHO` | `false` | Enable SQLAlchemy echo. |
| `MIN_DELAY_ATTEMPT` | `60` | Minimum delay between attempts. |
| `MIN_FAILURE_ATTEMPTS` | `3` | Minimum failure attempts. |
| `KEYCLOAK_BASE_URL` | `https://keycloak.dfcubidesc.com` | Keycloak base URL. |
| `KEYCLOAK_REALM` | `habit-tracker` | Keycloak realm. |
| `LOG_LEVEL` | `INFO` | Logging level. |
| `LOG_FILE` | `` | Log file path. |

### `fe-client/.env.development`

| Variable | Default | Purpose |
|---|---|---|
| `VITE_KEYCLOAK_URL` | `https://keycloak.dfcubidesc.com` | Keycloak URL. |
| `VITE_KEYCLOAK_REALM` | `habit-tracker` | Keycloak realm. |
| `VITE_KEYCLOAK_CLIENT_ID` | `auth-service` | Keycloak client ID. |
| `VITE_KEYCLOAK_REDIRECT_URI` | `http://localhost:8000/auth/login` | Redirect URI. |
| `VITE_KEYCLOAK_SCOPES` | `openid profile email` | OAuth scopes. |
| `VITE_AUTH_BACKEND_URL` | `http://localhost:8002` | Backend URL for auth. |
| `VITE_DEMO_DIRECT_USERNAME` | `demo-direct` | Demo direct-flow username. |
| `VITE_DEMO_DIRECT_PASSWORD` | `demo123` | Demo direct-flow password. |
| `VITE_DEMO_STANDARD_USERNAME` | `demo-oauth` | Demo standard-flow username. |
| `VITE_DEMO_STANDARD_PASSWORD` | `demo123` | Demo standard-flow password. |
| `VITE_MOCK_LOGIN_DELAY` | `1000` | Mock login delay. |
| `VITE_MOCK_TOKEN_DELAY` | `800` | Mock token delay. |
| `VITE_MOCK_LOGOUT_DELAY` | `500` | Mock logout delay. |
| `VITE_INSTANT_MOCK_RESPONSES` | `false` | Instant mock responses. |

### Secrets

| File | Default | Purpose |
|---|---|---|
| `secrets/keycloak_client_secret_key` | `dummy-keycloak-client-secret` | Keycloak client secret. |
| `secrets/redis_password` | `dummy-redis-password` | Redis password. |
| `secrets/postgres_password` | `dummy-postgres-password` | PostgreSQL password. |

## 7. Technologies and frameworks

- **Backend**: Python, FastAPI, Flask, SQLAlchemy (async), pydantic, python-keycloak, `requests`, OpenTelemetry.
- **Frontend**: React (JSX), TypeScript models, Vite, Tailwind CSS, Keycloak OAuth.
- **Infrastructure**: Docker Compose, PostgreSQL 16, Redis, Kafka, Selenium Grid, OpenTelemetry Collector/Tempo/Loki/Prometheus/Grafana.
- **Build**: Docker multi-stage builds, Alembic migrations.

## 8. Potential architectural improvements

- **Centralize configuration**: move shared config into a single package consumed by all services.
- **Consistent telemetry setup**: standardize the OTel setup across services (currently `auth-service`, `vacation-planner`, and `flight-service` each have their own).
- **Simplify presentation layers**: `flight-service` has three presentation implementations (REST, gRPC, GraphQL) that could be consolidated.
- **Add API gateway**: route all frontend traffic through a single gateway for consistent auth and routing.
- **Move `recommendations` to Python**: currently a Node.js service; consider aligning with the Python backend stack.
- **Add health checks and readiness probes** to compose dependencies.
- **Use a shared database schema** for cross-service queries instead of duplicating entities.
- **Add rate limiting and circuit breakers** for external calls.
- **Add end-to-end tests** across services.
```