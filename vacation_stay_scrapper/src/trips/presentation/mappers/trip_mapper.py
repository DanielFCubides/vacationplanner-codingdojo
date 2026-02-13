"""
Trip Mappers

Convert between domain entities and API schemas.
"""
from datetime import date as date_type
from decimal import Decimal

from ...domain.entities.trip import Trip
from ...domain.entities.flight import Flight
from ...domain.entities.traveler import Traveler
from ...domain.entities.activity import Activity
from ...domain.value_objects.trip_id import TripId
from ...domain.value_objects.trip_status import TripStatus
from ...domain.value_objects.airport import Airport
from ...domain.value_objects.money import Money
from ..api.schemas import (
    TripResponse,
    TripCreateRequest,
    TripUpdateRequest,
    FlightResponse,
    TravelerResponse,
    ActivityResponse
)


class TripMapper:
    """Maps between Trip domain entities and API schemas"""
    
    @staticmethod
    def to_response(trip: Trip) -> TripResponse:
        """
        Convert Trip entity to API response
        
        Args:
            trip: Trip domain entity
            
        Returns:
            TripResponse schema
        """
        total_cost = trip.total_cost
        
        return TripResponse(
            id=str(trip.id),
            name=trip.name,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            status=str(trip.status),
            duration_days=trip.duration_days,
            budget=float(trip.budget.amount) if trip.budget else None,
            budget_currency=trip.budget.currency if trip.budget else None,
            total_cost=float(total_cost.amount) if total_cost else None,
            travelers=[TripMapper._traveler_to_response(t) for t in trip.travelers],
            flights=[TripMapper._flight_to_response(f) for f in trip.flights],
            activities=[TripMapper._activity_to_response(a) for a in trip.activities],
            created_at=trip.created_at,
            updated_at=trip.updated_at
        )
    
    @staticmethod
    def from_create_request(request: TripCreateRequest) -> Trip:
        """
        Convert create request to Trip entity
        
        Args:
            request: TripCreateRequest schema
            
        Returns:
            Trip domain entity
        """
        return Trip(
            id=TripId.generate(),
            name=request.name,
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            status=TripStatus.PLANNING,
            budget=Money.from_float(request.budget) if request.budget else None,
            created_at=date_type.today()
        )
    
    @staticmethod
    def update_from_request(trip: Trip, request: TripUpdateRequest) -> Trip:
        """
        Update Trip entity from update request
        
        Args:
            trip: Existing trip entity
            request: TripUpdateRequest schema
            
        Returns:
            Updated trip entity
        """
        if request.name is not None:
            trip.name = request.name
        if request.destination is not None:
            trip.destination = request.destination
        if request.start_date is not None:
            trip.start_date = request.start_date
        if request.end_date is not None:
            trip.end_date = request.end_date
        if request.status is not None:
            trip.status = TripStatus.from_string(request.status)
        if request.budget is not None:
            trip.budget = Money.from_float(request.budget)
        
        trip.updated_at = date_type.today()
        return trip
    
    @staticmethod
    def _traveler_to_response(traveler: Traveler) -> TravelerResponse:
        """Convert Traveler entity to response"""
        return TravelerResponse(
            id=traveler.id,
            name=traveler.name,
            email=traveler.email,
            role=traveler.role,
            avatar=traveler.avatar
        )
    
    @staticmethod
    def _flight_to_response(flight: Flight) -> FlightResponse:
        """Convert Flight entity to response"""
        return FlightResponse(
            id=flight.id,
            airline=flight.airline,
            flight_number=flight.flight_number,
            departure_airport_code=flight.departure_airport.code,
            departure_airport_city=flight.departure_airport.city,
            arrival_airport_code=flight.arrival_airport.code,
            arrival_airport_city=flight.arrival_airport.city,
            departure_time=flight.departure_time,
            arrival_time=flight.arrival_time,
            price=float(flight.price.amount),
            currency=flight.price.currency,
            cabin_class=flight.cabin_class,
            status=flight.status
        )
    
    @staticmethod
    def _activity_to_response(activity: Activity) -> ActivityResponse:
        """Convert Activity entity to response"""
        return ActivityResponse(
            id=activity.id,
            name=activity.name,
            date=activity.date,
            cost=float(activity.cost.amount),
            currency=activity.cost.currency,
            category=activity.category,
            status=activity.status,
            description=activity.description
        )
