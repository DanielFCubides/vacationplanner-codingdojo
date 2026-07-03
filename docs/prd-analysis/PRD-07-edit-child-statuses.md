# Architecture Analysis — PRD-07: Edit Trip Child Statuses

**PRD:** `plans/PRD-07-edit-child-statuses.md`
**Analyst:** Senior Software Architect agent
**Date:** 2026-07-03
**Service in scope:** `vacation_stay_scrapper` (backend) + `fe-client` (frontend)
**Companion docs:** `plans/PRD-07-edit-child-statuses/implementation-plan.md`, `plans/PRD-07-edit-child-statuses/c4-model.puml`, `docs/diagrams/seq-prd07-update-child-status.puml`, `docs/adr/ADR-002-*`, `docs/adr/ADR-003-*`

---

## 1. Summary

Add three owner-scoped PATCH endpoints to move a flight, accommodation, or activity through its booking
lifecycle, with server-enforced valid transitions and a live budget recalculation. The change is
almost entirely additive in the domain and application layers; infrastructure and persistence require
**no change** because the `status` columns and full-trip `save()` already exist.

---

## 2. Impacted Components per Layer

### 2.1 Domain — `vacation_stay_scrapper/src/trips/domain/`

**Created**
- `services/child_status_transition.py` — `ChildStatusTransitionValidator` (base, parameterized by a
  `VALID_TRANSITIONS: dict[str, set[str]]`) + `FlightStatusTransitionValidator`,
  `AccommodationStatusTransitionValidator`, `ActivityStatusTransitionValidator`. See **ADR-002**.

**Modified**
- `entities/trip.py::Trip` — add `update_flight_status(flight_id, new_status)`,
  `update_accommodation_status(accommodation_id, new_status)`,
  `update_activity_status(activity_id, new_status)`. Each locates the child (else `ChildNotFound`),
  validates the move (else `InvalidStatusTransition`), sets the child's `status`, and — if a budget is
  present — replaces `self.budget` via `Budget.recalculate_spent(...)`.
- `value_objects/budget.py::Budget` — add `recalculate_spent(flights, accommodations, activities) -> Budget`.
  See **ADR-003**.
- `value_objects/money.py::Money` — add `Money.zero(currency="USD")` classmethod (safe summation seed;
  `sum()` starts at int `0` which breaks `Money.__add__`, and `Money` forbids negatives so it has no `__sub__`).

**Must not touch**
- `entities/flight.py`, `entities/accommodation.py`, `entities/activity.py` — keep inline `__post_init__`
  status-value validation as a defensive net; **do not** add `update_status` to children (mutation flows
  through the aggregate).
- `repositories/trip_repository.py::ITripRepository` — interface unchanged.

### 2.2 Application — `.../application/use_cases/`

**Created**
- `update_flight_status.py::UpdateFlightStatusUseCase`
- `update_accommodation_status.py::UpdateAccommodationStatusUseCase`
- `update_activity_status.py::UpdateActivityStatusUseCase`

Each is constructed with `ITripRepository` + the matching validator, exposes
`async execute(trip_id, child_id, new_status, owner_id) -> Trip`, resolves ownership (see §5),
delegates to the aggregate method, calls `repository.save(trip)`, and returns the updated `Trip`.

**Must not touch**
- `update_trip.py`, `create_trip.py`, `get_trip.py`, `delete_trip.py` — status edits are decoupled
  from the full-trip update (PRD goal 4).

### 2.3 Infrastructure — `.../infrastructure/persistence/`

**No change.**
- `postgres_trip_repository.py::PostgresTripRepository.save()` already replaces child collections on update,
  so a changed `status` is persisted.
- `models/{flight,accommodation,activity}.py` already declare a `status` column with a default.
- `mappers/trip_orm_mapper.py` already round-trips `status` in both directions.
- **No Alembic migration required.**

### 2.4 Presentation — `.../presentation/`

**Modified**
- `api/routes.py` — three new PATCH routes (see §3), each `Depends(get_current_user)` + the matching
  use-case dependency; returns `TripMapper.to_response(updated_trip)`.
