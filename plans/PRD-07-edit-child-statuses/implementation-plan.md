# Implementation Plan — PRD-07: Edit Trip Child Statuses

**PRD:** `plans/PRD-07-edit-child-statuses.md`
**Author (this doc):** Senior Software Architect agent
**Phase:** 1 — Architecture (no production code)
**Date:** 2026-07-03
**Target service:** `vacation_stay_scrapper` (+ `fe-client`)

---

## 0. Decisions Resolved at Implementation Time

The Phase-1 open questions in §7/§8 were resolved by the product owner before Phase 2:

1. **Base branch → `main`** (per §6 recommendation). `feature/PRD-07-edit-child-statuses` was cut from `main`.
2. **Non-owner → 404, not 403** (Option **B** in §7). Use cases keep `find_by_owner`; a trip
   that is missing *or* not owned by the caller raises `EntityNotFound → 404`, preserving the
   existing anti-enumeration convention. This is a deliberate deviation from the PRD's 403
   acceptance criterion (documented in `test-instructions.md` → Known limitations).
3. **Budget `spent` includes confirmed flights** (ADR-003 as written): `spent` = confirmed
   flights + confirmed accommodations + booked activities.
4. Same-state PATCH is rejected as an invalid transition (strict, per ADR-002).
5. Error body keeps the existing shape (`{"message": ...}` / `{"details": ...}`), not the PRD's
   illustrative `{"detail": ...}`.

---

## 1. Business Goal

Travelers plan a trip long before every booking is finalized. Today the status of each flight,
accommodation, and activity is frozen at the moment it is created and can never change through the
product. PRD-07 lets a trip owner move each child element through its real-world booking lifecycle
(e.g. a flight `pending → confirmed` when the ticket is issued, an accommodation `confirmed → cancelled`
when a hotel drops the reservation), with server-enforced valid transitions and a live-updating budget.
The business value is an accurate, trustworthy itinerary: owners always see what is truly booked versus
pending, and the budget's "spent" figure reflects only money that is actually committed.

---

## 2. Ground-Truth Findings (verified against current `opentelmetry-daf` branch)

These facts shaped the plan. Every claim below was read from the actual code.

| Area | Current state | Implication for PRD-07 |
|---|---|---|
| `Flight` / `Accommodation` / `Activity` (`domain/entities/*.py`) | `@dataclass` with a `status: str` field validated inline in `__post_init__`. Helpers `is_confirmed()` / `is_booked()`. **No** transition logic, **no** `update_status`. | Add transition-aware update path; keep the inline value-set validation as-is (it stays a safety net). |
| `Trip` aggregate (`domain/entities/trip.py`) | Has `add_/remove_/get_confirmed_*` and `get_booked_activities`. **No** `update_flight_status` / `update_accommodation_status` / `update_activity_status`. | Add three aggregate methods (FR-4). |
| `Budget` (`domain/value_objects/budget.py`) | `@dataclass` (mutable) with `total`, `spent`, `categories`, `is_over_budget`, `remaining`, `percentage_spent`. **No** `recalculate_spent`. | Add `recalculate_spent(...)` (FR-6) → returns a new `Budget`. |
| `Money` (`domain/value_objects/money.py`) | `frozen`. Has `__add__` and `from_float`. **No** `__sub__`. `amount < 0` raises. | Summing costs must seed with `Money(Decimal("0"))` (built-in `sum()` starts at int `0` and will fail). Budget math must avoid subtraction of Money. |
| Domain exceptions (`shared/domain/exceptions.py`) | `DomainException`, `EntityNotFound(entity_type, entity_id)`, `ValidationError`, `BusinessRuleViolation`, `ServiceUnavailable`. **No** `ChildNotFound`, **no** `InvalidStatusTransition`. | Add both exceptions. See §7 for the HTTP-mapping decision. |
| Exception → HTTP middleware (`shared/presentation/middleware.py`) | Maps `EntityNotFound → 404`, `ValidationError → 422`, `BusinessRuleViolation → 400`, `DomainException → 500`. Body shape is `{"message": ..., ...}`, **not** `{"detail": ...}`. | New exceptions subclass existing ones to get correct codes for free (see ADR-002). PRD's `{"detail": ...}` body shape does **not** match current middleware — flagged in §8. |
| `routes.py` | CRUD only: `POST/GET/GET{id}/PUT/DELETE`. `owner_id = current_user["sub"]`. **No** status endpoint. | Add 3 PATCH routes (FR-1). |
| `schemas.py` | Per-child `Literal` status types already correct. `TripResponse` already the canonical full-trip response. | Add one request schema `ChildStatusUpdateRequest {status: str}`; reuse `TripResponse`. |
| `dependencies.py` | Factories for the 5 CRUD use cases, all injecting `ITripRepository`. | Add 3 use-case factories + inject the transition validator(s). |
| `ITripRepository` + `PostgresTripRepository` | `save()` already replaces the whole child collection set on update; `find_by_owner(trip_id, owner_id)` scopes by owner. | **No new repository methods needed.** Reuse `find_by_owner` + `save`. Interface unchanged. |
| ORM (`infrastructure/persistence/models/{flight,accommodation,activity}.py`) | Each child model already has a `status` column (`String, default=...`). `TripOrmMapper` round-trips `status`. | **No DB migration, no ORM change** required. |
| PRD-06 "reuse" | **Not present** on `main`, on `opentelmetry-daf`, or on `edit-trip-status`. No `UpdateTripStatusUseCase`, no `domain/services/` transition service, no `InvalidStatusTransition`. | PRD-07 introduces the transition-validation pattern **fresh**. Nothing to import from PRD-06. |
| Frontend | `.tsx`/`.ts` (not `.jsx`) for trip detail. `TripService.ts` = `ITripService` + `SimpleTripService` + `ApiTripService`. Child cards (`flightsOverview.tsx`, `StaysOverview.tsx`, `ActivitiesOverview.tsx`) are **display-only** (receive `trip` prop, no callbacks/state). `TripDetailsView.tsx` owns `trip` state. `StatusColors.ts` maps `pending→yellow`, `booked→blue` (conflicts with FR-10). | Add 3 service methods; thread an update callback from `TripDetailsView` down to cards; add an editable status control; update `StatusColors.ts`. |

