"""
Unit tests for UpdateFlightUseCase.

Mirrors the child-status use case tests: mock repository + real Trip
aggregate so domain rules (child existence, budget recalculation) are
genuinely exercised. The merged Flight is produced by the presentation
mapper's apply_flight_update; here we simulate its output by building a
new Flight carrying the same id.
"""
import asyncio
from datetime import date, datetime
from unittest.mock import AsyncMock

import pytest

from src.shared.domain.exceptions import EntityNotFound, ChildNotFound
from src.trips.application.use_cases.update_flight import UpdateFlightUseCase
from src.trips.domain.entities.trip import Trip
from src.trips.domain.entities.flight import Flight
from src.trips.domain.value_objects.trip_status import TripStatus
from src.trips.domain.value_objects.airport import Airport
from src.trips.domain.value_objects.money import Money


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def make_flight(flight_id: str = "f1", airline: str = "Iberia") -> Flight:
    return Flight(
        id=flight_id,
        airline=airline,
        flight_number="IB3166",
        departure_airport=Airport(code="BCN", city="Barcelona"),
        departure_time=datetime(2025, 7, 1, 10, 0),
        arrival_airport=Airport(code="LHR", city="London"),
        arrival_time=datetime(2025, 7, 1, 12, 30),
        duration="2h 30m",
        price=Money.from_float(150.0),
        status="pending",
    )


def make_repo(**method_returns) -> AsyncMock:
    repo = AsyncMock()
    for method, return_value in method_returns.items():
        getattr(repo, method).return_value = return_value
    return repo


def trip_with_flights() -> Trip:
    trip = make_trip()
    trip.add_flight(make_flight(flight_id="f1", airline="Iberia"))
    trip.add_flight(make_flight(flight_id="f2", airline="Vueling"))
    return trip


# ---------------------------------------------------------------------------
# UpdateFlightUseCase
# ---------------------------------------------------------------------------

class TestUpdateFlightUseCase:

    def test_replaces_flight_and_preserves_id(self):
        trip = trip_with_flights()
        repo = make_repo(find_by_owner=trip, save=trip)
        merged = make_flight(flight_id="f1", airline="Ryanair")

        result = asyncio.run(
            UpdateFlightUseCase(repo).execute("1", merged, "user-1")
        )

        assert result.flights[0].id == "f1"
        assert result.flights[0].airline == "Ryanair"
        repo.save.assert_called_once_with(trip)

    def test_scopes_lookup_to_owner(self):
        trip = trip_with_flights()
        repo = make_repo(find_by_owner=trip, save=trip)
        merged = make_flight(flight_id="f1", airline="Ryanair")

        asyncio.run(
            UpdateFlightUseCase(repo).execute("1", merged, "user-1")
        )

        repo.find_by_owner.assert_called_once_with(1, "user-1")

    def test_leaves_other_flights_untouched(self):
        trip = trip_with_flights()
        repo = make_repo(find_by_owner=trip, save=trip)
        merged = make_flight(flight_id="f1", airline="Ryanair")

        result = asyncio.run(
            UpdateFlightUseCase(repo).execute("1", merged, "user-1")
        )

        assert result.flights[1].id == "f2"
        assert result.flights[1].airline == "Vueling"

    def test_raises_entity_not_found_when_trip_missing_or_not_owned(self):
        repo = make_repo(find_by_owner=None)
        merged = make_flight(flight_id="f1", airline="Ryanair")

        with pytest.raises(EntityNotFound):
            asyncio.run(
                UpdateFlightUseCase(repo).execute("999", merged, "user-1")
            )
        repo.save.assert_not_called()

    def test_raises_child_not_found_for_unknown_flight(self):
        trip = trip_with_flights()
        repo = make_repo(find_by_owner=trip, save=trip)
        merged = make_flight(flight_id="nope", airline="Ryanair")

        with pytest.raises(ChildNotFound):
            asyncio.run(
                UpdateFlightUseCase(repo).execute("1", merged, "user-1")
            )
        repo.save.assert_not_called()
