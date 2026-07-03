# ADR-003: Budget.recalculate_spent Semantics

**Status:** Proposed
**Date:** 2026-07-03
**PRD:** PRD-07 — Edit Trip Child Statuses (FR-6, FR-12, US-2)
**Deciders:** Senior Software Architect, Product Owner
**Related:** ADR-002 (child status transition validator)

---

## Context

PRD-07 FR-6 states: *"when an accommodation or activity is cancelled, its cost should be excluded from
`budget.spent`. When confirmed/booked, it should be included. Implement a `recalculate_spent` method on
`Budget`."* US-2 reinforces this: cancelling a hotel should recalculate the trip total cost.

Current code (verified):
- `Budget` (`domain/value_objects/budget.py`) is a mutable `@dataclass` holding `total: Money`,
  `spent: Money`, and `categories: list[BudgetCategory]`. It has `remaining`, `percentage_spent`,
  `is_over_budget` — but **no** `recalculate_spent`.
- `Money` (`domain/value_objects/money.py`) is `frozen`, forbids negative amounts (`__post_init__`
  raises), and has `__add__` but **no** `__sub__`.
- Each child carries a `Money` cost: `Flight.price`, `Accommodation.total_price`, `Activity.cost`.
- Python's built-in `sum()` seeds with the integer `0`, so `sum([Money(...), ...])` raises
  (`int + Money` unsupported).

Two questions must be answered:

**Q1 — Which children count toward `spent`?** FR-6 names only accommodations and activities, but flights
also carry a price. Options:
- (a) accommodations + activities only (literal FR-6 reading)
- (b) flights + accommodations + activities (everything with a cost)

**Q2 — Which statuses count?** FR-6 says cancelled excluded, confirmed/booked included. It is silent on
`pending`. Options:
- include pending (treat `spent` as "planned commitment")
- exclude pending (treat `spent` as "money actually committed")

---

## Decision

**`spent` = the sum of costs of every child that is in its committed state:**
- confirmed **flights** (`Flight.price`)
- confirmed **accommodations** (`Accommodation.total_price`)
- booked **activities** (`Activity.cost`)

That is: **Q1 → option (b)** (flights included, for internal consistency — a paid ticket is spent money),
and **Q2 → exclude pending** (only confirmed/booked count; `pending` and `cancelled` are excluded).

Signature (pure, returns a new value object; `Budget` is otherwise treated as immutable):

```python
def recalculate_spent(self, flights, accommodations, activities) -> "Budget":
    total_spent = Money.zero(self.total.currency)
    for f in flights:
        if f.is_confirmed():
            total_spent = total_spent + f.price
    for a in accommodations:
        if a.is_confirmed():
            total_spent = total_spent + a.total_price
    for act in activities:
        if act.is_booked():
            total_spent = total_spent + act.cost
    return Budget(total=self.total, spent=total_spent, categories=self.categories)
```

Supporting change: add `Money.zero(currency="USD")` as the summation seed (avoids the `sum()`-starts-at-`int`
problem and `Money`'s negative guard). `total` and `categories` are preserved unchanged; only `spent` is
recomputed.

The `Trip` aggregate's `update_*_status` methods call `self.budget = self.budget.recalculate_spent(
self.flights, self.accommodations, self.activities)` when a budget is present, so `spent` is always
consistent with the current child statuses after any status change.

---

## Consequences

**Positive**
- A single, deterministic definition of `spent` derived from child state — no drift between what the UI
  shows and what was booked.
- Pure function returning a new `Budget`; unit-testable in isolation and consistent with treating value
  objects as immutable.
- FR-12 (frontend budget panel) needs no client-side recomputation: the PATCH response already carries the
  recalculated budget.

**Negative**
- Including flights (Q1-b) goes slightly beyond the literal FR-6 wording; if product intends flights to be
  excluded from `spent`, drop the flight loop. Flagged as an open question (plan §8, Q4).
- `spent` now ignores the per-category `spent` breakdown and the request-supplied `budget.spent` — the
  derived figure overrides any manually provided value. Category-level `spent` reconciliation is **out of
  scope** for PRD-07 and left as future work.
- If a trip was created with `total = 0` (the mapper's default), any committed child makes
  `is_over_budget` true. This is technically correct (over a zero budget) but may surprise users; the FE
  budget bar must guard against divide-by-zero on `planned`.

**Constraints introduced**
- Whenever a child's status changes (ADR-002 path), the aggregate **must** call `recalculate_spent` so the
  invariant "`spent` reflects only committed children" holds.
- `Money` arithmetic in budget code must seed sums with `Money.zero(...)` and must never attempt
  subtraction of `Money` (no `__sub__`; `remaining` already builds a fresh `Money`).

---

## Alternatives Rejected

- **Mutate `budget.spent` in place.** Rejected: although `Budget` is a mutable dataclass, treating it as a
  value object (return-new) keeps semantics predictable and tests simpler.
- **Recalculate lazily in the mapper / presentation layer.** Rejected: `spent` is domain knowledge and must
  be correct for any consumer of the aggregate, not only the HTTP response.
- **Include `pending` in `spent`.** Rejected: contradicts the plain reading of FR-6 ("when confirmed/booked
  it should be included") and would misrepresent committed money.
