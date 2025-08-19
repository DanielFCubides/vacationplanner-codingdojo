"""
Stay domain models.

Business entities for accommodation search and booking.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Set
from uuid import UUID, uuid4


class StayType(Enum):
    """Type of accommodation."""
    HOTEL = "hotel"
    APARTMENT = "apartment"
    HOUSE = "house"
    RESORT = "resort"
    HOSTEL = "hostel"
    VILLA = "villa"


class Amenities(Enum):
    """Available amenities."""
    WIFI = "wifi"
    PARKING = "parking"
    POOL = "pool"
    GYM = "gym"
    BREAKFAST = "breakfast"
    PET_FRIENDLY = "pet_friendly"
    AIR_CONDITIONING = "air_conditioning"
    KITCHEN = "kitchen"


@dataclass
class Stay:
    """
    Stay accommodation entity.
    
    Represents an available accommodation option.
    """
    id: UUID
    name: str
    stay_type: StayType
    location: str
    price_per_night: Decimal
    max_guests: int
    
    # Optional features
    amenities: Set[Amenities] = None
    rating: Optional[float] = None
    description: str = ""
    
    def __post_init__(self):
        """Initialize amenities if None."""
        if self.amenities is None:
            self.amenities = set()
    
    @classmethod
    def create_new(
        cls,
        name: str,
        stay_type: StayType,
        location: str,
        price_per_night: Decimal,
        max_guests: int
    ) -> 'Stay':
        """Create a new stay."""
        return cls(
            id=uuid4(),
            name=name,
            stay_type=stay_type,
            location=location,
            price_per_night=price_per_night,
            max_guests=max_guests
        )
    
    def add_amenity(self, amenity: Amenities) -> None:
        """Add an amenity to the stay."""
        self.amenities.add(amenity)
    
    def has_amenity(self, amenity: Amenities) -> bool:
        """Check if stay has specific amenity."""
        return amenity in self.amenities
    
    def can_accommodate(self, guests: int) -> bool:
        """Check if stay can accommodate number of guests."""
        return guests <= self.max_guests
    
    def calculate_total_price(self, nights: int) -> Decimal:
        """Calculate total price for stay duration."""
        return self.price_per_night * nights
