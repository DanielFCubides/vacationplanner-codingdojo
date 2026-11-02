# Vacation / Stay Scrapper

Trip management service — Clean Architecture with PostgreSQL persistence.

## Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)

## Running the service

### With Docker Compose (recommended)

```shell
# From the repo root — starts vacation-planner + postgres
docker compose --profile app up -d
```

The service runs on `http://localhost:8000`. On startup it automatically runs
`alembic upgrade head` to provision the database schema.

### Locally

Requires a running PostgreSQL instance. Set `DATABASE_URL` before starting, or
provide the `POSTGRES_*` settings and `POSTGRES_PASSWORD_FILE` as used by the
Compose development stack:

```shell
export DATABASE_URL='postgresql+asyncpg://USER:PASSWORD@HOST:5432/DATABASE'
cd vacation_stay_scrapper
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | unset | Optional async PostgreSQL connection URL; overrides the individual `POSTGRES_*` settings |
| `POSTGRES_HOST` | `localhost` | PostgreSQL host when `DATABASE_URL` is unset |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_USER` | `vacation` | PostgreSQL user |
| `POSTGRES_DB` | `vacation_planner` | PostgreSQL database name |
| `POSTGRES_PASSWORD_FILE` | unset | Path to a file containing the PostgreSQL password |
| `DATABASE_ECHO` | `false` | Log all SQL statements |

## Database migrations

Migrations are managed with Alembic and run automatically on app startup.
To run them manually:

```shell
cd vacation_stay_scrapper
alembic upgrade head
```

## Running tests

Navigate to the project folder and run locally:

```shell
cd vacation_stay_scrapper
pytest .
```

Or via Docker:

```shell
docker compose up vacation-planner-tests
```
