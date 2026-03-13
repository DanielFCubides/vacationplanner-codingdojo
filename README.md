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

### Frontend + vacation planner backend
For UI development. Starts only the React frontend and the vacation planner API.

```sh
docker compose --profile frontend up
```

### All backend services (no infrastructure)
Starts all three backend services without Redis, Kafka, or Selenium. Good for backend development and integration testing.

```sh
docker compose --profile app up
```

### Full stack
Starts everything: all services plus Redis, Kafka, and Selenium Grid.

```sh
docker compose --profile full up
```

## Running tests

```sh
docker compose up vacation-planner-tests
docker compose up flight-scrapper-tests
```

Or run tests locally inside the service folder:

```sh
cd vacation_stay_scrapper && pytest .
cd flight_scrapper_service && pytest .
```
