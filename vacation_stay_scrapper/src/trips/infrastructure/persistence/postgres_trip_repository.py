from datetime import date
from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.trips.domain.entities.trip import Trip
from src.trips.domain.repositories.trip_repository import ITripRepository
from src.trips.infrastructure.persistence.mappers.trip_orm_mapper import TripOrmMapper
from src.trips.infrastructure.persistence.models.trip_model import TripModel


class PostgresTripRepository(ITripRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, trip: Trip) -> Trip:
        if trip.created_at is None:
            trip.created_at = date.today()
        trip.updated_at = date.today()

        if trip.id is None:
            model = TripOrmMapper.to_model(trip)
            self._session.add(model)
            await self._session.flush()
            trip.id = model.id
        else:
            existing = await self._session.get(TripModel, trip.id)
            updated = TripOrmMapper.to_model(trip)
            if existing is None:
                self._session.add(updated)
                await self._session.flush()
            else:
                existing.owner_id = updated.owner_id
                existing.name = updated.name
                existing.destination = updated.destination
                existing.start_date = updated.start_date
                existing.end_date = updated.end_date
                existing.status = updated.status
                existing.budget_total_amount = updated.budget_total_amount
                existing.budget_total_currency = updated.budget_total_currency
                existing.budget_spent_amount = updated.budget_spent_amount
                existing.budget_spent_currency = updated.budget_spent_currency
                existing.created_at = updated.created_at
                existing.updated_at = updated.updated_at
                existing.travelers = updated.travelers
                existing.flights = updated.flights
                existing.accommodations = updated.accommodations
                existing.activities = updated.activities
                existing.budget_categories = updated.budget_categories
                await self._session.flush()

        return trip

    async def find_by_id(self, trip_id: int) -> Optional[Trip]:
        result = await self._session.execute(
            select(TripModel).where(TripModel.id == trip_id)
        )
        model = result.scalar_one_or_none()
        return TripOrmMapper.to_domain(model) if model else None

    async def find_by_owner(self, trip_id: int, owner_id: str) -> Optional[Trip]:
        result = await self._session.execute(
            select(TripModel).where(
                TripModel.id == trip_id,
                TripModel.owner_id == owner_id,
            )
        )
        model = result.scalar_one_or_none()
        return TripOrmMapper.to_domain(model) if model else None

    async def find_all_by_owner(self, owner_id: str) -> List[Trip]:
        result = await self._session.execute(
            select(TripModel).where(TripModel.owner_id == owner_id)
        )
        return [TripOrmMapper.to_domain(m) for m in result.scalars().all()]

    async def delete(self, trip_id: int) -> bool:
        result = await self._session.execute(
            delete(TripModel).where(TripModel.id == trip_id)
        )
        return result.rowcount > 0

    async def exists(self, trip_id: int) -> bool:
        result = await self._session.execute(
            select(TripModel.id).where(TripModel.id == trip_id)
        )
        return result.scalar_one_or_none() is not None
