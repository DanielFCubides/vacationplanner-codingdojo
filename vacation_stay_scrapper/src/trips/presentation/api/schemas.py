"""
Trip API Schemas

Pydantic models for FastAPI request/response validation.
Matches frontend Models.ts interfaces exactly.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List, Optional, Literal


# ============================================================================
# REQUEST SCHEMAS FOR NESTED OBJECTS
# ============================================================================

class TravelerCreateRequest(BaseModel):
    """Request schema for creating a traveler"""
    name: str = Field(..., min_length=1)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$', examples=["user@example.com"])
    role: Literal["owner", "editor", "viewer"] = "viewer"
    avatar: Optional[str] = None
    
    class Config:
        populate_by_name = True


class FlightLocationRequest(BaseModel):
    """Request schema for flight location (departure/arrival)"""
    airport: str = Field(..., min_length=3, max_length=3)  # IATA code
    city: str = Field(..., min_length=1)
    time: datetime


class FlightCreateRequest(BaseModel):
    """Request schema for creating a flight"""
    airline: str = Field(..., min_length=1)
    flight_number: str = Field(..., min_length=1, alias="flightNumber")
    departure: FlightLocationRequest
    arrival: FlightLocationRequest
    duration: str = Field(..., min_length=1)  # e.g., "2h 30m"
    stops: int = Field(0, ge=0)
    price: float = Field(..., gt=0)
    cabin_class: str = Field("Economy", alias="cabinClass")
    status: Literal["confirmed", "pending", "cancelled"] = "pending"
    
    class Config:
        populate_by_name = True


class AccommodationCreateRequest(BaseModel):
    """Request schema for creating an accommodation"""
    name: str = Field(..., min_length=1)
    type: Literal["hotel", "airbnb", "hostel", "resort"]
    image: Optional[str] = None
    check_in: date = Field(..., alias="checkIn")
    check_out: date = Field(..., alias="checkOut")
    price_per_night: float = Field(..., gt=0, alias="pricePerNight")
    total_price: float = Field(..., gt=0, alias="totalPrice")
    rating: float = Field(..., ge=0, le=5)
    amenities: List[str] = Field(default_factory=list)
    status: Literal["confirmed", "pending", "cancelled"] = "pending"
    
    class Config:
        populate_by_name = True


class ActivityCreateRequest(BaseModel):
    """Request schema for creating an activity"""
    name: str = Field(..., min_length=1)
    date: date
    cost: float = Field(..., ge=0)
    status: Literal["booked", "pending", "cancelled"] = "pending"
    category: str = Field(..., min_length=1)
    description: Optional[str] = None


class BudgetCategoryRequest(BaseModel):
    """Request schema for budget category"""
    category: str = Field(..., min_length=1)
    planned: float = Field(..., ge=0)
    spent: float = Field(0, ge=0)


class BudgetRequest(BaseModel):
    """Request schema for budget"""
    total: float = Field(..., ge=0)
    spent: float = Field(0, ge=0)
    categories: List[BudgetCategoryRequest] = Field(default_factory=list)


# ============================================================================
# RESPONSE SCHEMAS (Nested structures)
# ============================================================================

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


# ============================================================================
# MAIN REQUEST SCHEMAS
# ============================================================================

class TripCreateRequest(BaseModel):
    """
    Request schema for creating a trip with all nested objects
    
    Now supports creating a complete trip with flights, accommodations,
    activities, and travelers in a single request.
    """
    # Basic trip info
    name: str = Field(..., min_length=1, max_length=200)
    destination: str = Field(..., min_length=1, max_length=200)
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    status: Optional[Literal["planning", "confirmed", "completed"]] = "planning"
    
    # Nested objects (optional, defaults to empty lists)
    travelers: Optional[List[TravelerCreateRequest]] = Field(default_factory=list)
    flights: Optional[List[FlightCreateRequest]] = Field(default_factory=list)
    accommodations: Optional[List[AccommodationCreateRequest]] = Field(default_factory=list)
    activities: Optional[List[ActivityCreateRequest]] = Field(default_factory=list)
    budget: Optional[BudgetRequest] = None
    
    class Config:
        populate_by_name = True


class TripUpdateRequest(BaseModel):
    """Request schema for updating a trip"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    destination: Optional[str] = None
    start_date: Optional[date] = Field(None, alias="startDate")
    end_date: Optional[date] = Field(None, alias="endDate")
    status: Optional[Literal["planning", "confirmed", "completed"]] = None
    
    # Nested objects for update (optional)
    travelers: Optional[List[TravelerCreateRequest]] = None
    flights: Optional[List[FlightCreateRequest]] = None
    accommodations: Optional[List[AccommodationCreateRequest]] = None
    activities: Optional[List[ActivityCreateRequest]] = None
    budget: Optional[BudgetRequest] = None
    
    class Config:
        populate_by_name = True


# ============================================================================
# LIST RESPONSES
# ============================================================================

class TripListResponse(BaseModel):
    """Response schema for trip list"""
    trips: List[TripResponse]
    total: int


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    details: Optional[dict] = None
