"""
Vacation Plan domain models.

Core business entities for vacation planning.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4


class VacationPlanStatus(Enum):
    """Status of a vacation plan."""
    DRAFT = "draft"
    CONFIRMED = "confirmed" 
    CANCELLED = "cancelled"
    COMPLETED = "completed"


@dataclass(frozen=True)
class VacationPlanId:
    """Value object for vacation plan identification."""
    value: UUID = field(default_factory=uuid4)
    
    def __str__(self) -> str:
        return str(self.value)
    
    @classmethod
    def from_string(cls, value: str) -> 'VacationPlanId':
        """Create VacationPlanId from string representation."""
        return cls(UUID(value))


@dataclass
class FlightInfo:
    """Flight information within a vacation plan."""
    origin: str
    destination: str
    departure_date: date
    return_date: Optional[date] = None
    passengers: int = 1
    price: Optional[Decimal] = None
    booking_reference: Optional[str] = None
    
    def __post_init__(self):
        """Validate flight information."""
        if self.passengers < 1:
            raise ValueError("Passengers must be at least 1")
        if self.return_date and self.return_date <= self.departure_date:
            raise ValueError("Return date must be after departure date")


@dataclass  
class StayInfo:
    """Stay information within a vacation plan."""
    location: str
    check_in_date: date
    check_out_date: date
    guests: int = 1
    price_per_night: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    booking_reference: Optional[str] = None
    
    def __post_init__(self):
        """Validate stay information."""
        if self.guests < 1:
            raise ValueError("Guests must be at least 1") 
        if self.check_out_date <= self.check_in_date:
            raise ValueError("Check-out date must be after check-in date")
    
    @property
    def nights(self) -> int:
        """Calculate number of nights."""
        return (self.check_out_date - self.check_in_date).days


@dataclass
class VacationPlan:
    """
    Main vacation plan aggregate root.
    
    Represents a complete vacation plan with flights and accommodations.
    """
    id: VacationPlanId = field(default_factory=VacationPlanId)
    title: str = ""
    description: str = ""
    status: VacationPlanStatus = VacationPlanStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Core vacation components
    flight_info: Optional[FlightInfo] = None
    stay_info: Optional[StayInfo] = None
    
    # Additional metadata
    user_id: Optional[str] = None
    total_budget: Optional[Decimal] = None
    notes: str = ""
    
    def __post_init__(self):
        """Validate vacation plan."""
        if not self.title.strip():
            self.title = f"Vacation Plan {self.id}"
    
    def update_status(self, new_status: VacationPlanStatus) -> None:
        """Update vacation plan status."""
        self.status = new_status
        self.updated_at = datetime.now()
    
    def add_flight_info(self, flight_info: FlightInfo) -> None:
        """Add flight information to the vacation plan."""
        self.flight_info = flight_info
        self.updated_at = datetime.now()
    
    def add_stay_info(self, stay_info: StayInfo) -> None:
        """Add stay information to the vacation plan."""
        self.stay_info = stay_info
        self.updated_at = datetime.now()
    
    def calculate_total_cost(self) -> Optional[Decimal]:
        """Calculate total vacation cost."""
        total = Decimal('0')
        
        if self.flight_info and self.flight_info.price:
            total += self.flight_info.price
            
        if self.stay_info and self.stay_info.total_price:
            total += self.stay_info.total_price
            
        return total if total > 0 else None
    
    def is_complete(self) -> bool:
        """Check if vacation plan has all required information."""
        return (self.flight_info is not None and 
                self.stay_info is not None and
                self.title.strip() != "")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert vacation plan to dictionary for serialization."""
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'flight_info': self._flight_info_to_dict(),
            'stay_info': self._stay_info_to_dict(),
            'user_id': self.user_id,
            'total_budget': str(self.total_budget) if self.total_budget else None,
            'notes': self.notes,
            'total_cost': str(self.calculate_total_cost()) if self.calculate_total_cost() else None,
            'is_complete': self.is_complete()
        }
    
    def _flight_info_to_dict(self) -> Optional[Dict[str, Any]]:
        """Convert flight info to dictionary."""
        if not self.flight_info:
            return None
            
        return {
            'origin': self.flight_info.origin,
            'destination': self.flight_info.destination,
            'departure_date': self.flight_info.departure_date.isoformat(),
            'return_date': self.flight_info.return_date.isoformat() if self.flight_info.return_date else None,
            'passengers': self.flight_info.passengers,
            'price': str(self.flight_info.price) if self.flight_info.price else None,
            'booking_reference': self.flight_info.booking_reference
        }
    
    def _stay_info_to_dict(self) -> Optional[Dict[str, Any]]:
        """Convert stay info to dictionary."""
        if not self.stay_info:
            return None
            
        return {
            'location': self.stay_info.location,
            'check_in_date': self.stay_info.check_in_date.isoformat(),
            'check_out_date': self.stay_info.check_out_date.isoformat(), 
            'guests': self.stay_info.guests,
            'nights': self.stay_info.nights,
            'price_per_night': str(self.stay_info.price_per_night) if self.stay_info.price_per_night else None,
            'total_price': str(self.stay_info.total_price) if self.stay_info.total_price else None,
            'booking_reference': self.stay_info.booking_reference
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VacationPlan':
        """Create vacation plan from dictionary."""
        plan = cls(
            id=VacationPlanId.from_string(data['id']),
            title=data['title'],
            description=data.get('description', ''),
            status=VacationPlanStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            user_id=data.get('user_id'),
            total_budget=Decimal(data['total_budget']) if data.get('total_budget') else None,
            notes=data.get('notes', '')
        )
        
        # Add flight info if present
        if data.get('flight_info'):
            flight_data = data['flight_info']
            plan.flight_info = FlightInfo(
                origin=flight_data['origin'],
                destination=flight_data['destination'],
                departure_date=date.fromisoformat(flight_data['departure_date']),
                return_date=date.fromisoformat(flight_data['return_date']) if flight_data.get('return_date') else None,
                passengers=flight_data['passengers'],
                price=Decimal(flight_data['price']) if flight_data.get('price') else None,
                booking_reference=flight_data.get('booking_reference')
            )
        
        # Add stay info if present
        if data.get('stay_info'):
            stay_data = data['stay_info']
            plan.stay_info = StayInfo(
                location=stay_data['location'],
                check_in_date=date.fromisoformat(stay_data['check_in_date']),
                check_out_date=date.fromisoformat(stay_data['check_out_date']),
                guests=stay_data['guests'],
                price_per_night=Decimal(stay_data['price_per_night']) if stay_data.get('price_per_night') else None,
                total_price=Decimal(stay_data['total_price']) if stay_data.get('total_price') else None,
                booking_reference=stay_data.get('booking_reference')
            )
        
        return plan
