"""
Unit tests for UpdateTripUseCase.update_status.
"""
import asyncio
from datetime import date
from unittest.mock import AsyncMock

import pytest

from src.shared.domain.exceptions import EntityNotFound
from src.trips.application.use_cases.update_trip import UpdateTripUseCase
from src.trips.domain.entities.trip import Trip
from src.trips.domain.value_objects.trip_status import TripStatus


def make_trip(trip_id: int = 1, owner_id: str = "user-1", status: TripStatus = TripStatus.PLANNING) -> Trip:
    """Return a minimal valid Trip for use in tests."""
    return Trip(
        id=trip_id,
        owner_id=owner_id,
        name="Summer Holiday",
        destination="Barcelona",
        start_date=date(2025, 7, 1),
        end_date=date(2025, 7, 8),
        status=status,
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


class TestUpdateTripUseCaseStatus:

    def test_returns_updated_trip_with_new_status(self):
        trip = make_trip(trip_id=1, status=TripStatus.PLANNING)
        repo = make_repo(find_by_owner=trip, update_status=True)

        result = asyncio.run(
            UpdateTripUseCase(repo).update_status("1", "user-1", TripStatus.CONFIRMED)
        )

        assert result.status == TripStatus.CONFIRMED
        assert result.updated_at is not None

    def test_calls_update_status_on_repository(self):
        trip = make_trip(trip_id=1, status=TripStatus.PLANNING)
        repo = make_repo(find_by_owner=trip, update_status=True)

        asyncio.run(
            UpdateTripUseCase(repo).update_status("1", "user-1", TripStatus.CONFIRMED)
        )

        repo.update_status.assert_called_once()

    def test_raises_entity_not_found_when_trip_is_missing(self):
        repo = make_repo(find_by_owner=None)

        with pytest.raises(EntityNotFound) as exc_info:
            asyncio.run(
                UpdateTripUseCase(repo).update_status("999", "user-1", TripStatus.CONFIRMED)
            )

        assert exc_info.value.entity_type == "Trip"
        assert exc_info.value.entity_id == "999"

    def test_raises_entity_not_found_when_trip_is_not_owned_by_user(self):
        repo = make_repo(find_by_owner=None)

        with pytest.raises(EntityNotFound):
            asyncio.run(
                UpdateTripUseCase(repo).update_status("42", "different-user", TripStatus.CONFIRMED)
            )

    def test_does_not_call_update_status_when_trip_does_not_exist(self):
        repo = make_repo(find_by_owner=None)

        with pytest.raises(EntityNotFound):
            asyncio.run(
                UpdateTripUseCase(repo).update_status("999", "user-1", TripStatus.CONFIRMED)
            )

        repo.update_status.assert_not_called()

    def test_transitions_to_in_progress_status(self):
        trip = make_trip(trip_id=1, status=TripStatus.CONFIRMED)
        repo = make_repo(find_by_owner=trip, update_status=True)

        result = asyncio.run(
            UpdateTripUseCase(repo).update_status("1", "user-1", TripStatus.IN_PROGRESS)
        )

        assert result.status == TripStatus.IN_PROGRESS

    def test_transitions_to_completed_status(self):
        trip = make_trip(trip_id=1, status=TripStatus.IN_PROGRESS)
        repo = make_repo(find_by_owner=trip, update_status=True)

        result = asyncio.run(
            UpdateTripUseCase(repo).update_status("1", "user-1", TripStatus.COMPLETED)
        )

        assert result.status == TripStatus.COMPLETED

    def test_transitions_to_cancelled_status(self):
        trip = make_trip(trip_id=1, status=TripStatus.PLANNING)
        repo = make_repo(find_by_owner=trip, update_status=True)

        result = asyncio.run(
            UpdateTripUseCase(repo).update_status("1", "user-1", TripStatus.CANCELLED)
        )

        assert result.status == TripStatus.CANCELLED

    def test_transitions_back_to_planning_status(self):
        trip = make_trip(trip_id=1, status=TripStatus.CANCELLED)
        repo = make_repo(find_by_owner=trip, update_status=True)

        result = asyncio.run(
            UpdateTripUseCase(repo).update_status("1", "user-1", TripStatus.PLANNING)
        )

        assert result.status == TripStatus.PLANNING

    def test_passes_correct_trip_id_to_repository(self):
        trip = make_trip(trip_id=1)
        repo = make_repo(find_by_owner=trip, update_status=True)

        asyncio.run(
            UpdateTripUseCase(repo).update_status("1", "user-1", TripStatus.CONFIRMED)
        )

        called_with = repo.find_by_owner.call_args[0][0]
        assert called_with == 1

    def test_passes_correct_owner_id_to_repository(self):
        trip = make_trip(trip_id=1)
        repo = make_repo(find_by_owner=trip, update_status=True)

        asyncio.run(
            UpdateTripUseCase(repo).update_status("1", "user-1", TripStatus.CONFIRMED)
        )

        called_with = repo.find_by_owner.call_args[0][1]
        assert called_with == "user-1"