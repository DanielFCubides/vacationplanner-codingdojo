"""
Unit tests for the Trip aggregate's child-status update methods (PRD-07, FR-4).

Status changes flow through the aggregate so that domain invariants
(valid transition + child existence) are enforced in one place.
"""
import pytest
from datetime import date, datetime
from decimal import Decimal

from src.trips.domain.entities.trip import Trip
from src.trips.domain.entities.flight import Flight
from src.trips.domain.entities.accommodation import Accommodation
from src.trips.domain.entities.activity import Activity
from src.trips.domain.value_objects.trip_status import TripStatus
from src.trips.domain.value_objects.airport import Airport
from src.trips.domain.value_objects.money import Money
from src.trips.domain.value_objects.budget import Budget
from src.shared.domain.exceptions import ChildNotFound, InvalidStatusTransition


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


def make_flight(flight_id: str = "f1", status: str = "pending") -> Flight:
    return Flight(
        id=flight_id,
        airline="Iberia",
        flight_number="IB3166",
        departure_airport=Airport(code="BCN", city="Barcelona"),
        departure_time=datetime(2025, 7, 1, 10, 0),
        arrival_airport=Airport(code="LHR", city="London"),
        arrival_time=datetime(2025, 7, 1, 12, 30),
        duration="2h 30m",
        price=Money.from_float(150.0),
        status=status,
    )


def make_accommodation(acc_id: str = "a1", status: str = "pending") -> Accommodation:
    return Accommodation(
        id=acc_id,
        name="Hotel Arts",
        type="hotel",
        check_in=date(2025, 7, 1),
        check_out=date(2025, 7, 5),
        price_per_night=Money.from_float(200.0),
        total_price=Money.from_float(800.0),
        rating=4.5,
        amenities=["wifi"],
        status=status,
    )


def make_activity(activity_id: str = "act1", status: str = "pending") -> Activity:
    return Activity(
        id=activity_id,
        name="Sagrada Familia Tour",
        date=date(2025, 7, 2),
        cost=Money.from_float(50.0),
        category="sightseeing",
        status=status,
    )


class TestTripUpdateFlightStatus:

    def test_updates_flight_status_on_valid_transition(self):
        trip = make_trip()
        trip.add_flight(make_flight(status="pending"))

        trip.update_flight_status("f1", "confirmed")

        assert trip.flights[0].status == "confirmed"

    def test_raises_child_not_found_for_unknown_flight(self):
        trip = make_trip()
        trip.add_flight(make_flight("f1"))

        with pytest.raises(ChildNotFound):
            trip.update_flight_status("does-not-exist", "confirmed")

    def test_raises_invalid_transition_for_illegal_move(self):
        trip = make_trip()
        trip.add_flight(make_flight(status="confirmed"))

        with pytest.raises(InvalidStatusTransition):
            trip.update_flight_status("f1", "pending")

    def test_does_not_change_status_when_transition_is_invalid(self):
        trip = make_trip()
        trip.add_flight(make_flight(status="confirmed"))

        with pytest.raises(InvalidStatusTransition):
            trip.update_flight_status("f1", "pending")

        assert trip.flights[0].status == "confirmed"


class TestTripUpdateAccommodationStatus:

    def test_updates_accommodation_status_on_valid_transition(self):
        trip = make_trip()
        trip.add_accommodation(make_accommodation(status="pending"))

        trip.update_accommodation_status("a1", "confirmed")

        assert trip.accommodations[0].status == "confirmed"

    def test_raises_child_not_found_for_unknown_accommodation(self):
        trip = make_trip()
        trip.add_accommodation(make_accommodation("a1"))

        with pytest.raises(ChildNotFound):
            trip.update_accommodation_status("nope", "confirmed")

    def test_raises_invalid_transition_for_illegal_move(self):
        trip = make_trip()
        trip.add_accommodation(make_accommodation(status="confirmed"))

        with pytest.raises(InvalidStatusTransition):
            trip.update_accommodation_status("a1", "pending")


def make_budget(total: float = 5000.0) -> Budget:
    return Budget(total=Money.from_float(total), spent=Money.from_float(0.0))


class TestChildStatusUpdateRecalculatesBudget:

    def test_confirming_a_flight_adds_its_price_to_spent(self):
        trip = make_trip(budget=make_budget())
        trip.add_flight(make_flight(status="pending"))  # price 150

        trip.update_flight_status("f1", "confirmed")

        assert trip.budget.spent.amount == Decimal("150.0")

    def test_cancelling_an_accommodation_excludes_its_cost(self):
        trip = make_trip(budget=make_budget())
        trip.add_accommodation(make_accommodation(status="confirmed"))  # total 800

        assert trip.budget.spent.amount == Decimal("0.0")  # not yet recalculated
        trip.update_accommodation_status("a1", "cancelled")

        assert trip.budget.spent.amount == Decimal("0")

    def test_booking_an_activity_adds_its_cost_to_spent(self):
        trip = make_trip(budget=make_budget())
        trip.add_activity(make_activity(status="pending"))  # cost 50

        trip.update_activity_status("act1", "booked")

        assert trip.budget.spent.amount == Decimal("50.0")

    def test_no_budget_is_tolerated(self):
        trip = make_trip(budget=None)
        trip.add_flight(make_flight(status="pending"))

        # Should not raise even though there is no budget to recalculate
        trip.update_flight_status("f1", "confirmed")

        assert trip.flights[0].status == "confirmed"
        assert trip.budget is None


class TestTripUpdateActivityStatus:

    def test_updates_activity_status_on_valid_transition(self):
        trip = make_trip()
        trip.add_activity(make_activity(status="pending"))

        trip.update_activity_status("act1", "booked")

        assert trip.activities[0].status == "booked"

    def test_raises_child_not_found_for_unknown_activity(self):
        trip = make_trip()
        trip.add_activity(make_activity("act1"))

        with pytest.raises(ChildNotFound):
            trip.update_activity_status("nope", "booked")

    def test_raises_invalid_transition_for_illegal_move(self):
        trip = make_trip()
        trip.add_activity(make_activity(status="booked"))

        with pytest.raises(InvalidStatusTransition):
            trip.update_activity_status("act1", "pending")
