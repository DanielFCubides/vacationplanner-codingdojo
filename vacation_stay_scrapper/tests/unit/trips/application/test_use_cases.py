"""
Unit tests for trips application use cases.

Each use case is tested in isolation by injecting a mock repository.
No database, no HTTP — just pure business logic.

Pattern used:
    - AsyncMock replaces the repository so async calls resolve instantly.
    - asyncio.run() drives each async use case from a regular pytest test.

References:
    - unittest.mock.AsyncMock: https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock
    - Hexagonal Architecture (Ports & Adapters): https://alistair.cockburn.us/hexagonal-architecture/
"""
import asyncio
from datetime import date
from unittest.mock import AsyncMock

import pytest

from src.shared.domain.exceptions import EntityNotFound
from src.trips.application.use_cases.create_trip import CreateTripUseCase
from src.trips.application.use_cases.delete_trip import DeleteTripUseCase
from src.trips.application.use_cases.get_trip import GetAllTripsUseCase, GetTripUseCase
from src.trips.application.use_cases.update_trip import UpdateTripUseCase
from src.trips.domain.entities.trip import Trip
from src.trips.domain.value_objects.trip_status import TripStatus


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def make_trip(trip_id: int = 1, owner_id: str = "user-1") -> Trip:
    """Return a minimal valid Trip for use in tests."""
    return Trip(
        id=trip_id,
        owner_id=owner_id,
        name="Summer Holiday",
        destination="Barcelona",
        start_date=date(2025, 7, 1),
        end_date=date(2025, 7, 8),
        status=TripStatus.PLANNING,
    )


def make_repo(**method_returns) -> AsyncMock:
    """
    Return a mock repository.

    Pass keyword arguments matching repository method names to control
    what each method returns, e.g. make_repo(save=trip, find_by_id=trip).
    """
    repo = AsyncMock()
    for method, return_value in method_returns.items():
        getattr(repo, method).return_value = return_value
    return repo


# ---------------------------------------------------------------------------
# CreateTripUseCase
# ---------------------------------------------------------------------------

class TestCreateTripUseCase:

    def test_returns_the_saved_trip(self):
        trip = make_trip()
        repo = make_repo(save=trip)

        result = asyncio.run(CreateTripUseCase(repo).execute(trip))

        assert result == trip

    def test_delegates_save_to_the_repository(self):
        trip = make_trip()
        repo = make_repo(save=trip)

        asyncio.run(CreateTripUseCase(repo).execute(trip))

        repo.save.assert_called_once_with(trip)


# ---------------------------------------------------------------------------
# GetTripUseCase
# ---------------------------------------------------------------------------

class TestGetTripUseCase:

    def test_returns_trip_when_found(self):
        trip = make_trip(trip_id=1)
        repo = make_repo(find_by_owner=trip)

        result = asyncio.run(GetTripUseCase(repo).execute("1", "user-1"))

        assert result == trip

    def test_raises_entity_not_found_when_trip_is_missing(self):
        repo = make_repo(find_by_owner=None)

        with pytest.raises(EntityNotFound):
            asyncio.run(GetTripUseCase(repo).execute("999", "user-1"))

    def test_passes_correct_trip_id_to_repository(self):
        trip = make_trip(trip_id=1)
        repo = make_repo(find_by_owner=trip)

        asyncio.run(GetTripUseCase(repo).execute("1", "user-1"))

        called_with = repo.find_by_owner.call_args[0][0]
        assert called_with == 1


# ---------------------------------------------------------------------------
# GetAllTripsUseCase
# ---------------------------------------------------------------------------

class TestGetAllTripsUseCase:

    def test_returns_all_trips_from_repository(self):
        trips = [make_trip(), make_trip()]
        repo = make_repo(find_all_by_owner=trips)

        result = asyncio.run(GetAllTripsUseCase(repo).execute("user-1"))

        assert result == trips

    def test_returns_empty_list_when_no_trips_exist(self):
        repo = make_repo(find_all_by_owner=[])

        result = asyncio.run(GetAllTripsUseCase(repo).execute("user-1"))

        assert result == []


# ---------------------------------------------------------------------------
# DeleteTripUseCase
# ---------------------------------------------------------------------------

class TestDeleteTripUseCase:

    def test_returns_true_when_trip_is_deleted(self):
        trip = make_trip()
        repo = make_repo(find_by_owner=trip, delete=True)

        result = asyncio.run(DeleteTripUseCase(repo).execute("42", "user-1"))

        assert result is True

    def test_calls_delete_on_the_repository(self):
        trip = make_trip()
        repo = make_repo(find_by_owner=trip, delete=True)

        asyncio.run(DeleteTripUseCase(repo).execute("42", "user-1"))

        repo.delete.assert_called_once()

    def test_raises_entity_not_found_when_trip_is_missing(self):
        repo = make_repo(find_by_owner=None)

        with pytest.raises(EntityNotFound):
            asyncio.run(DeleteTripUseCase(repo).execute("999", "user-1"))

    def test_does_not_call_delete_when_trip_does_not_exist(self):
        repo = make_repo(find_by_owner=None)

        with pytest.raises(EntityNotFound):
            asyncio.run(DeleteTripUseCase(repo).execute("999", "user-1"))

        repo.delete.assert_not_called()


# ---------------------------------------------------------------------------
# UpdateTripUseCase
# ---------------------------------------------------------------------------

class TestUpdateTripUseCase:

    def test_returns_updated_trip(self):
        existing = make_trip(trip_id=1)
        updated = make_trip(trip_id=1)
        updated.name = "Updated Name"
        repo = make_repo(find_by_owner=existing, save=updated)

        result = asyncio.run(UpdateTripUseCase(repo).execute("1", updated, "user-1"))

        assert result == updated

    def test_saves_the_updated_trip_to_repository(self):
        existing = make_trip(trip_id=1)
        updated = make_trip(trip_id=1)
        repo = make_repo(find_by_owner=existing, save=updated)

        asyncio.run(UpdateTripUseCase(repo).execute("1", updated, "user-1"))

        repo.save.assert_called_once_with(updated)

    def test_raises_entity_not_found_when_trip_is_missing(self):
        updated = make_trip()
        repo = make_repo(find_by_owner=None)

        with pytest.raises(EntityNotFound):
            asyncio.run(UpdateTripUseCase(repo).execute("999", updated, "user-1"))

    def test_does_not_save_when_trip_does_not_exist(self):
        updated = make_trip()
        repo = make_repo(find_by_owner=None)

        with pytest.raises(EntityNotFound):
            asyncio.run(UpdateTripUseCase(repo).execute("999", updated, "user-1"))

        repo.save.assert_not_called()
