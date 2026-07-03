# Test Instructions — PRD-07: Edit Trip Child Statuses

**Branch:** `feature/PRD-07-edit-child-statuses` (based on `main`)
**Service:** `vacation_stay_scrapper` (backend) + `fe-client` (frontend)
**Reviewer role:** Senior Quality Analyst

---

## 1. What was implemented (business value)

Trip owners can now move each flight, accommodation, and activity through its real-world booking
lifecycle instead of being stuck with the status set at creation. A flight can go
`pending → confirmed` when the ticket is issued, an accommodation `confirmed → cancelled` when a
hotel drops the reservation, an activity `pending → booked` when reserved. The server enforces the
valid transitions per child type, and the trip budget's **spent** figure is recomputed to reflect
only committed items (confirmed flights, confirmed accommodations, booked activities). The trip
detail UI turns each status badge into a small dropdown of valid next states, updates optimistically,
reverts with a toast on failure, and visually de-emphasizes cancelled items.

### Endpoints added (all require authentication)
```
PATCH /api/trips/{trip_id}/flights/{flight_id}/status
PATCH /api/trips/{trip_id}/accommodations/{accommodation_id}/status
PATCH /api/trips/{trip_id}/activities/{activity_id}/status
```
Request body (all): `{ "status": "<new_status>" }`
Success `200`: the full updated trip (same shape as other trip endpoints), with recalculated budget.

### Transition rules (server-enforced)
| Child | Allowed transitions |
|---|---|
| Flight | `pending→confirmed`, `pending→cancelled`, `confirmed→cancelled`, `cancelled→pending` |
| Accommodation | same as Flight |
| Activity | `pending→booked`, `pending→cancelled`, `booked→cancelled`, `cancelled→pending` |

Any move not listed (including same-state, e.g. `pending→pending`) is rejected.

---

## 2. Prerequisites

### Backend
- Python virtualenv at `vacation_stay_scrapper/.venv` (already present) or `pip install -r requirements.txt`.
- For running the API: PostgreSQL + auth (Keycloak) as wired by Docker Compose.

```sh
# Core services (redis, auth-service, vacation-planner, fe-client)
docker compose --profile app up
```

- **Auth:** every endpoint uses `get_current_user` (JWT Bearer validated against Keycloak).
  `owner_id` is taken from the JWT `sub` claim.
  - In the full stack, the browser talks to `auth_service` (BFF), which holds the session in Redis
    and injects `Authorization: Bearer <jwt>` before proxying to `vacation_stay_scrapper`.
  - To hit `vacation_stay_scrapper` (port 8000) directly with `curl`, you need a valid Keycloak
    access token in the `Authorization: Bearer` header.

### Seed data
- Create a trip (via the UI wizard or `POST /api/trips`) that has at least one flight, one
  accommodation, and one activity, and a budget with a non-zero `total`. Note the returned
  `trip.id` and the child `id`s from the response for the calls below.

### Frontend
```sh
cd fe-client
npm install      # if not already
npm run dev      # http://localhost:3001  (or npm run build to verify a production build)
```

---

## 3. Automated tests

```sh
cd vacation_stay_scrapper
.venv/bin/python -m pytest tests/unit -q          # 112 passed — all PRD-07 logic layers

# Targeted PRD-07 suites:
.venv/bin/python -m pytest \
  tests/unit/shared/domain/test_exceptions.py \
  tests/unit/trips/domain/test_child_status_transition.py \
  tests/unit/trips/domain/test_trip_child_status.py \
  tests/unit/trips/domain/test_budget_recalculate.py \
  tests/unit/trips/application/test_update_child_status_use_cases.py -q
```

Frontend production build (type/JSX compile check):
```sh
cd fe-client && npm run build      # ✓ built
```

> Note: `npm run lint` reports 15 pre-existing errors in unrelated auth files
> (`App.jsx`, `Dashboard.jsx`, `authContext.jsx`, `authService.js`, keycloak flows). The PRD-07
> files (`ChildStatusControl.tsx`, the three overviews, `tripDetailsView.tsx`, `TripService.ts`,
> `childStatusTransitions.ts`, `StatusColors.ts`) are lint-clean.

---

## 4. Manual test — API (maps to PRD scenarios)

Set convenience vars (replace with your token/ids):
```sh
BASE=http://localhost:8000        # vacation_stay_scrapper direct; or via auth_service proxy
TOKEN='<keycloak access token>'
TRIP=<trip_id>; FLIGHT=<flight_id>; ACC=<accommodation_id>; ACT=<activity_id>
AUTH="Authorization: Bearer $TOKEN"
CT="Content-Type: application/json"
```

### US-1 — Confirm a flight (happy path, `pending → confirmed`)
```sh
curl -i -X PATCH "$BASE/api/trips/$TRIP/flights/$FLIGHT/status" \
  -H "$AUTH" -H "$CT" -d '{"status":"confirmed"}'
```
**Expected:** `200`, full trip JSON, that flight now `"status":"confirmed"`, and
`budget.spent` increased by the flight's `price`.