---

## 3. Affected Components by Layer (created vs. modified)

### `vacation_stay_scrapper`

#### Domain layer (`src/trips/domain/`)
| File | Action | Detail |
|---|---|---|
| `services/child_status_transition.py` | **create** | `ChildStatusTransitionValidator` base parameterized by a `VALID_TRANSITIONS` map + three concrete validators (`FlightStatusTransitionValidator`, `AccommodationStatusTransitionValidator`, `ActivityStatusTransitionValidator`). See ADR-002. |
| `entities/trip.py` | **modify** | Add `update_flight_status(flight_id, new_status)`, `update_accommodation_status(...)`, `update_activity_status(...)`. Each finds the child (raise `ChildNotFound`), asks the matching validator (raise `InvalidStatusTransition`), sets the child status, then recomputes `self.budget` via `Budget.recalculate_spent(...)`. |
| `value_objects/budget.py` | **modify** | Add `recalculate_spent(flights, accommodations, activities) -> Budget`. See ADR-003. |
| `value_objects/money.py` | **modify (small)** | Add `__sub__` **or** a `zero()` classmethod to make budget summation safe. (Preferred: `Money.zero(currency)`; avoids negative-guard surprises.) |
| `entities/{flight,accommodation,activity}.py` | **not touched** (optional) | Inline `__post_init__` status-value validation stays as a defensive net. No `update_status` on children — status changes flow through the aggregate + validator. |
| `repositories/trip_repository.py` | **not touched** | Interface unchanged. |

#### Application layer (`src/trips/application/use_cases/`)
| File | Action | Detail |
|---|---|---|
| `update_flight_status.py` | **create** | `UpdateFlightStatusUseCase(repository, validator)` → `execute(trip_id, flight_id, new_status, owner_id)`. |
| `update_accommodation_status.py` | **create** | `UpdateAccommodationStatusUseCase`. |
| `update_activity_status.py` | **create** | `UpdateActivityStatusUseCase`. |

Each use case: fetch owner-scoped trip, resolve ownership (§7), call the aggregate method, `save`, return the updated `Trip`.

#### Infrastructure layer (`src/trips/infrastructure/`)
| File | Action | Detail |
|---|---|---|
| `persistence/postgres_trip_repository.py` | **not touched** | `save()` already persists child-status changes. |
| `persistence/models/*`, `persistence/mappers/trip_orm_mapper.py` | **not touched** | `status` columns and mapping already exist. **No migration.** |

