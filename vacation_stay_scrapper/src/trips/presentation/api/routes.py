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
        current_user: dict = Depends(get_current_user)
) -> TripResponse:
    """
    Create a new trip

    The owner of the trip is automatically set to the authenticated user.

    Args:
        request: Trip creation request
        use_case: Create trip use case (injected)
        current_user: Decoded JWT claims from the authenticated user

    Returns:
        Created trip details
    """
    owner_id = current_user["sub"]

    trip = TripMapper.from_create_request(request, owner_id=owner_id)

    created_trip = await use_case.execute(trip)

    return TripMapper.to_response(created_trip)


@router.get(
    "",
    response_model=TripListResponse,
    summary="Get all trips"
)
async def get_all_trips(
        use_case: GetAllTripsUseCase = Depends(get_get_all_trips_use_case),
        current_user: dict = Depends(get_current_user)
) -> TripListResponse:
    """
    Get all trips belonging to the authenticated user.

    Args:
        use_case: Get all trips use case (injected)
        current_user: Decoded JWT claims from the authenticated user

    Returns:
        List of trips owned by the current user
    """
    owner_id = current_user["sub"]
    trips = await use_case.execute(owner_id=owner_id)

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
        current_user: dict = Depends(get_current_user)
) -> TripResponse:
    """
    Get a trip by ID. Only returns the trip if it belongs to the authenticated user.

    Args:
        trip_id: Trip identifier
        use_case: Get trip use case (injected)
        current_user: Decoded JWT claims from the authenticated user

    Returns:
        Trip details
    """
    owner_id = current_user["sub"]
    trip = await use_case.execute(trip_id, owner_id=owner_id)
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
        current_user: dict = Depends(get_current_user)
) -> TripResponse:
    """
    Update an existing trip. Only the owner can update their trip.

    Args:
        trip_id: Trip identifier
        request: Trip update request
        use_case: Update trip use case (injected)
        get_use_case: Get trip use case (injected)
        current_user: Decoded JWT claims from the authenticated user

    Returns:
        Updated trip details
    """
    owner_id = current_user["sub"]

    # Fetch existing trip scoped to owner
    existing_trip = await get_use_case.execute(trip_id, owner_id=owner_id)

    # Apply changes from request onto the existing entity
    updated_trip = TripMapper.update_from_request(existing_trip, request)

    # Persist update, scoped to owner
    result = await use_case.execute(trip_id, updated_trip, owner_id=owner_id)

    return TripMapper.to_response(result)


@router.delete(
    "/{trip_id}",
    response_model=MessageResponse,
    summary="Delete trip"
)
async def delete_trip(
        trip_id: str,
        use_case: DeleteTripUseCase = Depends(get_delete_trip_use_case),
        current_user: dict = Depends(get_current_user)
) -> MessageResponse:
    """
    Delete a trip. Only the owner can delete their trip.

    Args:
        trip_id: Trip identifier
        use_case: Delete trip use case (injected)
        current_user: Decoded JWT claims from the authenticated user

    Returns:
        Success message
    """
    owner_id = current_user["sub"]
    await use_case.execute(trip_id, owner_id=owner_id)

    return MessageResponse(
        message=f"Trip {trip_id} deleted successfully"
    )
