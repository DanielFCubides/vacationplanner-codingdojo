"""
Trip API Schemas

Pydantic models for FastAPI request/response validation.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List, Optional
from decimal import Decimal


# Request Schemas

class TripCreateRequest(BaseModel):
    """Request schema for creating a trip"""
    name: str = Field(..., min_length=1, max_length=200)
    destination: str = Field(..., min_length=1, max_length=200)
    start_date: date
    end_date: date
    budget: Optional[float] = None


class TripUpdateRequest(BaseModel):
    """Request schema for updating a trip"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    budget: Optional[float] = None


# Response Schemas

class TravelerResponse(BaseModel):
    """Response schema for traveler"""
    id: str
    name: str
    email: str
    role: str
    avatar: Optional[str] = None


class FlightResponse(BaseModel):
    """Response schema for flight"""
    id: str
    airline: str
    flight_number: str
    departure_airport_code: str
    departure_airport_city: str
    arrival_airport_code: str
    arrival_airport_city: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    currency: str
    cabin_class: str
    status: str


class ActivityResponse(BaseModel):
    """Response schema for activity"""
    id: str
    name: str
    date: date
    cost: float
    currency: str
    category: str
    status: str
    description: Optional[str] = None


class TripResponse(BaseModel):
    """Response schema for trip"""
    id: str
    name: str
    destination: str
    start_date: date
    end_date: date
    status: str
    duration_days: int
    budget: Optional[float] = None
    budget_currency: Optional[str] = None
    total_cost: Optional[float] = None
    travelers: List[TravelerResponse] = []
    flights: List[FlightResponse] = []
    activities: List[ActivityResponse] = []
    created_at: Optional[date] = None
    updated_at: Optional[date] = None
    
    class Config:
        from_attributes = True


class TripListResponse(BaseModel):
    """Response schema for trip list"""
    trips: List[TripResponse]
    total: int


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    details: Optional[dict] = None
