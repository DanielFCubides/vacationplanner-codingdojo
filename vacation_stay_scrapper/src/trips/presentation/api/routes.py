"""
Trip API Routes

FastAPI routes for trip management CRUD operations.
"""
import logging

from fastapi import APIRouter, Depends, status
from typing import List, Annotated

from fastapi.security import HTTPBearer

from src.shared.infrastructure.auth.dependencies import get_current_user
from .schemas import (
    TripCreateRequest,
    TripUpdateRequest,
    TripResponse,
    TripListResponse,
    MessageResponse
)
from .dependencies import (
    get_create_trip_use_case,
    get_get_trip_use_case,
    get_get_all_trips_use_case,
    get_update_trip_use_case,
    get_delete_trip_use_case
)
from ...application.use_cases.create_trip import CreateTripUseCase
from ...application.use_cases.get_trip import GetTripUseCase, GetAllTripsUseCase
from ...application.use_cases.update_trip import UpdateTripUseCase
from ...application.use_cases.delete_trip import DeleteTripUseCase
from ..mappers.trip_mapper import TripMapper

# Create router
router = APIRouter(prefix="/api/trips", tags=["trips"])
@router.post(
    "",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new trip"
)
async def create_trip(
        request: TripCreateRequest,
        use_case: CreateTripUseCase = Depends(get_create_trip_use_case),
        token: str = Depends(get_current_user)
) -> TripResponse:
    """
    Create a new trip

    Args:
        request: Trip creation request
        use_case: Create trip use case (injected)

    Returns:
        Created trip details
    """
    # Convert request to domain entity
    trip = TripMapper.from_create_request(request)

    # Execute use case
    created_trip = await use_case.execute(trip)

    # Convert to response
    return TripMapper.to_response(created_trip)


@router.get(
    "",
    response_model=TripListResponse,
    summary="Get all trips"
)
async def get_all_trips(
        use_case: GetAllTripsUseCase = Depends(get_get_all_trips_use_case),
        token: str = Depends(get_current_user)
) -> TripListResponse:
    """
    Get all trips
    
    Args:
        use_case: Get all trips use case (injected)
        
    Returns:
        List of all trips
    """
    trips = await use_case.execute()

    return TripListResponse(
        trips=[TripMapper.to_response(trip) for trip in trips],
        total=len(trips)
    )


@router.get(
    "/{trip_id}",
    response_model=TripResponse,
    summary="Get trip by ID"
)
async def get_trip(
        trip_id: str,
        use_case: GetTripUseCase = Depends(get_get_trip_use_case),
        token: str = Depends(get_current_user)
) -> TripResponse:
    """
    Get trip by ID
    
    Args:
        trip_id: Trip identifier
        use_case: Get trip use case (injected)
        
    Returns:
        Trip details
    """
    trip = await use_case.execute(trip_id)
    return TripMapper.to_response(trip)


@router.put(
    "/{trip_id}",
    response_model=TripResponse,
    summary="Update trip"
)
async def update_trip(
        trip_id: str,
        request: TripUpdateRequest,
        use_case: UpdateTripUseCase = Depends(get_update_trip_use_case),
        get_use_case: GetTripUseCase = Depends(get_get_trip_use_case),
        token: str = Depends(get_current_user)
) -> TripResponse:
    """
    Update an existing trip
    
    Args:
        trip_id: Trip identifier
        request: Trip update request
        use_case: Update trip use case (injected)
        get_use_case: Get trip use case (injected)
        
    Returns:
        Updated trip details
    """
    # Get existing trip
    existing_trip = await get_use_case.execute(trip_id)

    # Update trip with request data
    updated_trip = TripMapper.update_from_request(existing_trip, request)

    # Execute update
    result = await use_case.execute(trip_id, updated_trip)

    return TripMapper.to_response(result)


@router.delete(
    "/{trip_id}",
    response_model=MessageResponse,
    summary="Delete trip"
)
async def delete_trip(
        trip_id: str,
        use_case: DeleteTripUseCase = Depends(get_delete_trip_use_case),
        token: str = Depends(get_current_user)
) -> MessageResponse:
    """
    Delete a trip
    
    Args:
        trip_id: Trip identifier
        use_case: Delete trip use case (injected)
        
    Returns:
        Success message
    """
    await use_case.execute(trip_id)

    return MessageResponse(
        message=f"Trip {trip_id} deleted successfully"
    )
