"""
Trip Mappers

Convert between domain entities and API schemas.
Ensures compatibility with frontend Models.ts
Supports creating trips with nested objects (flights, accommodations, etc.)
"""
from datetime import date as date_type
from uuid import uuid4

from ...domain.entities.trip import Trip
from ...domain.entities.flight import Flight
from ...domain.entities.traveler import Traveler
from ...domain.entities.activity import Activity
from ...domain.entities.accommodation import Accommodation
from ...domain.value_objects.trip_id import TripId
from ...domain.value_objects.trip_status import TripStatus
from ...domain.value_objects.budget import Budget, BudgetCategory
from ...domain.value_objects.money import Money
from ...domain.value_objects.airport import Airport
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
    BudgetCategoryResponse,
    TravelerCreateRequest,
    FlightCreateRequest,
    AccommodationCreateRequest,
    ActivityCreateRequest,
    BudgetRequest,
    BudgetCategoryRequest
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
        Convert create request to Trip entity with nested objects
        
        Args:
            request: TripCreateRequest schema with optional nested objects
            
        Returns:
            Trip domain entity with all nested objects created
        """
        # Create travelers from request
        travelers = [
            TripMapper._traveler_from_request(t) 
            for t in (request.travelers or [])
        ]
        
        # Create flights from request
        flights = [
            TripMapper._flight_from_request(f) 
            for f in (request.flights or [])
        ]
        
        # Create accommodations from request
        accommodations = [
            TripMapper._accommodation_from_request(a) 
            for a in (request.accommodations or [])
        ]
        
        # Create activities from request
        activities = [
            TripMapper._activity_from_request(a) 
            for a in (request.activities or [])
        ]
        
        # Create budget from request
        budget = TripMapper._budget_from_request(request.budget) if request.budget else Budget(
            total=Money(0, "USD"),
            spent=Money(0, "USD"),
            categories=[]
        )
        
        return Trip(
            id=TripId.generate(),
            name=request.name,
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            status=TripStatus.from_string(request.status or "planning"),
            travelers=travelers,
            flights=flights,
            accommodations=accommodations,
            activities=activities,
            budget=budget,
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
        # Update basic fields
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
        
        # Update nested collections (replace if provided)
        if request.travelers is not None:
            trip.travelers = [
                TripMapper._traveler_from_request(t) for t in request.travelers
            ]
        
        if request.flights is not None:
            trip.flights = [
                TripMapper._flight_from_request(f) for f in request.flights
            ]
        
        if request.accommodations is not None:
            trip.accommodations = [
                TripMapper._accommodation_from_request(a) for a in request.accommodations
            ]
        
        if request.activities is not None:
            trip.activities = [
                TripMapper._activity_from_request(a) for a in request.activities
            ]
        
        if request.budget is not None:
            trip.budget = TripMapper._budget_from_request(request.budget)
        
        trip.updated_at = date_type.today()
        return trip
    
    # ========================================================================
    # RESPONSE CONVERTERS (Domain → API Response)
    # ========================================================================
    
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
    
    # ========================================================================
    # REQUEST CONVERTERS (API Request → Domain Entity)
    # ========================================================================
    
    @staticmethod
    def _traveler_from_request(request: TravelerCreateRequest) -> Traveler:
        """Convert traveler request to Traveler entity"""
        return Traveler(
            id=str(uuid4()),
            name=request.name,
            email=request.email,
            role=request.role,
            avatar=request.avatar
        )
    
    @staticmethod
    def _flight_from_request(request: FlightCreateRequest) -> Flight:
        """Convert flight request to Flight entity"""
        return Flight(
            id=str(uuid4()),
            airline=request.airline,
            flight_number=request.flight_number,
            departure_airport=Airport(
                code=request.departure.airport,
                city=request.departure.city
            ),
            departure_time=request.departure.time,
            arrival_airport=Airport(
                code=request.arrival.airport,
                city=request.arrival.city
            ),
            arrival_time=request.arrival.time,
            duration=request.duration,
            price=Money(request.price, "USD"),
            stops=request.stops,
            cabin_class=request.cabin_class,
            status=request.status
        )
    
    @staticmethod
    def _accommodation_from_request(
        request: AccommodationCreateRequest
    ) -> Accommodation:
        """Convert accommodation request to Accommodation entity"""
        return Accommodation(
            id=str(uuid4()),
            name=request.name,
            type=request.type,
            check_in=request.check_in,
            check_out=request.check_out,
            price_per_night=Money(request.price_per_night, "USD"),
            total_price=Money(request.total_price, "USD"),
            rating=request.rating,
            amenities=request.amenities,
            status=request.status,
            image=request.image
        )
    
    @staticmethod
    def _activity_from_request(request: ActivityCreateRequest) -> Activity:
        """Convert activity request to Activity entity"""
        return Activity(
            id=str(uuid4()),
            name=request.name,
            date=request.date,
            cost=Money(request.cost, "USD"),
            category=request.category,
            status=request.status,
            description=request.description
        )
    
    @staticmethod
    def _budget_from_request(request: BudgetRequest) -> Budget:
        """Convert budget request to Budget value object"""
        categories = [
            BudgetCategory(
                category=cat.category,
                planned=Money(cat.planned, "USD"),
                spent=Money(cat.spent, "USD")
            )
            for cat in request.categories
        ]
        
        return Budget(
            total=Money(request.total, "USD"),
            spent=Money(request.spent, "USD"),
            categories=categories
        )
