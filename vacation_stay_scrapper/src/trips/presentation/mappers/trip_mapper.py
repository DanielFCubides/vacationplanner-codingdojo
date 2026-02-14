"""
Trip Mappers

Convert between domain entities and API schemas.
Ensures compatibility with frontend Models.ts
"""
from datetime import date as date_type

from ...domain.entities.trip import Trip
from ...domain.entities.flight import Flight
from ...domain.entities.traveler import Traveler
from ...domain.entities.activity import Activity
from ...domain.entities.accommodation import Accommodation
from ...domain.value_objects.trip_id import TripId
from ...domain.value_objects.trip_status import TripStatus
from ...domain.value_objects.budget import Budget, BudgetCategory
from ...domain.value_objects.money import Money
from ..api.schemas import (
    TripResponse,
    TripCreateRequest,
    TripUpdateRequest,
    FlightResponse,
    FlightLocationResponse,
    TravelerResponse,
    ActivityResponse,
    AccommodationResponse,
    BudgetResponse,
    BudgetCategoryResponse
)


class TripMapper:
    """Maps between Trip domain entities and API schemas"""
    
    @staticmethod
    def to_response(trip: Trip) -> TripResponse:
        """
        Convert Trip entity to API response matching frontend model
        
        Args:
            trip: Trip domain entity
            
        Returns:
            TripResponse schema matching frontend Trip interface
        """
        return TripResponse(
            id=str(trip.id),
            name=trip.name,
            destination=trip.destination,
            startDate=trip.start_date,
            endDate=trip.end_date,
            status=str(trip.status),
            travelers=[
                TripMapper._traveler_to_response(t) for t in trip.travelers
            ],
            flights=[
                TripMapper._flight_to_response(f) for f in trip.flights
            ],
            accommodations=[
                TripMapper._accommodation_to_response(a) 
                for a in trip.accommodations
            ],
            activities=[
                TripMapper._activity_to_response(a) for a in trip.activities
            ],
            budget=TripMapper._budget_to_response(trip.budget) if trip.budget 
                   else BudgetResponse(total=0, spent=0, categories=[])
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
            status=TripStatus.from_string(request.status or "planning"),
            travelers=[],
            flights=[],
            accommodations=[],
            activities=[],
            budget=Budget(
                total=Money(0, "USD"),
                spent=Money(0, "USD"),
                categories=[]
            ),
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
        
        trip.updated_at = date_type.today()
        return trip
    
    # Helper methods for nested objects
    
    @staticmethod
    def _traveler_to_response(traveler: Traveler) -> TravelerResponse:
        """Convert Traveler entity to response matching frontend"""
        return TravelerResponse(
            id=traveler.id,
            name=traveler.name,
            email=traveler.email,
            role=traveler.role,
            avatar=traveler.avatar or ""
        )
    
    @staticmethod
    def _flight_to_response(flight: Flight) -> FlightResponse:
        """Convert Flight entity to response matching frontend"""
        return FlightResponse(
            id=flight.id,
            airline=flight.airline,
            flightNumber=flight.flight_number,
            departure=FlightLocationResponse(
                airport=flight.departure_airport.code,
                city=flight.departure_city,
                time=flight.departure_time
            ),
            arrival=FlightLocationResponse(
                airport=flight.arrival_airport.code,
                city=flight.arrival_city,
                time=flight.arrival_time
            ),
            duration=flight.duration,
            stops=flight.stops,
            price=float(flight.price.amount),
            cabinClass=flight.cabin_class,
            status=flight.status
        )
    
    @staticmethod
    def _accommodation_to_response(
        accommodation: Accommodation
    ) -> AccommodationResponse:
        """Convert Accommodation entity to response matching frontend"""
        return AccommodationResponse(
            id=accommodation.id,
            name=accommodation.name,
            type=accommodation.type,
            image=accommodation.image or "",
            checkIn=accommodation.check_in,
            checkOut=accommodation.check_out,
            pricePerNight=float(accommodation.price_per_night.amount),
            totalPrice=float(accommodation.total_price.amount),
            rating=accommodation.rating,
            amenities=accommodation.amenities,
            status=accommodation.status
        )
    
    @staticmethod
    def _activity_to_response(activity: Activity) -> ActivityResponse:
        """Convert Activity entity to response matching frontend"""
        return ActivityResponse(
            id=activity.id,
            name=activity.name,
            date=activity.date,
            cost=float(activity.cost.amount),
            status=activity.status,
            category=activity.category,
            description=activity.description or ""
        )
    
    @staticmethod
    def _budget_to_response(budget: Budget) -> BudgetResponse:
        """Convert Budget value object to response matching frontend"""
        return BudgetResponse(
            total=float(budget.total.amount),
            spent=float(budget.spent.amount),
            categories=[
                BudgetCategoryResponse(
                    category=cat.category,
                    planned=float(cat.planned.amount),
                    spent=float(cat.spent.amount)
                )
                for cat in budget.categories
            ]
        )
