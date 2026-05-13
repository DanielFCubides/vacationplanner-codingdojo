"""
Unit tests for PostgresTripRepository.

Uses mocked AsyncSession — no real database involved.
"""
import asyncio
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.trips.domain.entities.trip import Trip
from src.trips.domain.value_objects.trip_status import TripStatus
from src.trips.infrastructure.persistence.models.trip import Trip as TripOrm
from src.trips.infrastructure.persistence.postgres_trip_repository import PostgresTripRepository


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_trip(trip_id=None, owner_id="user-1") -> Trip:
    return Trip(
        id=trip_id,
        owner_id=owner_id,
        name="Summer Holiday",
        destination="Barcelona",
        start_date=date(2025, 7, 1),
        end_date=date(2025, 7, 8),
        status=TripStatus.PLANNING,
    )


def make_trip_model(trip_id=1, owner_id="user-1") -> TripOrm:
    model = TripOrm(
        owner_id=owner_id,
        name="Summer Holiday",
        destination="Barcelona",
        start_date=date(2025, 7, 1),
        end_date=date(2025, 7, 8),
        status="planning",
    )
    model.id_ = trip_id
    model.travelers = []
    model.flights = []
    model.accommodations = []
    model.activities = []
    model.budget_categories = []
    model.budget_total_amount = None
    model.created_at = None
    model.updated_at = None
    return model


def make_session() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    return session


def scalar_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def scalars_result(values):
    result = MagicMock()
    inner = MagicMock()
    inner.all.return_value = values
    result.scalars.return_value = inner
    return result


# ---------------------------------------------------------------------------
# save — new trip (id is None)
# ---------------------------------------------------------------------------

class TestSaveNewTrip:

    def test_adds_model_to_session(self):
        session = make_session()
        model = make_trip_model(trip_id=42)
        session.flush = AsyncMock(side_effect=lambda: setattr(model, "id_", 42))

        trip = make_trip(trip_id=None)

        with patch(
            "src.trips.infrastructure.persistence.postgres_trip_repository.TripOrmMapper.to_model",
            return_value=model,
        ):
            asyncio.run(PostgresTripRepository(session).save(trip))

        session.add.assert_called_once_with(model)

    def test_assigns_id_from_model_after_flush(self):
        session = make_session()
        model = make_trip_model(trip_id=99)

        async def fake_flush():
            model.id_ = 99

        session.flush = AsyncMock(side_effect=fake_flush)

        trip = make_trip(trip_id=None)

        with patch(
            "src.trips.infrastructure.persistence.postgres_trip_repository.TripOrmMapper.to_model",
            return_value=model,
        ):
            asyncio.run(PostgresTripRepository(session).save(trip))

        assert trip.id == 99

    def test_sets_timestamps(self):
        session = make_session()
        model = make_trip_model()
        session.flush = AsyncMock()

        trip = make_trip(trip_id=None)
        assert trip.created_at is None

        with patch(
            "src.trips.infrastructure.persistence.postgres_trip_repository.TripOrmMapper.to_model",
            return_value=model,
        ):
            asyncio.run(PostgresTripRepository(session).save(trip))

        assert trip.created_at == date.today()
        assert trip.updated_at == date.today()


# ---------------------------------------------------------------------------
# save — existing trip (id set)
# ---------------------------------------------------------------------------

