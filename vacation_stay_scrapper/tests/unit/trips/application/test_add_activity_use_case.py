"""
Unit tests for AddActivityUseCase.

Mock repository + real Trip aggregate, mirroring the AddFlightUseCase
tests, so the aggregate's budget recalculation is genuinely exercised.
"""
import asyncio
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from src.shared.domain.exceptions import EntityNotFound
from src.trips.application.use_cases.add_activity import AddActivityUseCase
from src.trips.domain.entities.trip import Trip
from src.trips.domain.entities.activity import Activity
from src.trips.domain.value_objects.trip_status import TripStatus
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


def make_activity(
    activity_id: str = "act1", name: str = "Sagrada Familia tour",
    status: str = "pending", cost: float = 45.0,
) -> Activity:
    return Activity(
        id=activity_id,
        name=name,
        date=date(2025, 7, 2),
        cost=Money.from_float(cost),
        category="Sightseeing",
        status=status,
    )


def make_repo(**method_returns) -> AsyncMock:
    repo = AsyncMock()
    for method, return_value in method_returns.items():
        getattr(repo, method).return_value = return_value
    return repo


class TestAddActivityUseCase:

    def test_appends_activity_and_saves_trip(self):
        trip = make_trip()
        repo = make_repo(find_by_owner=trip, save=trip)

        result = asyncio.run(
            AddActivityUseCase(repo).execute("1", make_activity("new"), "user-1")
        )

        assert [a.id for a in result.activities] == ["new"]
        repo.save.assert_called_once_with(trip)

    def test_scopes_lookup_to_owner(self):
        trip = make_trip()
        repo = make_repo(find_by_owner=trip, save=trip)

        asyncio.run(
            AddActivityUseCase(repo).execute("1", make_activity("new"), "user-1")
        )

        repo.find_by_owner.assert_called_once_with(1, "user-1")

    def test_leaves_existing_activities_untouched(self):
        trip = make_trip()
        trip.add_activity(make_activity("act1", name="Sagrada Familia tour"))
        repo = make_repo(find_by_owner=trip, save=trip)

        result = asyncio.run(
            AddActivityUseCase(repo).execute(
                "1", make_activity("act2", name="Tapas crawl"), "user-1"
            )
        )

        assert result.activities[0].id == "act1"
        assert result.activities[0].name == "Sagrada Familia tour"
        assert result.activities[1].id == "act2"

    def test_recalculates_budget_for_booked_activity(self):
        trip = make_trip(
            budget=Budget(total=Money(Decimal("1000"), "USD"), spent=Money(Decimal("0"), "USD"))
        )
        repo = make_repo(find_by_owner=trip, save=trip)

        result = asyncio.run(
            AddActivityUseCase(repo).execute(
                "1", make_activity("new", status="booked"), "user-1"
            )
        )

        assert result.budget.spent.amount == Decimal("45.0")

    def test_raises_entity_not_found_when_trip_missing_or_not_owned(self):
        repo = make_repo(find_by_owner=None)

        with pytest.raises(EntityNotFound):
            asyncio.run(
                AddActivityUseCase(repo).execute("999", make_activity("new"), "user-1")
            )
        repo.save.assert_not_called()