#### Presentation layer (`src/trips/presentation/`)
| File | Action | Detail |
|---|---|---|
| `api/routes.py` | **modify** | Add `PATCH /api/trips/{trip_id}/flights/{flight_id}/status`, `.../accommodations/{accommodation_id}/status`, `.../activities/{activity_id}/status`. Each `Depends(get_current_user)` + the matching use case. Returns `TripMapper.to_response(trip)`. |
| `api/schemas.py` | **modify** | Add `ChildStatusUpdateRequest {status: str}`. Reuse `TripResponse`. (Do **not** over-constrain with a single `Literal` — the three child types have different allowed values; validate the value in the domain validator so the 422 message matches FR/PRD.) |
| `api/dependencies.py` | **modify** | Add `get_update_flight_status_use_case`, `get_update_accommodation_status_use_case`, `get_update_activity_status_use_case`, each constructing the use case with `ITripRepository` + the relevant validator. |
| `presentation/mappers/trip_mapper.py` | **not touched** | `to_response` already serializes child statuses and budget. |

#### Shared
| File | Action | Detail |
|---|---|---|
| `shared/domain/exceptions.py` | **modify** | Add `ChildNotFound(EntityNotFound)` and `InvalidStatusTransition(ValidationError)` (subclassing = correct HTTP code via existing middleware — ADR-002). |
| `shared/presentation/middleware.py` | **not touched** (default) | Subclassing avoids new handlers. Only touch if we decide to reshape bodies to `{"detail": ...}` (see §8). |

### `fe-client`
| File | Action | Detail |
|---|---|---|
| `src/services/TripService.ts` | **modify** | Add `updateFlightStatus(tripId, flightId, status)`, `updateAccommodationStatus(...)`, `updateActivityStatus(...)` to `ITripService` **and** both `SimpleTripService` + `ApiTripService` (workflow DoD). API impl calls `PATCH .../{child}/{id}/status`. |
| `src/components/ChildStatusControl.tsx` | **create** | Editable badge → dropdown of valid next states (mirrors backend transition map via `childStatusTransitions.ts`). Optimistic update + revert + toast (FR-8/9). |
| `src/config/childStatusTransitions.ts` | **create** | Static per-type transition map mirroring ADR-002. |
| `src/utils/StatusColors.ts` | **modify** | Align to FR-10: `pending→gray`, `confirmed`/`booked→green`, `cancelled→red` (current maps `pending→yellow`, `booked→blue`). |
| `src/tripDetailsView.tsx` | **modify** | Thread an `onChildStatusChange`/`setTrip` callback into the three overview cards so an optimistic edit updates the shared `trip` state; re-render budget from the PATCH response. |
| `src/components/flightsOverview.tsx` | **modify** | Replace static badge with `ChildStatusControl`; de-emphasize cancelled cards (FR-11). |
| `src/components/StaysOverview.tsx` | **modify** | Same. |
| `src/components/ActivitiesOverview.tsx` | **modify** | Same. |
| `src/components/BudgetOverview.tsx` | **modify (light)** | Continue to read `trip.budget.spent`; the value is now authoritative from the backend recalculation (FR-12). No client-side recompute needed. |
| `src/Models.ts` | **not touched** | Child `status` literal unions already correct. |

---

## 4. Incremental, TDD-First Delivery Plan

Each step is a thin vertical slice that ends green. **Unit tests are written first for logic layers only**
(domain entities, value objects, domain services, use cases) per `workflow.md`; presentation and repository
implementations are exercised via the manual/QA phase, not unit-tested.

### Step 0 — Scaffolding exceptions (domain)
- **Test first:** `test_exceptions.py` — `ChildNotFound` is an `EntityNotFound`; `InvalidStatusTransition` is a `ValidationError`; messages render as specified.
- Add `ChildNotFound`, `InvalidStatusTransition` to `shared/domain/exceptions.py`.

