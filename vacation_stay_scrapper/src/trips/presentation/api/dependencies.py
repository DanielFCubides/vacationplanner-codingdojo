"""
FastAPI Dependencies

Dependency injection for trip-related components.
"""
from functools import lru_cache
from fastapi import Depends

from ...infrastructure.persistence.in_memory_trip_repository import InMemoryTripRepository
from ...domain.repositories.trip_repository import ITripRepository
from ...application.use_cases.create_trip import CreateTripUseCase
from ...application.use_cases.get_trip import GetTripUseCase, GetAllTripsUseCase
from ...application.use_cases.update_trip import UpdateTripUseCase
from ...application.use_cases.delete_trip import DeleteTripUseCase


# Repository singleton
@lru_cache()
def get_trip_repository() -> ITripRepository:
    """
    Get trip repository instance
    
    Returns:
        Trip repository (singleton)
    """
    return InMemoryTripRepository()


# Use case dependencies

def get_create_trip_use_case(
    repository: ITripRepository = Depends(get_trip_repository)
) -> CreateTripUseCase:
    """Get create trip use case"""
    return CreateTripUseCase(repository)


def get_get_trip_use_case(
    repository: ITripRepository = Depends(get_trip_repository)
) -> GetTripUseCase:
    """Get get trip use case"""
    return GetTripUseCase(repository)


def get_get_all_trips_use_case(
    repository: ITripRepository = Depends(get_trip_repository)
) -> GetAllTripsUseCase:
    """Get all trips use case"""
    return GetAllTripsUseCase(repository)


def get_update_trip_use_case(
    repository: ITripRepository = Depends(get_trip_repository)
) -> UpdateTripUseCase:
    """Get update trip use case"""
    return UpdateTripUseCase(repository)


def get_delete_trip_use_case(
    repository: ITripRepository = Depends(get_trip_repository)
) -> DeleteTripUseCase:
    """Get delete trip use case"""
    return DeleteTripUseCase(repository)
