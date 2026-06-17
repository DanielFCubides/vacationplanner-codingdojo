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

### Backend services 
Starts all backend services without Kafka, or Selenium. Good for backend development and integration testing.

```sh
docker compose -f compose.yml -f docker/compose.dependencies.yml --profile app up
```

### Full stack
Starts everything: all services plus Redis, Kafka, and Selenium Grid.

```sh
docker compose -f compose.yml -f docker/compose.dependencies.yml --profile full up
```

### Observability stack
Starts OpenTelemetry Collector, Tempo, Prometheus, and Grafana.

```sh
docker compose -f docker/compose.observability.yml --profile observability up
```

## Running tests

```sh
docker compose -f docker/compose.tests.yml up vacation-planner-tests
docker compose -f docker/compose.tests.yml up flight-scrapper-tests
```

Or run tests locally inside the service folder:

```sh
cd vacation_stay_scrapper && pytest .
cd flight_service && pytest .
```
