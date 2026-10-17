"""
Unit tests for AddFlightUseCase.

Mock repository + real Trip aggregate, mirroring the UpdateFlightUseCase
tests, so the aggregate's budget recalculation is genuinely exercised.
"""
import asyncio
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from src.shared.domain.exceptions import EntityNotFound
from src.trips.application.use_cases.add_flight import AddFlightUseCase
from src.trips.domain.entities.trip import Trip
from src.trips.domain.entities.flight import Flight
from src.trips.domain.value_objects.trip_status import TripStatus
from src.trips.domain.value_objects.airport import Airport
from src.trips.domain.value_objects.budget import Budget
from src.trips.domain.value_objects.money import Money


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


def make_flight(flight_id: str = "f1", airline: str = "Iberia", status: str = "pending") -> Flight:
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
        status=status,
    )


def make_repo(**method_returns) -> AsyncMock:
    repo = AsyncMock()
    for method, return_value in method_returns.items():
        getattr(repo, method).return_value = return_value
    return repo


class TestAddFlightUseCase:

    def test_appends_flight_and_saves_trip(self):
        trip = make_trip()
        repo = make_repo(find_by_owner=trip, save=trip)

        result = asyncio.run(
            AddFlightUseCase(repo).execute("1", make_flight("new"), "user-1")
        )

        assert [f.id for f in result.flights] == ["new"]
        repo.save.assert_called_once_with(trip)

    def test_scopes_lookup_to_owner(self):
        trip = make_trip()
        repo = make_repo(find_by_owner=trip, save=trip)

        asyncio.run(
            AddFlightUseCase(repo).execute("1", make_flight("new"), "user-1")
        )

        repo.find_by_owner.assert_called_once_with(1, "user-1")

    def test_leaves_existing_flights_untouched(self):
        trip = make_trip()
        trip.add_flight(make_flight("f1", airline="Iberia"))
        repo = make_repo(find_by_owner=trip, save=trip)

        result = asyncio.run(
            AddFlightUseCase(repo).execute("1", make_flight("f2", airline="Vueling"), "user-1")
        )

        assert result.flights[0].id == "f1"
        assert result.flights[0].airline == "Iberia"
        assert result.flights[1].id == "f2"

    def test_recalculates_budget_for_committed_flight(self):
        trip = make_trip(
            budget=Budget(total=Money(Decimal("1000"), "USD"), spent=Money(Decimal("0"), "USD"))
        )
        repo = make_repo(find_by_owner=trip, save=trip)

        result = asyncio.run(
            AddFlightUseCase(repo).execute("1", make_flight("new", status="confirmed"), "user-1")
        )

        assert result.budget.spent.amount == Decimal("150.0")

    def test_raises_entity_not_found_when_trip_missing_or_not_owned(self):
        repo = make_repo(find_by_owner=None)

        with pytest.raises(EntityNotFound):
            asyncio.run(
                AddFlightUseCase(repo).execute("999", make_flight("new"), "user-1")
            )
        repo.save.assert_not_called()
