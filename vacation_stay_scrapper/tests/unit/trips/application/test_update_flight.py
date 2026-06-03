"""
Unit tests for UpdateFlightUseCase.
"""
import asyncio
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.shared.domain.exceptions import EntityNotFound
from src.trips.application.use_cases.update_flight import UpdateFlightUseCase
from src.trips.domain.entities.flight import Flight
from src.trips.domain.entities.trip import Trip
from src.trips.domain.value_objects.airport import Airport
from src.trips.domain.value_objects.money import Money
from src.trips.domain.value_objects.trip_status import TripStatus


def make_flight(flight_id: str = "flight-1", airline: str = "Delta") -> Flight:
    return Flight(
        id=flight_id,
        airline=airline,
        flight_number="DL100",
        departure_airport=Airport(code="JFK", city="New York"),
        departure_time=datetime(2025, 7, 1, 8, 0, tzinfo=timezone.utc),
        arrival_airport=Airport(code="LAX", city="Los Angeles"),
        arrival_time=datetime(2025, 7, 1, 14, 30, tzinfo=timezone.utc),
        duration="6h 30m",
        price=Money(450, "USD"),
        stops=0,
        cabin_class="Economy",
        status="confirmed",
    )


def make_trip(trip_id: int = 1, owner_id: str = "user-1", flights=None) -> Trip:
    return Trip(
        id=trip_id,
        owner_id=owner_id,
        name="Summer Holiday",
        destination="Barcelona",
        start_date=date(2025, 7, 1),
        end_date=date(2025, 7, 8),
        status=TripStatus.PLANNING,
        flights=flights or [],
    )


def make_repo(**method_returns) -> AsyncMock:
    repo = AsyncMock()
    for method, return_value in method_returns.items():
        getattr(repo, method).return_value = return_value
    return repo


class TestUpdateFlightUseCase:

    def test_updates_flight_and_returns_updated_entity(self):
        flight = make_flight("flight-1", "Delta")
        trip = make_trip(flights=[flight])

        def apply_update(f: Flight) -> Flight:
            f.airline = "United"
            return f

        repo = make_repo(find_by_owner=trip, update_flight=flight)

        result = asyncio.run(
            UpdateFlightUseCase(repo).execute(
                trip_id="1",
                flight_id="flight-1",
                apply_update=apply_update,
                owner_id="user-1",
            )
        )

        assert result.id == "flight-1"
        assert result.airline == "United"

    def test_preserves_flight_id(self):
        flight = make_flight("flight-1", "Delta")
        trip = make_trip(flights=[flight])

        def apply_update(f: Flight) -> Flight:
            f.airline = "United"
            return f

        repo = make_repo(find_by_owner=trip, update_flight=flight)

        result = asyncio.run(
            UpdateFlightUseCase(repo).execute(
                trip_id="1",
                flight_id="flight-1",
                apply_update=apply_update,
                owner_id="user-1",
            )
        )

        assert result.id == "flight-1"

    def test_does_not_touch_other_flights_in_trip(self):
        target = make_flight("flight-1", "Delta")
        other = make_flight("flight-2", "Lufthansa")
        trip = make_trip(flights=[target, other])

        def apply_update(f: Flight) -> Flight:
            f.airline = "United"
            return f

        repo = make_repo(find_by_owner=trip, update_flight=target)

        asyncio.run(
            UpdateFlightUseCase(repo).execute(
                trip_id="1",
                flight_id="flight-1",
                apply_update=apply_update,
                owner_id="user-1",
            )
        )

        # Other flight unchanged in trip
        assert trip.flights[1].airline == "Lufthansa"
        # Repository called once for the targeted flight only
        repo.update_flight.assert_called_once()
        called_flight = repo.update_flight.call_args[0][0]
        assert called_flight.id == "flight-1"

    def test_raises_entity_not_found_when_trip_missing(self):
        repo = make_repo(find_by_owner=None)

        def apply_update(f: Flight) -> Flight:
            return f

        with pytest.raises(EntityNotFound) as exc_info:
            asyncio.run(
                UpdateFlightUseCase(repo).execute(
                    trip_id="999",
                    flight_id="flight-1",
                    apply_update=apply_update,
                    owner_id="user-1",
                )
            )

        assert exc_info.value.entity_type == "Trip"

    def test_raises_entity_not_found_when_trip_not_owned(self):
        repo = make_repo(find_by_owner=None)

        def apply_update(f: Flight) -> Flight:
            return f

        with pytest.raises(EntityNotFound):
            asyncio.run(
                UpdateFlightUseCase(repo).execute(
                    trip_id="1",
                    flight_id="flight-1",
                    apply_update=apply_update,
                    owner_id="another-user",
                )
            )

    def test_raises_entity_not_found_when_flight_missing(self):
        trip = make_trip(flights=[make_flight("flight-1")])
        repo = make_repo(find_by_owner=trip)

        def apply_update(f: Flight) -> Flight:
            return f

        with pytest.raises(EntityNotFound) as exc_info:
            asyncio.run(
                UpdateFlightUseCase(repo).execute(
                    trip_id="1",
                    flight_id="missing-flight",
                    apply_update=apply_update,
                    owner_id="user-1",
                )
            )

        assert exc_info.value.entity_type == "Flight"
        assert exc_info.value.entity_id == "missing-flight"

    def test_does_not_call_update_flight_when_trip_missing(self):
        repo = make_repo(find_by_owner=None)

        def apply_update(f: Flight) -> Flight:
            return f

        with pytest.raises(EntityNotFound):
            asyncio.run(
                UpdateFlightUseCase(repo).execute(
                    trip_id="1",
                    flight_id="flight-1",
                    apply_update=apply_update,
                    owner_id="user-1",
                )
            )

        repo.update_flight.assert_not_called()

    def test_does_not_call_update_flight_when_flight_missing(self):
        trip = make_trip(flights=[make_flight("flight-1")])
        repo = make_repo(find_by_owner=trip)

        def apply_update(f: Flight) -> Flight:
            return f

        with pytest.raises(EntityNotFound):
            asyncio.run(
                UpdateFlightUseCase(repo).execute(
                    trip_id="1",
                    flight_id="missing-flight",
                    apply_update=apply_update,
                    owner_id="user-1",
                )
            )

        repo.update_flight.assert_not_called()

    def test_passes_correct_trip_id_to_repository(self):
        flight = make_flight("flight-1")
        trip = make_trip(flights=[flight])
        repo = make_repo(find_by_owner=trip, update_flight=flight)

        asyncio.run(
            UpdateFlightUseCase(repo).execute(
                trip_id="1",
                flight_id="flight-1",
                apply_update=lambda f: f,
                owner_id="user-1",
            )
        )

        assert repo.find_by_owner.call_args[0][0] == 1
        assert repo.update_flight.call_args[0][1] == 1
