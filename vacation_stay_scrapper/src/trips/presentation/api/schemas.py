"""
Trip API Schemas

Pydantic models for FastAPI request/response validation.
Matches frontend Models.ts interfaces exactly.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List, Optional, Literal


# Nested Response Schemas (matching frontend structure)

class AirportResponse(BaseModel):
    """Airport response matching frontend"""
    airport: str  # IATA code
    city: str


class FlightLocationResponse(BaseModel):
    """Flight departure/arrival location"""
    airport: str  # IATA code
    city: str
    time: datetime


class BudgetCategoryResponse(BaseModel):
    """Budget category response"""
    category: str
    planned: float
    spent: float


class BudgetResponse(BaseModel):
    """Budget response matching frontend structure"""
    total: float
    spent: float
    categories: List[BudgetCategoryResponse] = []


class TravelerResponse(BaseModel):
    """Traveler response matching frontend"""
    id: str
    name: str
    email: str
    role: Literal["owner", "editor", "viewer"]
    avatar: str


class FlightResponse(BaseModel):
    """Flight response matching frontend exactly"""
    id: str
    airline: str
    flight_number: str = Field(alias="flightNumber")
    departure: FlightLocationResponse
    arrival: FlightLocationResponse
    duration: str
    stops: int
    price: float
    cabin_class: str = Field(alias="cabinClass")
    status: Literal["confirmed", "pending", "cancelled"]
    
    class Config:
        populate_by_name = True


class AccommodationResponse(BaseModel):
    """Accommodation response matching frontend"""
    id: str
    name: str
    type: Literal["hotel", "airbnb", "hostel", "resort"]
    image: str
    check_in: date = Field(alias="checkIn")
    check_out: date = Field(alias="checkOut")
    price_per_night: float = Field(alias="pricePerNight")
    total_price: float = Field(alias="totalPrice")
    rating: float
    amenities: List[str]
    status: Literal["confirmed", "pending", "cancelled"]
    
    class Config:
        populate_by_name = True


class ActivityResponse(BaseModel):
    """Activity response matching frontend"""
    id: str
    name: str
    date: date
    cost: float
    status: Literal["booked", "pending", "cancelled"]
    category: str
    description: str


class TripResponse(BaseModel):
    """Trip response matching frontend Trip interface exactly"""
    id: str
    name: str
    destination: str
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    status: Literal["planning", "confirmed", "completed"]
    travelers: List[TravelerResponse] = []
    flights: List[FlightResponse] = []
    accommodations: List[AccommodationResponse] = []
    activities: List[ActivityResponse] = []
    budget: BudgetResponse
    
    class Config:
        populate_by_name = True


# Request Schemas

class TripCreateRequest(BaseModel):
    """Request schema for creating a trip"""
    name: str = Field(..., min_length=1, max_length=200)
    destination: str = Field(..., min_length=1, max_length=200)
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    status: Optional[Literal["planning", "confirmed", "completed"]] = "planning"
    
    class Config:
        populate_by_name = True


class TripUpdateRequest(BaseModel):
    """Request schema for updating a trip"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    destination: Optional[str] = None
    start_date: Optional[date] = Field(None, alias="startDate")
    end_date: Optional[date] = Field(None, alias="endDate")
    status: Optional[Literal["planning", "confirmed", "completed"]] = None
    
    class Config:
        populate_by_name = True


# List Responses

class TripListResponse(BaseModel):
    """Response schema for trip list"""
    trips: List[TripResponse]
    total: int


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    details: Optional[dict] = None
