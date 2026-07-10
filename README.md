# Vacation Planner

A microservices system for planning vacations — aggregating flights, stays, activities, and recommendations.

## Services

| Service | Port | Description |
|---|---|---|
| `vacation-planner` | 8000 | Trip management and stay scraping |
| `flight-scrapper` | 8001 | Flight search (REST / gRPC / GraphQL) |
| `recommendations` | — | Recommendation engine |
| `fe-client` | 5173 | React frontend |

## Running the stack

All day-to-day operations go through `make`, which wraps the Docker Compose files and creates the shared observability network automatically. Run `make` (or `make help`) to list every target.

### Everything

```sh
make up
```

Starts all services plus the observability stack in detached mode.

### Partial stacks

```sh
make vacation-planner    # fe-client, auth-service, postgres, vacation-planner
make flight-service      # flight-service, redis, redis-ui, selenium grid
make observability       # OpenTelemetry Collector, Tempo, Prometheus, Grafana, Loki
make run SERVICE=auth-service    # any single service
```

### Building images

```sh
make build                          # build all main services
make build SERVICE=fe-client        # build one service
make build NO_CACHE=1               # build without the Docker cache
```

`SERVICE` must be one of: `auth-service`, `vacation-planner`, `flight-service`, `recommendations`, `fe-client`.

### Managing the stack

```sh
make ps                          # show stack status
make logs                        # follow logs for all main services
make logs SERVICE=grafana        # follow logs for one service (main or observability)
make exec SERVICE=vacation-planner    # open a bash shell inside a service
make restart [SERVICE=x]         # restart everything or one service
make stop [SERVICE=x]            # stop everything or one service
make down [SERVICE=x]            # stop and remove everything or one service
make down SERVICE=observability  # tear down only the observability stack
make config                      # render the combined compose config
```

`make exec` supports: `flight-service`, `vacation-planner`, `postgres`, `redis-cache`, `auth-service`.

## Running tests

```sh
make tests                            # run all test suites
make tests SERVICE=vacation-planner   # vacation_stay_scrapper tests
make tests SERVICE=flight-service     # flight_scrapper_service tests
```

Or run tests locally inside the service folder:

```sh
cd vacation_stay_scrapper && pytest .
cd flight_service && pytest .
```

## Running without make

The Makefile is a thin wrapper over Docker Compose; the equivalent raw commands are:

```sh
docker compose -f compose.yml -f docker/compose.dependencies.yml --profile app up    # backend services
docker compose -f compose.yml -f docker/compose.dependencies.yml --profile full up  # full stack
docker compose -f docker/compose.observability.yml --profile observability up       # observability
docker compose -f docker/compose.tests.yml up vacation-planner-tests                # tests
```
