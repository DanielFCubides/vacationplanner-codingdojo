# PostgreSQL Persistence — Full Implementation (Phases 1–5)

## Summary

Replaces the in-memory trip repository with a full PostgreSQL persistence stack.
All trip data now survives service restarts and is scoped by authenticated user.

## What changed

### Infrastructure (Phases 1–3)
- **Async engine + session** — `AsyncSession` via SQLAlchemy asyncio, managed by a
  FastAPI dependency that commits on clean exit and rolls back on error.
- **Settings** — `DATABASE_URL` and `DATABASE_ECHO` read from environment; defaults
  target the Docker Compose Postgres service.
- **Docker Compose** — `postgres:16-alpine` added to the `app` and `full` profiles;
  `vacation-planner` declares `depends_on: postgres` and receives `DATABASE_URL`.
- **ORM models** — Six SQLAlchemy 2.0 declarative models (`Trip`, `Traveler`, `Flight`,
  `Accommodation`, `Activity`, `BudgetCategory`) with:
  - `BIGSERIAL` PKs on `trips` and `budget_categories`; `STRING` PKs on child tables
  - All foreign keys use `ondelete="CASCADE"` + `cascade="all, delete-orphan"`
  - `lazy="selectin"` on all relationships to avoid N+1 under async
  - `Budget` value object inlined as columns on `trips`; `Airport` flattened on `flights`
  - `amenities` stored as `JSONB` on accommodations
- **Alembic migrations** — `migrations/versions/0001_initial_schema.py` creates all
  tables in dependency order. `main.py` lifespan runs `alembic upgrade head` on startup.

### Repository + Mapper (Phase 4)
- **`PostgresTripRepository`** — implements `ITripRepository` with `AsyncSession`;
  does not commit (session dependency owns the transaction).
- **`TripOrmMapper`** — bidirectional mapper between the `Trip` aggregate and ORM models.
  Uses `Orm`-suffix aliases (`TripOrm`, `TravelerOrm`, …) to avoid name collision with
  identically-named domain entities. Accesses primary keys via the `id_` attribute
  convention (trailing underscore avoids shadowing Python's built-in `id`).
- **Unit tests** — `tests/unit/trips/infrastructure/test_postgres_trip_repository.py`
  covers all CRUD methods with a mocked `AsyncSession` (no database required).

### DI wiring (Phase 5)
- **`dependencies.py`** — `get_trip_repository` now injects `AsyncSession` via
  `Depends(get_db_session)` and returns `PostgresTripRepository(session)`.
  Removed `@lru_cache()` and `InMemoryTripRepository`.
  All downstream use-case factories are unchanged.

## Architecture decisions

**ORM model naming** — Model files keep plain names (`trip.py`, class `Trip`) rather
than a `_model` / `Model` suffix, as the package path already communicates that these
are persistence models. Collisions with domain entities are resolved with import aliases
(`Trip as TripOrm`). Primary keys use `id_` (trailing underscore per PEP 8 convention
for avoiding builtin shadowing) mapped to the `"id"` SQL column.

**Owner scoping** — All repository queries filter by `owner_id`. Non-owned trips return
`None` / `EntityNotFound` to prevent information leakage about trip existence.

**Transaction boundary** — The repository never commits; the `get_db_session` dependency
owns commit/rollback, keeping the repository reusable in multi-step unit-of-work flows.

## Testing

```bash
# Unit tests (no DB required)
cd vacation_stay_scrapper && pytest tests/unit/ -v

# Integration smoke test
docker compose --profile app up -d
curl -X POST http://localhost:8000/api/trips ...   # create a trip
docker compose restart vacation-planner
curl http://localhost:8000/api/trips               # data must still be there
```

All 49 unit tests pass.

## Pre-merge checklist

- [x] Postgres service healthy in Docker Compose (`app` profile)
- [x] `alembic upgrade head` runs automatically on container start
- [x] `PostgresTripRepository` complete and unit-tested
- [x] All existing unit tests pass (49/49)
- [ ] Integration smoke test: POST → restart → GET persists data