class TestSaveExistingTrip:

    def test_updates_existing_model_fields(self):
        session = make_session()
        existing_model = make_trip_model(trip_id=1)
        updated_model = make_trip_model(trip_id=1)
        updated_model.name = "New Name"

        session.get = AsyncMock(return_value=existing_model)
        session.flush = AsyncMock()

        trip = make_trip(trip_id=1)
        trip.name = "New Name"

        with patch(
            "src.trips.infrastructure.persistence.postgres_trip_repository.TripOrmMapper.to_model",
            return_value=updated_model,
        ):
            asyncio.run(PostgresTripRepository(session).save(trip))

        assert existing_model.name == "New Name"
        session.flush.assert_called_once()

    def test_adds_new_model_when_not_found_in_db(self):
        session = make_session()
        new_model = make_trip_model(trip_id=7)

        session.get = AsyncMock(return_value=None)
        session.flush = AsyncMock()

        trip = make_trip(trip_id=7)

        with patch(
            "src.trips.infrastructure.persistence.postgres_trip_repository.TripOrmMapper.to_model",
            return_value=new_model,
        ):
            asyncio.run(PostgresTripRepository(session).save(trip))

        session.add.assert_called_once_with(new_model)


# ---------------------------------------------------------------------------
# find_by_id
# ---------------------------------------------------------------------------

class TestFindById:

    def test_returns_domain_trip_when_found(self):
        session = make_session()
        model = make_trip_model(trip_id=1)
        session.execute = AsyncMock(return_value=scalar_result(model))

        result = asyncio.run(PostgresTripRepository(session).find_by_id(1))

        assert result is not None
        assert result.id == 1

    def test_returns_none_when_not_found(self):
        session = make_session()
        session.execute = AsyncMock(return_value=scalar_result(None))

        result = asyncio.run(PostgresTripRepository(session).find_by_id(999))

        assert result is None


# ---------------------------------------------------------------------------
# find_by_owner
# ---------------------------------------------------------------------------

class TestFindByOwner:

    def test_returns_trip_belonging_to_owner(self):
        session = make_session()
        model = make_trip_model(trip_id=1, owner_id="user-1")
        session.execute = AsyncMock(return_value=scalar_result(model))

        result = asyncio.run(PostgresTripRepository(session).find_by_owner(1, "user-1"))

        assert result is not None
        assert result.owner_id == "user-1"

    def test_returns_none_when_trip_not_found(self):
        session = make_session()
        session.execute = AsyncMock(return_value=scalar_result(None))

        result = asyncio.run(PostgresTripRepository(session).find_by_owner(1, "user-1"))

        assert result is None


# ---------------------------------------------------------------------------
# find_all_by_owner
# ---------------------------------------------------------------------------

class TestFindAllByOwner:

    def test_returns_all_trips_for_owner(self):
        session = make_session()
        models = [make_trip_model(trip_id=1), make_trip_model(trip_id=2)]
        session.execute = AsyncMock(return_value=scalars_result(models))

        result = asyncio.run(PostgresTripRepository(session).find_all_by_owner("user-1"))

        assert len(result) == 2

    def test_returns_empty_list_when_no_trips(self):
        session = make_session()
        session.execute = AsyncMock(return_value=scalars_result([]))

        result = asyncio.run(PostgresTripRepository(session).find_all_by_owner("user-1"))

        assert result == []


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

class TestDelete:

    def test_returns_true_when_trip_deleted(self):
        session = make_session()
        db_result = MagicMock()
        db_result.rowcount = 1
        session.execute = AsyncMock(return_value=db_result)

        result = asyncio.run(PostgresTripRepository(session).delete(1))

        assert result is True

    def test_returns_false_when_trip_not_found(self):
        session = make_session()
        db_result = MagicMock()
        db_result.rowcount = 0
        session.execute = AsyncMock(return_value=db_result)

        result = asyncio.run(PostgresTripRepository(session).delete(999))

        assert result is False


# ---------------------------------------------------------------------------
# exists
# ---------------------------------------------------------------------------

class TestExists:

    def test_returns_true_when_trip_exists(self):
        session = make_session()
        session.execute = AsyncMock(return_value=scalar_result(1))

        result = asyncio.run(PostgresTripRepository(session).exists(1))

        assert result is True

    def test_returns_false_when_trip_does_not_exist(self):
        session = make_session()
        session.execute = AsyncMock(return_value=scalar_result(None))

        result = asyncio.run(PostgresTripRepository(session).exists(999))

        assert result is False
