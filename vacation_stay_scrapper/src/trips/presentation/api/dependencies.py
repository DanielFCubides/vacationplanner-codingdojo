"""
FastAPI Dependencies

Dependency injection for trip-related components.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database.session import get_db_session
from ...infrastructure.persistence.postgres_trip_repository import PostgresTripRepository
from ...domain.repositories.trip_repository import ITripRepository
from ...application.use_cases.create_trip import CreateTripUseCase
from ...application.use_cases.get_trip import GetTripUseCase, GetAllTripsUseCase
from ...application.use_cases.update_trip import UpdateTripUseCase
from ...application.use_cases.delete_trip import DeleteTripUseCase
from ...application.use_cases.update_flight_status import UpdateFlightStatusUseCase
from ...application.use_cases.update_accommodation_status import UpdateAccommodationStatusUseCase


def get_trip_repository(
    session: AsyncSession = Depends(get_db_session)
) -> ITripRepository:
    return PostgresTripRepository(session)


def get_create_trip_use_case(
    repository: ITripRepository = Depends(get_trip_repository)
) -> CreateTripUseCase:
    return CreateTripUseCase(repository)


def get_get_trip_use_case(
    repository: ITripRepository = Depends(get_trip_repository)
) -> GetTripUseCase:
    return GetTripUseCase(repository)


def get_get_all_trips_use_case(
    repository: ITripRepository = Depends(get_trip_repository)
) -> GetAllTripsUseCase:
    return GetAllTripsUseCase(repository)


def get_update_trip_use_case(
    repository: ITripRepository = Depends(get_trip_repository)
) -> UpdateTripUseCase:
    return UpdateTripUseCase(repository)


def get_delete_trip_use_case(
    repository: ITripRepository = Depends(get_trip_repository)
) -> DeleteTripUseCase:
    return DeleteTripUseCase(repository)


def get_update_flight_status_use_case(
    repository: ITripRepository = Depends(get_trip_repository)
) -> UpdateFlightStatusUseCase:
    return UpdateFlightStatusUseCase(repository)


def get_update_accommodation_status_use_case(
    repository: ITripRepository = Depends(get_trip_repository)
) -> UpdateAccommodationStatusUseCase:
    return UpdateAccommodationStatusUseCase(repository)
