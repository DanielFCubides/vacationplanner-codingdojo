"""
Unit tests for Trip.update_budget.

The traveler sets the Budget total and the Budget categories; Spent is
always derived from committed children, never taken from the caller.
"""
from datetime import date, datetime
from decimal import Decimal

import pytest

from src.trips.domain.entities.trip import Trip
from src.trips.domain.entities.flight import Flight
from src.trips.domain.value_objects.airport import Airport
from src.trips.domain.value_objects.budget import Budget, BudgetCategory
from src.trips.domain.value_objects.money import Money
from src.trips.domain.value_objects.trip_status import TripStatus


def make_trip(**overrides) -> Trip:
    defaults = dict(
        id=1,
        owner_id="user-1",
        name="Summer Holiday",
        destination="Barcelona",
        start_date=date(2025, 7, 1),
        end_date=date(2025, 7, 8),
        status=TripStatus.PLANNING,
    )
    defaults.update(overrides)
    return Trip(**defaults)


def make_flight(status: str = "confirmed", price: float = 150.0) -> Flight:
    return Flight(
        id="f1",
        airline="Iberia",
        flight_number="IB3166",
        departure_airport=Airport(code="BCN", city="Barcelona"),
        departure_time=datetime(2025, 7, 1, 10, 0),
        arrival_airport=Airport(code="LHR", city="London"),
        arrival_time=datetime(2025, 7, 1, 12, 30),
        duration="2h 30m",
        price=Money.from_float(price),
        status=status,
    )


def category(name: str, planned: float = 100.0, spent: float = 0.0) -> BudgetCategory:
    return BudgetCategory(
        category=name, planned=Money.from_float(planned), spent=Money.from_float(spent)
    )


class TestTripUpdateBudget:

    def test_sets_total_and_categories_in_order(self):
        trip = make_trip()

        trip.update_budget(
            Money.from_float(2000), [category("Food", 300), category("Transport", 500, 120)]
        )

        assert trip.budget.total.amount == Decimal("2000")
        assert [c.category for c in trip.budget.categories] == ["Food", "Transport"]
        assert trip.budget.categories[1].spent.amount == Decimal("120")

    def test_spent_is_derived_from_confirmed_children(self):
        trip = make_trip(
            budget=Budget(total=Money.from_float(1000), spent=Money.from_float(999))
        )
        trip.add_flight(make_flight(status="confirmed", price=150))

        trip.update_budget(Money.from_float(3000), [])

        assert trip.budget.spent.amount == Decimal("150")

    def test_creates_budget_when_trip_has_none(self):
        trip = make_trip(budget=None)

        trip.update_budget(Money.from_float(500), [])

        assert trip.budget.total.amount == Decimal("500")
        assert trip.budget.spent.amount == Decimal("0")

    def test_total_below_spent_is_allowed(self):
        trip = make_trip()
        trip.add_flight(make_flight(status="confirmed", price=1200))

        trip.update_budget(Money.from_float(1000), [])

        assert trip.budget.is_over_budget

    def test_category_names_are_trimmed(self):
        trip = make_trip()

        trip.update_budget(Money.from_float(100), [category("  Food  ")])

        assert trip.budget.categories[0].category == "Food"

    @pytest.mark.parametrize("names", [["Food", "food"], ["Food", " FOOD "]])
    def test_duplicate_category_names_are_rejected(self, names):
        trip = make_trip(
            budget=Budget(total=Money.from_float(1000), spent=Money.from_float(0))
        )

        with pytest.raises(ValueError):
            trip.update_budget(Money.from_float(100), [category(n) for n in names])

        assert trip.budget.total.amount == Decimal("1000")

    def test_blank_category_name_is_rejected(self):
        trip = make_trip()

        with pytest.raises(ValueError):
            trip.update_budget(Money.from_float(100), [category("   ")])

    def test_planned_above_total_is_allowed(self):
        trip = make_trip()

        trip.update_budget(
            Money.from_float(1000), [category("Food", 800), category("Transport", 500)]
        )

        assert len(trip.budget.categories) == 2