### US-3 — Book an activity (`pending → booked`)
```sh
curl -i -X PATCH "$BASE/api/trips/$TRIP/activities/$ACT/status" \
  -H "$AUTH" -H "$CT" -d '{"status":"booked"}'
```
**Expected:** `200`; activity `"status":"booked"`; `budget.spent` includes its `cost`.

### US-2 — Cancel an accommodation and see budget recalculate
```sh
# first confirm it (so it counts), then cancel it
curl -s -X PATCH "$BASE/api/trips/$TRIP/accommodations/$ACC/status" -H "$AUTH" -H "$CT" -d '{"status":"confirmed"}' >/dev/null
curl -i -X PATCH "$BASE/api/trips/$TRIP/accommodations/$ACC/status" \
  -H "$AUTH" -H "$CT" -d '{"status":"cancelled"}'
```
**Expected:** `200`; accommodation `"status":"cancelled"`; its `total_price` is **excluded** from
`budget.spent` (spent drops back).

### Invalid transition → 422 (descriptive message)
```sh
# a confirmed flight cannot go back to pending
curl -s -X PATCH "$BASE/api/trips/$TRIP/flights/$FLIGHT/status" -H "$AUTH" -H "$CT" -d '{"status":"confirmed"}' >/dev/null
curl -i -X PATCH "$BASE/api/trips/$TRIP/flights/$FLIGHT/status" \
  -H "$AUTH" -H "$CT" -d '{"status":"pending"}'
```
**Expected:** `422`, body:
`{"message":"Validation failed","details":"Invalid transition: cannot move from 'confirmed' to 'pending'"}`

### Unknown child → 404
```sh
curl -i -X PATCH "$BASE/api/trips/$TRIP/flights/does-not-exist/status" \
  -H "$AUTH" -H "$CT" -d '{"status":"confirmed"}'
```
**Expected:** `404`, body includes `"message":"Flight not found in this trip"`.

### Missing / not-owned trip → 404  (see Known limitations re: 403)
```sh
curl -i -X PATCH "$BASE/api/trips/999999/flights/$FLIGHT/status" \
  -H "$AUTH" -H "$CT" -d '{"status":"confirmed"}'
```
**Expected:** `404` (trip not found for this owner).

### No auth → 401/403 from the auth layer
```sh
curl -i -X PATCH "$BASE/api/trips/$TRIP/flights/$FLIGHT/status" -H "$CT" -d '{"status":"confirmed"}'
```
**Expected:** rejected by `get_current_user` (no Bearer token).

---

## 5. Manual test — UI (`fe-client`)

1. Log in and open a trip detail page (`/trip/:tripId` via the dashboard).
2. **Flights tab (FR-7/8/9):** click a flight's status badge → a dropdown of valid next states
   appears (e.g. a `pending` flight offers `confirmed` / `cancelled`). Pick one:
   - the badge updates immediately (optimistic),
   - on success it stays and the **Budget** tab reflects the new `spent`,
   - colors follow FR-10: `pending` gray, `confirmed`/`booked` green, `cancelled` red.
3. **Stays / Activities tabs:** same interaction; activities offer `booked` instead of `confirmed`.
4. **Cancelled de-emphasis (FR-11):** set an item to `cancelled` → its card dims (reduced opacity)
   and its cost shows a strikethrough.
5. **Failure path (FR-9):** with the app pointed at the real API, trigger an invalid move (e.g. via
   a stale tab) → the badge reverts and a red toast shows the backend message.
6. **Budget panel (FR-12):** the `spent` value tracks confirmed/booked items only, driven by the
   PATCH response (no client-side recomputation).

---

## 6. Known limitations / out of scope

- **Non-owner returns `404`, not `403`.** The PRD acceptance criteria ask for `403` on a non-owner
  request. By product decision we kept the existing anti-enumeration convention (`find_by_owner` →
  `EntityNotFound` → `404`) so the service does not leak trip existence to other users. This is the
  one intentional deviation from the PRD; flip to `403` only if the "don't leak existence" rule is
  relaxed. (See implementation-plan §0/§7.)
- **Error body shape** is the service's existing `{"message": ..., "details": ...}`, not the PRD's
  illustrative `{"detail": ...}`.
- **Flights count toward `budget.spent`** (confirmed flights included), which goes slightly beyond
  FR-6's literal wording (accommodations + activities); chosen for internal consistency (ADR-003).
- **Same-state PATCH** (e.g. `pending→pending`) is rejected as an invalid transition (strict).
- **`save()` replaces the whole child collection** on persist; concurrent edits to the same trip are
  last-writer-wins. Optimistic locking is out of scope (noted for future work).
- **Budget category-level `spent`** is not reconciled; only the aggregate `budget.spent` is derived.
- **Bulk status updates, payment-triggered auto-confirmation, and child audit history** are explicit
  PRD non-goals and were not implemented.
- No new DB migration was required — `status` columns already exist on all three child ORM models.