### Step 1 — Flight status, end-to-end (the simplest working slice)
1. **Domain service (test-first):** `test_child_status_transition.py` — `FlightStatusTransitionValidator` allows `pending→confirmed`, `pending→cancelled`, `confirmed→cancelled`, `cancelled→pending`; rejects `confirmed→pending` (the PRD's 422 example) and unknown values. Implement `ChildStatusTransitionValidator` + flight validator in `domain/services/child_status_transition.py`.
2. **Aggregate (test-first):** `test_trip_update_flight_status.py` — `Trip.update_flight_status` changes an existing flight's status on a valid transition; raises `ChildNotFound` for an unknown id; raises `InvalidStatusTransition` for a bad move. Implement the method (delegating to the validator).
3. **Use case (test-first):** `test_update_flight_status.py` with a fake `ITripRepository` — happy path persists via `save`; wrong owner → 403 path (§7); unknown trip → not found; bad transition → propagates `InvalidStatusTransition`. Implement `UpdateFlightStatusUseCase`.
4. **Presentation (no unit test):** add route, `ChildStatusUpdateRequest`, dependency factory. Wire `Depends(get_current_user)`.
5. **Manual check:** `curl` the flight PATCH end-to-end.

### Step 2 — Accommodations
- Repeat Step 1 (2)-(4) for `AccommodationStatusTransitionValidator`, `Trip.update_accommodation_status`, `UpdateAccommodationStatusUseCase`, route + dependency. Same transition table as flights.

### Step 3 — Activities
- Repeat for `ActivityStatusTransitionValidator` (`pending→booked`), `Trip.update_activity_status`, `UpdateActivityStatusUseCase`, route + dependency.

### Step 4 — Budget recalculation (FR-6, ADR-003)
- **Value object (test-first):** `test_budget_recalculate_spent.py` — cancelled children excluded; confirmed/booked included; pending excluded; result is a new `Budget` with `total`/`categories` preserved; `Money` summation seeded correctly. Implement `Budget.recalculate_spent(...)` + `Money.zero(...)`.
- **Aggregate wiring (test-first):** extend the aggregate tests so each `update_*_status` recomputes `self.budget` when a budget is present. Wire the three aggregate methods to call `recalculate_spent`.

### Step 5 — Frontend
- `TripService.ts`: add the three methods to interface + both implementations.
- `childStatusTransitions.ts` + `ChildStatusControl.tsx`.
- Update `StatusColors.ts` to FR-10.
- Wire callback through `tripDetailsView.tsx` into the three cards; optimistic update + revert + toast; de-emphasize cancelled (FR-11); budget re-renders from PATCH response (FR-12).
- `npm run lint` + manual smoke test.

### Step 6 — Full suite
- `cd vacation_stay_scrapper && pytest .` all green; verify Definition of Done (feature/endpoint + frontend checklists).

---

## 5. Architecture Guardrail Verification

- **Domain never imports infrastructure/presentation.** New domain service (`child_status_transition.py`) and Budget/Money changes import only from within `domain/`. Confirmed: no `infrastructure`/`presentation`/`fastapi`/`sqlalchemy` imports.
- **Use cases depend only on `ITripRepository`** (plus a pure-domain validator). No concrete `PostgresTripRepository` import in `application/`. Validators are injected via `dependencies.py`.
- **New Python code under `src/trips/{layer}/`** following the documented layout; nothing placed in `adapter/`.
- **Naming conventions:** `snake_case.py` files; `PascalCase` classes; use cases are `VerbNounUseCase` (`UpdateFlightStatusUseCase`); REST plural nested routes (`PATCH /api/trips/{trip_id}/flights/{flight_id}/status`); exceptions `PascalCase` (`ChildNotFound`, `InvalidStatusTransition`).
- **Auth on every endpoint:** all three routes take `Depends(get_current_user)`; `owner_id` from JWT `sub`.
- **No new cross-service contract** — `auth_service` proxies these paths automatically (first path segment routing); no `routes.yml` change required for a new sub-path under `/api/trips`.

---

## 6. Recommended Base Branch

**Recommendation: create `feature/PRD-07-edit-child-statuses` off `main`.**

Rationale (verified):
- `main` already contains every hard dependency of PRD-07: the full `trips` clean-architecture module, the child entities with `status`, and `PostgresTripRepository`.
- The PRD-06 status-transition pattern is **absent everywhere** — not in `main`, not in `opentelmetry-daf`, and not even in `edit-trip-status` (that branch has only the 5 CRUD use cases and an empty `domain/services/`). So there is nothing to rebase onto or import; PRD-07 builds the transition pattern fresh regardless of base.
- `opentelmetry-daf` is only ~2 commits ahead of `main` (the OpenTelemetry wiring). Basing PRD-07 on it would couple this feature to unmerged observability work with no functional benefit to PRD-07.

**Open question for the human (§8, Q1):** if the team intends `opentelmetry-daf` to merge into `main` imminently and wants PRD-07 to inherit OTel, base off `opentelmetry-daf` instead. Absent that intent, base off `main`.

---

## 7. Ownership / HTTP-status Decision (needs confirmation)

The PRD's acceptance criteria want **403** for a non-owner and **404** for a missing child.
The existing codebase deliberately does the opposite for trips: `UpdateTripUseCase` uses
`repository.find_by_owner(trip_id, owner_id)` and raises `EntityNotFound → 404` for **both**
"missing" and "wrong owner", specifically to avoid leaking trip existence to other users
(documented in that use case's docstring).

**Two options:**
- **(A) Honor PRD literally:** fetch with `find_by_id`, then compare `trip.owner_id` to the JWT `sub`; raise a new `NotTripOwner` (→ 403) when they differ. Matches PRD acceptance criteria but reverses the repo's "don't leak existence" convention.
- **(B) Follow existing convention:** keep `find_by_owner`; wrong owner returns 404. More secure/consistent, but fails the PRD's "non-owner returns 403" criterion.

**Assumption for the plan:** implement **(A)** to satisfy the PRD's explicit 403 acceptance criterion,
with `NotTripOwner(DomainException)` mapped to 403 via a new middleware handler (or subclassing).
Flagged for product/security sign-off — if security prefers non-disclosure, switch to (B) and update the PRD.
`ChildNotFound` (child id not in an owned trip) → 404 in both options.

---

## 8. Risks, Open Questions & Assumptions

**Open questions (need a human answer):**
1. **Base branch** — `main` (recommended) vs `opentelmetry-daf`. See §6.
2. **Owner mismatch → 403 vs 404.** See §7. Assumed 403 (option A).
3. **Response body shape.** PRD shows error bodies as `{"detail": "..."}`, but the current middleware emits `{"message": "...", ...}`. Assumption: keep the existing `{"message": ...}` shape (consistent with the rest of the service) and treat the PRD's `detail` wording as illustrative. If the FE contract truly needs `detail`, add dedicated exception handlers — a middleware change, flagged.
4. **Do flights count toward `budget.spent`?** FR-6 names only accommodations and activities, but flights carry a `price`. Assumption (ADR-003): `spent` = confirmed flights + confirmed accommodations + booked activities. Confirm whether flights should be included.
5. **Idempotent same-state PATCH** (e.g. `pending → pending`). Not in any transition map. Assumption: treat as `InvalidStatusTransition` (strict). Confirm if a no-op 200 is preferred.

**Risks:**
- **Budget/Money arithmetic edge cases.** `Money` has no subtraction and forbids negative amounts; `sum()` seeds at int `0`. `recalculate_spent` must seed with `Money.zero(currency)` and mix currencies safely (all seed data is USD, but guard against mixed-currency children). Mitigated by dedicated value-object tests (Step 4).
- **`save()` replaces whole child collections.** `PostgresTripRepository.save` reassigns `existing.flights = updated.flights` etc. Persisting a single status change rewrites all children for that trip. Functionally correct here, but concurrent edits to the same trip can clobber each other (last-writer-wins). Out of scope for PRD-07; note for future optimistic-locking work.
- **Frontend interactivity requires prop-drilling.** The three card components are currently display-only; making badges editable means threading a callback + optimistic state from `TripDetailsView`. Low risk but touches four components.
- **`StatusColors.ts` change is global.** It is shared with the trip-level badge; changing `pending→gray` also affects the trip header badge. Verify no visual regression on the trip status badge.
- **Budget seeded as empty on create.** `TripMapper.from_create_request` defaults budget to `total=0, spent=0`. After recalculation `spent` may exceed `total=0` → `is_over_budget=True`. Acceptable (it is literally over a zero budget), but the FE budget bar divides by `planned`; guard against divide-by-zero (already partly handled).

**Assumptions (explicit):**
- No new DB migration (status columns already exist).
- `ITripRepository` stays unchanged; reuse `find_by_owner` + `save`.
- Transition tables are exactly as in the PRD state machines.
- Frontend uses the existing `credentials: 'include'` session-cookie flow through `auth_service`.