- `api/schemas.py` — add `ChildStatusUpdateRequest { status: str }`. Reuse `TripResponse` for the 200 body.
  Deliberately **not** a single `Literal` (the three child types have different allowed values; value
  validation happens in the domain validator so the 422 message matches the PRD).
- `api/dependencies.py` — add `get_update_flight_status_use_case`, `get_update_accommodation_status_use_case`,
  `get_update_activity_status_use_case`.

**Must not touch**
- `presentation/mappers/trip_mapper.py::TripMapper.to_response` — already serializes child status + budget.

### 2.5 Shared

**Modified**
- `shared/domain/exceptions.py` — add `ChildNotFound(EntityNotFound)` and
  `InvalidStatusTransition(ValidationError)`. Subclassing reuses the existing middleware mapping
  (404 / 422) with no new handler. See **ADR-002**.

**Conditional**
- `shared/presentation/middleware.py` — only if the owner-mismatch decision needs a bespoke 403 handler,
  or if the error-body shape must change to `{"detail": ...}` (see §4, §5).

### 2.6 Frontend — `fe-client/src/`

**Created**
- `components/ChildStatusControl.tsx` — editable badge → dropdown of valid next states; optimistic update,
  revert-on-error, toast (FR-8/9).
- `config/childStatusTransitions.ts` — per-type transition map mirroring ADR-002.

**Modified**
- `services/TripService.ts` — `updateFlightStatus`, `updateAccommodationStatus`, `updateActivityStatus`
  added to `ITripService` **and** both `SimpleTripService` + `ApiTripService`.
- `utils/StatusColors.ts` — realign to FR-10 (`pending→gray`, `confirmed`/`booked→green`, `cancelled→red`).
- `tripDetailsView.tsx` — thread an update callback into the three cards; re-render budget from the
  PATCH response.
- `components/flightsOverview.tsx`, `components/StaysOverview.tsx`, `components/ActivitiesOverview.tsx` —
  swap static badge for `ChildStatusControl`; de-emphasize cancelled cards (FR-11).
- `components/BudgetOverview.tsx` — light: renders authoritative `trip.budget.spent` from the PATCH
  response (FR-12).

**Must not touch**
- `Models.ts` — child `status` unions already correct.

---

## 3. Contract Changes

### 3.1 New endpoints (all: auth required + owner-scoped)

```
PATCH /api/trips/{trip_id}/flights/{flight_id}/status
PATCH /api/trips/{trip_id}/accommodations/{accommodation_id}/status
PATCH /api/trips/{trip_id}/activities/{activity_id}/status
```

**Request body (all three):**
```json
{ "status": "confirmed" }
```
- flights / accommodations: `confirmed | pending | cancelled`
- activities: `booked | pending | cancelled`

**Responses:**
| Code | When | Body (current middleware shape) |
|---|---|---|
| 200 | valid transition persisted | full `TripResponse` (same shape as other trip endpoints) |
| 404 | child id not found in the owned trip | `{"message": "...", "entity_type": "...", "entity_id": "..."}` |
| 422 | invalid transition (e.g. `confirmed → pending`) | `{"message": "Validation failed", "details": "Invalid transition: cannot move from 'confirmed' to 'pending'"}` |
| 403 | requester is not the trip owner (assumption A, §5) | `{...}` (needs a 403 handler / exception) |

> **Contract mismatch flag:** the PRD specifies error bodies as `{"detail": "..."}`. The existing
> global middleware emits `{"message": ...}` (and `{"details": ...}` for validation). Either accept
> the existing shape (recommended, consistent with the rest of the service) or add dedicated handlers.

### 3.2 New domain exceptions
- `ChildNotFound(EntityNotFound)` → HTTP 404 via existing handler.
- `InvalidStatusTransition(ValidationError)` → HTTP 422 via existing handler.
- (Conditional) `NotTripOwner(DomainException)` → HTTP 403, requires a new handler (only if §5 option A).

### 3.3 Repository / interface changes
- **None.** `ITripRepository` is unchanged; use cases reuse `find_by_owner(trip_id, owner_id)` + `save(trip)`.

