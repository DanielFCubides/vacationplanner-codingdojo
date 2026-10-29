"""
Unit tests for UpdateBudgetUseCase.

Mock repository + real Trip aggregate, mirroring the AddFlightUseCase
tests, so the aggregate's budget rules are genuinely exercised.
"""
import asyncio
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from src.shared.domain.exceptions import EntityNotFound
from src.trips.application.use_cases.update_budget import UpdateBudgetUseCase
from src.trips.domain.entities.trip import Trip
from src.trips.domain.value_objects.budget import BudgetCategory
from src.trips.domain.value_objects.money import Money
from src.trips.domain.value_objects.trip_status import TripStatus


def make_trip() -> Trip:
    return Trip(
        id=1,
        owner_id="user-1",
        name="Summer Holiday",
        destination="Barcelona",
        start_date=date(2025, 7, 1),
        end_date=date(2025, 7, 8),
        status=TripStatus.PLANNING,
    )


def make_repo(**method_returns) -> AsyncMock:
    repo = AsyncMock()
    for method, return_value in method_returns.items():
        getattr(repo, method).return_value = return_value
    return repo


FOOD = BudgetCategory(
    category="Food", planned=Money.from_float(300), spent=Money.from_float(40)
)


class TestUpdateBudgetUseCase:

    def test_updates_budget_and_saves_trip(self):
        trip = make_trip()
        repo = make_repo(find_by_owner=trip, save=trip)

        result = asyncio.run(
            UpdateBudgetUseCase(repo).execute("1", Money.from_float(2000), [FOOD], "user-1")
        )

        assert result.budget.total.amount == Decimal("2000")
        assert [c.category for c in result.budget.categories] == ["Food"]
        repo.save.assert_called_once_with(trip)

    def test_scopes_lookup_to_owner(self):
        trip = make_trip()
        repo = make_repo(find_by_owner=trip, save=trip)

        asyncio.run(
            UpdateBudgetUseCase(repo).execute("1", Money.from_float(100), [], "user-1")
        )

        repo.find_by_owner.assert_called_once_with(1, "user-1")

    def test_raises_entity_not_found_when_trip_missing_or_not_owned(self):
        repo = make_repo(find_by_owner=None)

        with pytest.raises(EntityNotFound):
            asyncio.run(
                UpdateBudgetUseCase(repo).execute("999", Money.from_float(100), [], "user-1")
            )
        repo.save.assert_not_called()

    def test_does_not_save_when_budget_is_invalid(self):
        trip = make_trip()
        repo = make_repo(find_by_owner=trip, save=trip)

        with pytest.raises(ValueError):
            asyncio.run(
                UpdateBudgetUseCase(repo).execute(
                    "1", Money.from_float(100), [FOOD, FOOD], "user-1"
                )
            )
        repo.save.assert_not_called()
