from datetime import date
from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.trips.domain.entities.trip import Trip
from src.trips.domain.repositories.trip_repository import ITripRepository
from src.trips.infrastructure.persistence.mappers.trip_orm_mapper import TripOrmMapper
from src.trips.infrastructure.persistence.models.trip import Trip as TripOrm


class PostgresTripRepository(ITripRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, trip: Trip) -> Trip:
        if trip.created_at is None:
            trip.created_at = date.today()
        trip.updated_at = date.today()

        model = TripOrmMapper.to_model(trip)

        if trip.id is None:
            # New trip: let the database assign the autoincrement id.
            self._session.add(model)
            await self._session.flush()
            trip.id = model.id_
        else:
            # Existing trip: merge the full desired state onto the persistent
            # row and its child collections. merge() reconciles children by
            # primary key (insert/update) and, with the delete-orphan cascade,
            # removes children no longer present — all without creating a
            # duplicate parent (which previously caused a trips_pkey conflict).
            merged = await self._session.merge(model)
            await self._session.flush()
            trip.id = merged.id_

        return trip

    async def find_by_id(self, trip_id: int) -> Optional[Trip]:
        result = await self._session.execute(
            select(TripOrm).where(TripOrm.id_ == trip_id)
        )
        model = result.scalar_one_or_none()
        return TripOrmMapper.to_domain(model) if model else None

    async def find_by_owner(self, trip_id: int, owner_id: str) -> Optional[Trip]:
        result = await self._session.execute(
            select(TripOrm).where(
                TripOrm.id_ == trip_id,
                TripOrm.owner_id == owner_id,
            )
        )
        model = result.scalar_one_or_none()
        return TripOrmMapper.to_domain(model) if model else None

    async def find_all_by_owner(self, owner_id: str) -> List[Trip]:
        result = await self._session.execute(
            select(TripOrm).where(TripOrm.owner_id == owner_id)
        )
        return [TripOrmMapper.to_domain(m) for m in result.scalars().all()]

    async def delete(self, trip_id: int) -> bool:
        result = await self._session.execute(
            delete(TripOrm).where(TripOrm.id_ == trip_id)
        )
        return result.rowcount > 0

    async def exists(self, trip_id: int) -> bool:
        result = await self._session.execute(
            select(TripOrm.id_).where(TripOrm.id_ == trip_id)
        )
        return result.scalar_one_or_none() is not None
