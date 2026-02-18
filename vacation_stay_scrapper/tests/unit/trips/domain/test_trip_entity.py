"""
Unit tests for the Trip aggregate root.

Trip is the central entity of this service. These tests verify its
creation rules, domain logic, and internal consistency — with no
database or HTTP calls involved.
"""
import pytest
from datetime import date, datetime

from src.trips.domain.entities.trip import Trip
from src.trips.domain.entities.traveler import Traveler
from src.trips.domain.entities.flight import Flight
from src.trips.domain.value_objects.trip_id import TripId
from src.trips.domain.value_objects.trip_status import TripStatus
from src.trips.domain.value_objects.airport import Airport
from src.trips.domain.value_objects.money import Money


# ---------------------------------------------------------------------------
# Helpers / shared fixtures
# ---------------------------------------------------------------------------

def make_trip(**overrides) -> Trip:
    """Return a minimal valid Trip, allowing field overrides."""
    defaults = dict(
        id=TripId.generate(),
        name="Summer Holiday",
        destination="Barcelona",
        start_date=date(2025, 7, 1),
        end_date=date(2025, 7, 8),
        status=TripStatus.PLANNING,
    )
    defaults.update(overrides)
    return Trip(**defaults)


def make_traveler(role: str = "viewer") -> Traveler:
    return Traveler(id="t1", name="Alice", email="alice@example.com", role=role)


def make_flight(status: str = "pending") -> Flight:
    departure = Airport(code="BCN", city="Barcelona")
    arrival = Airport(code="LHR", city="London")
    return Flight(
        id="f1",
        airline="Iberia",
        flight_number="IB3166",
        departure_airport=departure,
        departure_time=datetime(2025, 7, 1, 10, 0),
        arrival_airport=arrival,
        arrival_time=datetime(2025, 7, 1, 12, 30),
        duration="2h 30m",
        price=Money.from_float(150.0),
        status=status,
    )


# ---------------------------------------------------------------------------
# Creation rules
# ---------------------------------------------------------------------------

class TestTripCreation:

    def test_creates_a_valid_trip(self):
        trip = make_trip()
        assert trip.name == "Summer Holiday"
        assert trip.destination == "Barcelona"
        assert trip.status == TripStatus.PLANNING

    def test_raises_when_name_is_empty(self):
        with pytest.raises(ValueError, match="name"):
            make_trip(name="")

    def test_raises_when_name_is_blank(self):
        with pytest.raises(ValueError, match="name"):
            make_trip(name="   ")

    def test_raises_when_destination_is_empty(self):
        with pytest.raises(ValueError, match="[Dd]estination"):
            make_trip(destination="")

    def test_raises_when_end_date_is_before_start_date(self):
        with pytest.raises(ValueError, match="[Ee]nd date"):
            make_trip(start_date=date(2025, 7, 8), end_date=date(2025, 7, 1))


# ---------------------------------------------------------------------------
# Duration
# ---------------------------------------------------------------------------

class TestTripDuration:

    def test_duration_is_inclusive_of_both_days(self):
        trip = make_trip(start_date=date(2025, 7, 1), end_date=date(2025, 7, 8))
        assert trip.duration_days == 8

    def test_single_day_trip_has_duration_one(self):
        trip = make_trip(start_date=date(2025, 7, 1), end_date=date(2025, 7, 1))
        assert trip.duration_days == 1


# ---------------------------------------------------------------------------
# Traveler management
# ---------------------------------------------------------------------------

class TestTripTravelers:

    def test_add_traveler(self):
        trip = make_trip()
        traveler = make_traveler()
        trip.add_traveler(traveler)
        assert traveler in trip.travelers

    def test_cannot_add_same_traveler_twice(self):
        trip = make_trip()
        traveler = make_traveler()
        trip.add_traveler(traveler)
        with pytest.raises(ValueError):
            trip.add_traveler(traveler)

    def test_remove_traveler(self):
        trip = make_trip()
        traveler = make_traveler()
        trip.add_traveler(traveler)
        trip.remove_traveler(traveler.id)
        assert traveler not in trip.travelers

    def test_get_owner_returns_the_owner_traveler(self):
        trip = make_trip()
        owner = Traveler(id="o1", name="Bob", email="bob@example.com", role="owner")
        trip.add_traveler(owner)
        trip.add_traveler(make_traveler(role="viewer"))
        assert trip.get_owner() == owner

    def test_get_owner_returns_none_when_no_owner(self):
        trip = make_trip()
        trip.add_traveler(make_traveler(role="viewer"))
        assert trip.get_owner() is None


# ---------------------------------------------------------------------------
# Flight management
# ---------------------------------------------------------------------------

class TestTripFlights:

    def test_add_flight(self):
        trip = make_trip()
        flight = make_flight()
        trip.add_flight(flight)
        assert flight in trip.flights

    def test_remove_flight(self):
        trip = make_trip()
        flight = make_flight()
        trip.add_flight(flight)
        trip.remove_flight(flight.id)
        assert flight not in trip.flights

    def test_only_confirmed_flights_are_returned(self):
        trip = make_trip()
        confirmed = make_flight(status="confirmed")
        pending = make_flight(status="pending")
        pending.id = "f2"
        trip.add_flight(confirmed)
        trip.add_flight(pending)
        assert confirmed in trip.get_confirmed_flights()
        assert pending not in trip.get_confirmed_flights()


# ---------------------------------------------------------------------------
# Status checks
# ---------------------------------------------------------------------------

class TestTripStatus:

    def test_is_planning_when_status_is_planning(self):
        trip = make_trip(status=TripStatus.PLANNING)
        assert trip.is_planning() is True
        assert trip.is_confirmed() is False

    def test_is_confirmed_when_status_is_confirmed(self):
        trip = make_trip(status=TripStatus.CONFIRMED)
        assert trip.is_confirmed() is True
        assert trip.is_planning() is False

    def test_is_completed_when_status_is_completed(self):
        trip = make_trip(status=TripStatus.COMPLETED)
        assert trip.is_completed() is True


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

class TestTripSummary:

    def test_summary_reflects_current_state(self):
        trip = make_trip()
        trip.add_traveler(make_traveler())
        trip.add_flight(make_flight())

        summary = trip.summary
        assert summary["name"] == trip.name
        assert summary["destination"] == trip.destination
        assert summary["travelers"] == 1
        assert summary["flights"] == 1
        assert summary["status"] == TripStatus.PLANNING.value