### 3.4 Database / ORM changes
- **None.** `status` columns already exist on `flights`, `accommodations`, `activities`. No migration.

### 3.5 Frontend service contract
- `ITripService` gains `updateFlightStatus(tripId, flightId, status)`,
  `updateAccommodationStatus(tripId, accommodationId, status)`,
  `updateActivityStatus(tripId, activityId, status)`; implemented in both service classes.

---

## 4. Gap Analysis (PRD requirement vs current code)

| PRD ref | Requirement | Current state | Gap / action |
|---|---|---|---|
| FR-1 | 3 PATCH status endpoints | none | **Gap** — add routes. |
| FR-2 | 3 use cases | none | **Gap** — create. |
| FR-3 | Per-type transition validators, "mirror PRD-06 pattern" | PRD-06 pattern **absent** on all branches (`main`, `opentelmetry-daf`, `edit-trip-status`); `domain/services/` empty | **Gap** — build the transition pattern **fresh** (ADR-002). Nothing to reuse. |
| FR-4 | `Trip.update_*_status` methods raising `ChildNotFound` / `InvalidStatusTransition` | aggregate has add/remove/get_confirmed only; exceptions don't exist | **Gap** — add methods + exceptions. |
| FR-5 | Persist child status via existing ORM relationship | `save()` already replaces child collections | **Met** — reuse; no infra change. |
| FR-6 | `Budget.recalculate_spent`; cancelled excluded, confirmed/booked included | `Budget` has `spent`/`is_over_budget` but **no** `recalculate_spent`; `Money` has no `__sub__` and `sum()` breaks | **Gap** — add method + `Money.zero`; decide flight inclusion (ADR-003). |
| FR-7/8/9 | Interactive, editable status badges w/ dropdown + optimistic update | cards are display-only, no callback/state | **Gap** — new control + prop-drill callback. |
| FR-10 | pending→gray, confirmed/booked→green, cancelled→red | `StatusColors.ts` maps pending→yellow, booked→blue | **Mismatch** — update util. |
| FR-11 | De-emphasize cancelled | none | **Gap** — card styling. |
| FR-12 | Budget panel recalculates spent from confirmed/booked | `BudgetOverview` renders `trip.budget.spent` verbatim | **Met via backend** — backend returns recalculated budget; FE just re-renders. |
| API 404/422/403 bodies | `{"detail": ...}` | middleware emits `{"message": ...}` | **Contract drift** — see §3.1 flag. |
| AC 403 | non-owner → 403 | trip use cases return 404 for wrong owner (anti-leak convention) | **Convention conflict** — see §5. |

---

## 5. Ownership / HTTP-status Conflict (decision required)

The PRD wants **403** for a non-owner; the codebase intentionally returns **404** for a non-owned trip
(via `find_by_owner`) to avoid disclosing that a trip exists (documented in `UpdateTripUseCase`).

- **Option A (assumed):** `find_by_id` + explicit owner check → raise `NotTripOwner` (403). Satisfies the
  PRD acceptance criterion; needs a 403 handler; reverses the anti-leak convention.
- **Option B:** keep `find_by_owner` → non-owner gets 404. Consistent + secure; fails the PRD's 403 AC.

Recommendation: confirm with product/security. The plan assumes **Option A** to honor the PRD, and flags
the security trade-off. `ChildNotFound` remains 404 in both.

---

## 6. Clean-Architecture Compliance

- New domain service and value-object changes import only from `domain/`. No `fastapi` / `sqlalchemy` /
  infrastructure imports leak into the domain.
- Use cases depend on `ITripRepository` + a pure-domain validator injected in `dependencies.py`; no
  concrete repository import in `application/`.
- New files land under `src/trips/{domain,application,presentation}/` following the documented layout.
- Naming: `UpdateFlightStatusUseCase`, `ChildStatusTransitionValidator`, `ChildNotFound`,
  `InvalidStatusTransition`, REST plural nested routes.

---

## 7. Companion Decisions
- **ADR-002** — shared `ChildStatusTransitionValidator` parameterized per child type.
- **ADR-003** — `Budget.recalculate_spent` semantics (which children count toward `spent`).
