# ADR-002: Shared ChildStatusTransitionValidator Parameterized per Child Type

**Status:** Proposed
**Date:** 2026-07-03
**PRD:** PRD-07 — Edit Trip Child Statuses
**Deciders:** Senior Software Architect, Product Owner
**Related:** ADR-001 (Trip status state machine as a domain service)

---

## Context

PRD-07 (FR-3) requires server-side validation of status transitions for three child types:

- **Flight:** `pending → {confirmed, cancelled}`, `confirmed → {cancelled}`, `cancelled → {pending}`
- **Accommodation:** identical to Flight
- **Activity:** `pending → {booked, cancelled}`, `booked → {cancelled}`, `cancelled → {pending}`

The three state machines are structurally identical and differ only in the "active" state label
(`confirmed` vs `booked`) and the set of legal values. The PRD explicitly suggests "a shared
`ChildStatusTransitionValidator` base class parameterized by the type's valid transitions to avoid
code duplication."

**Important:** ADR-001 anticipated reusing `TripStatusTransitionService` for child transitions, but that
PRD-06 service does **not exist** on any relevant branch (`main`, `opentelmetry-daf`, `edit-trip-status`);
`src/trips/domain/services/` contains only `__init__.py`. PRD-07 therefore introduces the child
transition pattern **fresh**. It follows the *shape* established by ADR-001 (transition logic as a
domain service) without importing anything from it.

The current child entities (`Flight`, `Accommodation`, `Activity`) are `@dataclass`es that validate the
*value set* of `status` inline in `__post_init__`, but hold **no** knowledge of legal *transitions*.

Three placement options were considered:
1. Inline transition maps inside each child entity's `update_status` method.
2. Three independent standalone validator classes (no shared base).
3. A single parameterized base `ChildStatusTransitionValidator` + three thin subclasses, living in
   `domain/services/`.

---

## Decision

**Adopt option 3:** a shared, parameterized domain service in
`src/trips/domain/services/child_status_transition.py`.

```
class ChildStatusTransitionValidator:
    VALID_TRANSITIONS: dict[str, set[str]] = {}      # overridden per subclass
    ENTITY_LABEL: str = "child"                       # for the error message

    def validate(self, current: str, new_status: str) -> None:
        allowed = self.VALID_TRANSITIONS.get(current, set())
        if new_status not in allowed:
            raise InvalidStatusTransition(
                f"Invalid transition: cannot move from '{current}' to '{new_status}'"
            )

class FlightStatusTransitionValidator(ChildStatusTransitionValidator): ...
class AccommodationStatusTransitionValidator(ChildStatusTransitionValidator): ...
class ActivityStatusTransitionValidator(ChildStatusTransitionValidator): ...
```

- Transition rules are **domain knowledge**, so they live in the domain layer — consistent with ADR-001.
- Validators are **stateless and pure** (no repository, no I/O), so they are trivially unit-testable and
  carry zero infrastructure imports.
- The `Trip` aggregate's `update_*_status` methods call the matching validator, then mutate the child's
  `status`. Use cases inject the concrete validator via `dependencies.py`.
- Two new exceptions are added to `shared/domain/exceptions.py`:
  - `InvalidStatusTransition(ValidationError)` — inherits the existing **422** middleware mapping.
  - `ChildNotFound(EntityNotFound)` — inherits the existing **404** middleware mapping.
  Subclassing existing exceptions means **no new middleware handler is required** to get the correct
  HTTP codes.

Same-state transitions (e.g. `pending → pending`) are **not** in any map and are therefore rejected as
`InvalidStatusTransition` (strict). This is an assumption open to product review (see PRD-07 plan §8, Q5).

---

## Consequences

**Positive**
- One authoritative place for child-transition rules; adding a state or a child type is a small,
  localized change (a new subclass + a `VALID_TRANSITIONS` map).
- Pure functions → fast, isolated unit tests without constructing a full `Trip` or touching the DB.
- Clean Architecture preserved: domain service imports only domain exceptions.
- The frontend `childStatusTransitions.ts` map mirrors these tables one-to-one, keeping client and server
  in lockstep.

**Negative**
- Three subclasses for near-identical maps may feel heavyweight; the alternative (one class instantiated
  with different maps) trades explicit types for fewer classes.
- The transition table now exists in two languages (Python + TS) and must be kept in sync by discipline
  (no shared source of truth across the service boundary).

**Constraints introduced**
- Child status changes **must** flow through `Trip.update_*_status` (which calls a validator) — never by
  direct ORM mutation or by the general `UpdateTripUseCase`.
- Any future auto-transition (e.g. a background job) must also call the relevant validator before persisting.

---

## Alternatives Rejected

- **Inline per-entity `update_status`:** bloats each `@dataclass` with a transition map and duplicates the
  `InvalidStatusTransition` raising logic three times; harder to keep consistent.
- **Three unrelated validators (no base):** duplicates the `validate()` body three times; a change to the
  validation/error contract must be repeated. The shared base removes that duplication with negligible cost.
