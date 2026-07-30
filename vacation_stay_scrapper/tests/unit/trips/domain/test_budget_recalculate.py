"""
Unit tests for Budget.recalculate_spent and Money.zero (PRD-07, FR-6, ADR-003).

`spent` is derived from committed children only:
    confirmed flights + confirmed accommodations + booked activities.
Pending and cancelled children are excluded.
"""
from datetime import date, datetime
from decimal import Decimal

from src.trips.domain.entities.flight import Flight
from src.trips.domain.entities.accommodation import Accommodation
from src.trips.domain.entities.activity import Activity
from src.trips.domain.value_objects.airport import Airport
from src.trips.domain.value_objects.budget import Budget, BudgetCategory
from src.trips.domain.value_objects.money import Money


def make_flight(status: str, price: float) -> Flight:
    return Flight(
        id=f"f-{status}-{price}",
        airline="Iberia",
        flight_number="IB1",
        departure_airport=Airport(code="BCN", city="Barcelona"),
        departure_time=datetime(2025, 7, 1, 10, 0),
        arrival_airport=Airport(code="LHR", city="London"),
        arrival_time=datetime(2025, 7, 1, 12, 30),
        duration="2h",
        price=Money.from_float(price),
        status=status,
    )


def make_accommodation(status: str, total: float) -> Accommodation:
    return Accommodation(
        id=f"a-{status}-{total}",
        name="Hotel",
        type="hotel",
        check_in=date(2025, 7, 1),
        check_out=date(2025, 7, 5),
        price_per_night=Money.from_float(total / 4),
        total_price=Money.from_float(total),
        rating=4.0,
        amenities=[],
        status=status,
    )


def make_activity(status: str, cost: float) -> Activity:
    return Activity(
        id=f"act-{status}-{cost}",
        name="Tour",
        date=date(2025, 7, 2),
        cost=Money.from_float(cost),
        category="sightseeing",
        status=status,
    )


class TestMoneyZero:

    def test_zero_is_a_zero_money(self):
        z = Money.zero()
        assert z.amount == Decimal("0")
        assert z.currency == "USD"

    def test_zero_respects_currency(self):
        z = Money.zero("EUR")
        assert z.amount == Decimal("0")
        assert z.currency == "EUR"


class TestBudgetRecalculateSpent:

    def _budget(self, total: float = 5000.0) -> Budget:
        return Budget(
            total=Money.from_float(total),
            spent=Money.from_float(999.0),  # stale value that must be overwritten
            categories=[
                BudgetCategory(
                    category="flights",
                    planned=Money.from_float(1000.0),
                    spent=Money.from_float(0.0),
                )
            ],
        )

    def test_sums_only_committed_children(self):
        budget = self._budget()
        flights = [make_flight("confirmed", 150.0), make_flight("pending", 200.0)]
        accommodations = [
            make_accommodation("confirmed", 800.0),
            make_accommodation("cancelled", 500.0),
        ]
        activities = [make_activity("booked", 50.0), make_activity("pending", 30.0)]

        result = budget.recalculate_spent(flights, accommodations, activities)

        # 150 (confirmed flight) + 800 (confirmed accom) + 50 (booked activity)
        assert result.spent.amount == Decimal("1000.0")

    def test_excludes_cancelled_and_pending(self):
        budget = self._budget()
        flights = [make_flight("cancelled", 150.0), make_flight("pending", 200.0)]
        accommodations = [make_accommodation("cancelled", 800.0)]
        activities = [make_activity("cancelled", 50.0), make_activity("pending", 30.0)]

        result = budget.recalculate_spent(flights, accommodations, activities)

        assert result.spent.amount == Decimal("0")

    def test_preserves_total_and_categories(self):
        budget = self._budget(total=5000.0)

        result = budget.recalculate_spent([], [], [])

        assert result.total == budget.total
        assert result.categories == budget.categories

    def test_returns_a_new_budget_instance(self):
        budget = self._budget()

        result = budget.recalculate_spent([], [], [])

        assert result is not budget

    def test_seeds_currency_from_total(self):
        budget = Budget(
            total=Money(amount=Decimal("100"), currency="EUR"),
            spent=Money(amount=Decimal("0"), currency="EUR"),
        )

        result = budget.recalculate_spent([], [], [])

        assert result.spent.currency == "EUR"
