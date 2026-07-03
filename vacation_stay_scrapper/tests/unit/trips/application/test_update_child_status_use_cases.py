"""
Unit tests for the child-status update use cases (PRD-07, FR-2).

Each use case is tested with a mock repository. The trip returned by the
repository is a real Trip aggregate so that the domain rules (transition
validation, child existence) are genuinely exercised.

Ownership decision (see plan §7): a trip that does not exist OR is not owned
by the caller both surface as EntityNotFound (404), consistent with the other
trip use cases (find_by_owner). The PRD's 403-for-non-owner is intentionally
not implemented to preserve the anti-enumeration convention.
"""
import asyncio
from datetime import date, datetime
from unittest.mock import AsyncMock

import pytest

from src.shared.domain.exceptions import (
    EntityNotFound,
    ChildNotFound,
    InvalidStatusTransition,
)
from src.trips.application.use_cases.update_flight_status import UpdateFlightStatusUseCase
from src.trips.application.use_cases.update_accommodation_status import (
    UpdateAccommodationStatusUseCase,
)
from src.trips.application.use_cases.update_activity_status import (
    UpdateActivityStatusUseCase,
)
from src.trips.domain.entities.trip import Trip
from src.trips.domain.entities.flight import Flight
from src.trips.domain.entities.accommodation import Accommodation
from src.trips.domain.entities.activity import Activity
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


def make_repo(**method_returns) -> AsyncMock:
    repo = AsyncMock()
    for method, return_value in method_returns.items():
        getattr(repo, method).return_value = return_value
    return repo


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


def trip_with_flight(status: str = "pending") -> Trip:
    trip = make_trip()
    trip.add_flight(make_flight(status=status))
    return trip


def make_activity(activity_id: str = "act1", status: str = "pending") -> Activity:
    return Activity(
        id=activity_id,
        name="Sagrada Familia Tour",
        date=date(2025, 7, 2),
        cost=Money.from_float(50.0),
        category="sightseeing",
        status=status,
    )


def trip_with_accommodation(status: str = "pending") -> Trip:
    trip = make_trip()
    trip.add_accommodation(make_accommodation(status=status))
    return trip


def trip_with_activity(status: str = "pending") -> Trip:
    trip = make_trip()
    trip.add_activity(make_activity(status=status))
    return trip


# ---------------------------------------------------------------------------
# UpdateFlightStatusUseCase
# ---------------------------------------------------------------------------

class TestUpdateFlightStatusUseCase:

    def test_updates_status_and_persists(self):
        trip = trip_with_flight("pending")
        repo = make_repo(find_by_owner=trip, save=trip)

        result = asyncio.run(
            UpdateFlightStatusUseCase(repo).execute("1", "f1", "confirmed", "user-1")
        )

        assert result.flights[0].status == "confirmed"
        repo.save.assert_called_once_with(trip)

    def test_scopes_lookup_to_owner(self):
        trip = trip_with_flight("pending")
        repo = make_repo(find_by_owner=trip, save=trip)

        asyncio.run(
            UpdateFlightStatusUseCase(repo).execute("1", "f1", "confirmed", "user-1")
        )

        repo.find_by_owner.assert_called_once_with(1, "user-1")

    def test_raises_entity_not_found_when_trip_missing_or_not_owned(self):
        repo = make_repo(find_by_owner=None)

        with pytest.raises(EntityNotFound):
            asyncio.run(
                UpdateFlightStatusUseCase(repo).execute("999", "f1", "confirmed", "user-1")
            )
        repo.save.assert_not_called()

    def test_raises_child_not_found_for_unknown_flight(self):
        trip = trip_with_flight("pending")
        repo = make_repo(find_by_owner=trip, save=trip)

        with pytest.raises(ChildNotFound):
            asyncio.run(
                UpdateFlightStatusUseCase(repo).execute("1", "nope", "confirmed", "user-1")
            )
        repo.save.assert_not_called()

    def test_raises_invalid_transition_and_does_not_persist(self):
        trip = trip_with_flight("confirmed")
        repo = make_repo(find_by_owner=trip, save=trip)

        with pytest.raises(InvalidStatusTransition):
            asyncio.run(
                UpdateFlightStatusUseCase(repo).execute("1", "f1", "pending", "user-1")
            )
        repo.save.assert_not_called()


class TestUpdateAccommodationStatusUseCase:

    def test_updates_status_and_persists(self):
        trip = trip_with_accommodation("pending")
        repo = make_repo(find_by_owner=trip, save=trip)

        result = asyncio.run(
            UpdateAccommodationStatusUseCase(repo).execute("1", "a1", "confirmed", "user-1")
        )

        assert result.accommodations[0].status == "confirmed"
        repo.save.assert_called_once_with(trip)

    def test_raises_entity_not_found_when_trip_missing_or_not_owned(self):
        repo = make_repo(find_by_owner=None)

        with pytest.raises(EntityNotFound):
            asyncio.run(
                UpdateAccommodationStatusUseCase(repo).execute("999", "a1", "confirmed", "user-1")
            )
        repo.save.assert_not_called()

    def test_raises_child_not_found_for_unknown_accommodation(self):
        trip = trip_with_accommodation("pending")
        repo = make_repo(find_by_owner=trip, save=trip)

        with pytest.raises(ChildNotFound):
            asyncio.run(
                UpdateAccommodationStatusUseCase(repo).execute("1", "nope", "confirmed", "user-1")
            )
        repo.save.assert_not_called()

    def test_raises_invalid_transition_and_does_not_persist(self):
        trip = trip_with_accommodation("confirmed")
        repo = make_repo(find_by_owner=trip, save=trip)

        with pytest.raises(InvalidStatusTransition):
            asyncio.run(
                UpdateAccommodationStatusUseCase(repo).execute("1", "a1", "pending", "user-1")
            )
        repo.save.assert_not_called()


class TestUpdateActivityStatusUseCase:

    def test_updates_status_and_persists(self):
        trip = trip_with_activity("pending")
        repo = make_repo(find_by_owner=trip, save=trip)

        result = asyncio.run(
            UpdateActivityStatusUseCase(repo).execute("1", "act1", "booked", "user-1")
        )

        assert result.activities[0].status == "booked"
        repo.save.assert_called_once_with(trip)

    def test_raises_entity_not_found_when_trip_missing_or_not_owned(self):
        repo = make_repo(find_by_owner=None)

        with pytest.raises(EntityNotFound):
            asyncio.run(
                UpdateActivityStatusUseCase(repo).execute("999", "act1", "booked", "user-1")
            )
        repo.save.assert_not_called()

    def test_raises_child_not_found_for_unknown_activity(self):
        trip = trip_with_activity("pending")
        repo = make_repo(find_by_owner=trip, save=trip)

        with pytest.raises(ChildNotFound):
            asyncio.run(
                UpdateActivityStatusUseCase(repo).execute("1", "nope", "booked", "user-1")
            )
        repo.save.assert_not_called()

    def test_raises_invalid_transition_and_does_not_persist(self):
        trip = trip_with_activity("booked")
        repo = make_repo(find_by_owner=trip, save=trip)

        with pytest.raises(InvalidStatusTransition):
            asyncio.run(
                UpdateActivityStatusUseCase(repo).execute("1", "act1", "pending", "user-1")
            )
        repo.save.assert_not_called()
