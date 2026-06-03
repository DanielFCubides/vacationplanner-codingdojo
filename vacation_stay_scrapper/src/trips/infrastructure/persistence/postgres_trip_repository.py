from datetime import date
from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.exceptions import EntityNotFound
from src.trips.domain.entities.accommodation import Accommodation
from src.trips.domain.entities.flight import Flight
from src.trips.domain.entities.trip import Trip
from src.trips.domain.repositories.trip_repository import ITripRepository
from src.trips.infrastructure.persistence.mappers.trip_orm_mapper import TripOrmMapper
from src.trips.infrastructure.persistence.models.accommodation import Accommodation as AccommodationOrm
from src.trips.infrastructure.persistence.models.flight import Flight as FlightOrm
from src.trips.infrastructure.persistence.models.trip import Trip as TripOrm


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
            trip.id = model.id_
        else:
            existing = await self._session.get(TripOrm, trip.id)
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

    async def update_status(self, trip_id: int, status: str) -> bool:
        result = await self._session.execute(
            update(TripOrm)
            .where(TripOrm.id_ == trip_id)
            .values(status=status, updated_at=date.today())
        )
        await self._session.flush()
        return result.rowcount > 0

    async def update_flight(self, flight: Flight, trip_id: int) -> Flight:
        result = await self._session.execute(
            select(FlightOrm).where(
                FlightOrm.id_ == flight.id,
                FlightOrm.trip_id == trip_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing is None:
            raise EntityNotFound(entity_type="Flight", entity_id=flight.id)

        existing.airline = flight.airline
        existing.flight_number = flight.flight_number
        existing.departure_airport_code = flight.departure_airport.code
        existing.departure_airport_city = flight.departure_airport.city
        existing.departure_time = flight.departure_time
        existing.arrival_airport_code = flight.arrival_airport.code
        existing.arrival_airport_city = flight.arrival_airport.city
        existing.arrival_time = flight.arrival_time
        existing.duration = flight.duration
        existing.price_amount = flight.price.amount
        existing.price_currency = flight.price.currency
        existing.stops = flight.stops
        existing.cabin_class = flight.cabin_class
        existing.status = flight.status

        await self._session.flush()
        return flight

    async def update_accommodation(self, accommodation: Accommodation, trip_id: int) -> Accommodation:
        result = await self._session.execute(
            select(AccommodationOrm).where(
                AccommodationOrm.id_ == accommodation.id,
                AccommodationOrm.trip_id == trip_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing is None:
            raise EntityNotFound(entity_type="Accommodation", entity_id=accommodation.id)

        existing.name = accommodation.name
        existing.type = accommodation.type
        existing.check_in = accommodation.check_in
        existing.check_out = accommodation.check_out
        existing.price_per_night_amount = accommodation.price_per_night.amount
        existing.price_per_night_currency = accommodation.price_per_night.currency
        existing.total_price_amount = accommodation.total_price.amount
        existing.total_price_currency = accommodation.total_price.currency
        existing.rating = accommodation.rating
        existing.amenities = accommodation.amenities
        existing.status = accommodation.status
        existing.image = accommodation.image

        await self._session.flush()
        return accommodation
