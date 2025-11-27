"""
Stay domain models.

Business entities for accommodation search and booking.
"""
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Set
from uuid import UUID, uuid4


class StayType(Enum):
    """Type of accommodation."""
    HOTEL = "hotel"
    APARTMENT = "apartment"
    HOUSE = "house"
    RESORT = "resort"
    HOSTEL = "hostel"
    BED_AND_BREAKFAST = "bed_and_breakfast"
    VILLA = "villa"
    CABIN = "cabin"


class Amenities(Enum):
    """Available amenities in accommodations."""
    WIFI = "wifi"
    PARKING = "parking"
    POOL = "pool"
    GYM = "gym"
    BREAKFAST = "breakfast"
    PET_FRIENDLY = "pet_friendly"
    AIR_CONDITIONING = "air_conditioning"
    KITCHEN = "kitchen"
    LAUNDRY = "laundry"
    BALCONY = "balcony"


@dataclass
class Stay:
    """
    Stay accommodation entity.
    
    Represents an available accommodation option with its features and pricing.
    """
    id: UUID
    name: str
    stay_type: StayType
    location: str
    price_per_night: Decimal
    max_guests: int
    
    # Optional features
    amenities: Set[Amenities] = field(default_factory=set)
    rating: float = 0.0
    description: str = ""
    
    @classmethod
    def create_new(
        cls,
        name: str,
        stay_type: StayType,
        location: str,
        price_per_night: Decimal,
        max_guests: int
    ) -> 'Stay':
        """
        Create a new stay accommodation.
        
        Args:
            name: Name of the accommodation
            stay_type: Type of accommodation
            location: Location of the stay
            price_per_night: Price per night
            max_guests: Maximum number of guests
            
        Returns:
            New Stay instance
        """
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
    
    def remove_amenity(self, amenity: Amenities) -> None:
        """Remove an amenity from the stay."""
        self.amenities.discard(amenity)
    
    def has_amenity(self, amenity: Amenities) -> bool:
        """Check if stay has a specific amenity."""
        return amenity in self.amenities
    
    def can_accommodate(self, guests: int) -> bool:
        """Check if stay can accommodate the number of guests."""
        return guests <= self.max_guests
    
    def calculate_total_price(self, nights: int) -> Decimal:
        """Calculate total price for the given number of nights."""
        if nights <= 0:
            return Decimal('0')
        return self.price_per_night * nights
