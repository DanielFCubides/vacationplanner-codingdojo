"""
Unit tests for AddAccommodationUseCase.

Mock repository + real Trip aggregate, mirroring the AddFlightUseCase
tests, so the aggregate's budget recalculation is genuinely exercised.
"""
import asyncio
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from src.shared.domain.exceptions import EntityNotFound
from src.trips.application.use_cases.add_accommodation import AddAccommodationUseCase
from src.trips.domain.entities.trip import Trip
from src.trips.domain.entities.accommodation import Accommodation
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


def make_accommodation(
    accommodation_id: str = "a1", name: str = "Hotel Arts", status: str = "pending"
) -> Accommodation:
    return Accommodation(
        id=accommodation_id,
        name=name,
        type="hotel",
        check_in=date(2025, 7, 1),
        check_out=date(2025, 7, 4),
        price_per_night=Money.from_float(100.0),
        total_price=Money.from_float(340.0),
        rating=None,
        amenities=[],
        status=status,
    )


def make_repo(**method_returns) -> AsyncMock:
    repo = AsyncMock()
    for method, return_value in method_returns.items():
        getattr(repo, method).return_value = return_value
    return repo


class TestAddAccommodationUseCase:

    def test_appends_accommodation_and_saves_trip(self):
        trip = make_trip()
        repo = make_repo(find_by_owner=trip, save=trip)

        result = asyncio.run(
            AddAccommodationUseCase(repo).execute("1", make_accommodation("new"), "user-1")
        )

        assert [a.id for a in result.accommodations] == ["new"]
        repo.save.assert_called_once_with(trip)

    def test_scopes_lookup_to_owner(self):
        trip = make_trip()
        repo = make_repo(find_by_owner=trip, save=trip)

        asyncio.run(
            AddAccommodationUseCase(repo).execute("1", make_accommodation("new"), "user-1")
        )

        repo.find_by_owner.assert_called_once_with(1, "user-1")

    def test_leaves_existing_accommodations_untouched(self):
        trip = make_trip()
        trip.add_accommodation(make_accommodation("a1", name="Hotel Arts"))
        repo = make_repo(find_by_owner=trip, save=trip)

        result = asyncio.run(
            AddAccommodationUseCase(repo).execute(
                "1", make_accommodation("a2", name="Casa Camper"), "user-1"
            )
        )

        assert result.accommodations[0].id == "a1"
        assert result.accommodations[0].name == "Hotel Arts"
        assert result.accommodations[1].id == "a2"

    def test_recalculates_budget_with_accommodation_total(self):
        trip = make_trip(
            budget=Budget(total=Money(Decimal("1000"), "USD"), spent=Money(Decimal("0"), "USD"))
        )
        repo = make_repo(find_by_owner=trip, save=trip)

        result = asyncio.run(
            AddAccommodationUseCase(repo).execute(
                "1", make_accommodation("new", status="confirmed"), "user-1"
            )
        )

        assert result.budget.spent.amount == Decimal("340.0")

    def test_raises_entity_not_found_when_trip_missing_or_not_owned(self):
        repo = make_repo(find_by_owner=None)

        with pytest.raises(EntityNotFound):
            asyncio.run(
                AddAccommodationUseCase(repo).execute("999", make_accommodation("new"), "user-1")
            )
        repo.save.assert_not_called()


class TestAccommodationRating:

    def test_rating_is_optional(self):
        assert make_accommodation().rating is None

    def test_rating_out_of_range_is_rejected(self):
        with pytest.raises(ValueError):
            Accommodation(
                id="a1", name="Hotel Arts", type="hotel",
                check_in=date(2025, 7, 1), check_out=date(2025, 7, 4),
                price_per_night=Money.from_float(100.0),
                total_price=Money.from_float(300.0),
                rating=6, amenities=[],
            )
