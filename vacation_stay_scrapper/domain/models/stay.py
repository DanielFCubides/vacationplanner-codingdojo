"""
Stay domain models.

Business entities for accommodation search and booking.
"""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any, Set
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


class AmenityType(Enum):
    """Available amenities."""
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
    SEA_VIEW = "sea_view"
    CITY_VIEW = "city_view"


@dataclass(frozen=True)
class StayId:
    """Value object for stay identification."""
    value: UUID = field(default_factory=uuid4)
    
    def __str__(self) -> str:
        return str(self.value)


@dataclass
class Location:
    """Geographical location information."""
    city: str
    country: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    def __post_init__(self):
        """Validate location data."""
        if not self.city.strip():
            raise ValueError("City cannot be empty")
        if not self.country.strip():
            raise ValueError("Country cannot be empty")
    
    def full_location(self) -> str:
        """Get full location string."""
        if self.address:
            return f"{self.address}, {self.city}, {self.country}"
        return f"{self.city}, {self.country}"


@dataclass
class Pricing:
    """Pricing information for a stay."""
    price_per_night: Decimal
    currency: str = "USD"
    total_price: Optional[Decimal] = None
    taxes_and_fees: Optional[Decimal] = None
    
    def __post_init__(self):
        """Validate pricing data."""
        if self.price_per_night <= 0:
            raise ValueError("Price per night must be positive")
        if not self.currency.strip():
            raise ValueError("Currency cannot be empty")
    
    def calculate_total(self, nights: int) -> Decimal:
        """Calculate total price for given number of nights."""
        base_total = self.price_per_night * nights
        if self.taxes_and_fees:
            return base_total + self.taxes_and_fees
        return base_total


@dataclass
class Stay:
    """
    Stay accommodation entity.
    
    Represents an available accommodation option.
    """
    id: StayId = field(default_factory=StayId)
    name: str = ""
    stay_type: StayType = StayType.HOTEL
    location: Optional[Location] = None
    pricing: Optional[Pricing] = None
    
    # Capacity and features
    max_guests: int = 2
    bedrooms: int = 1
    bathrooms: int = 1
    
    # Amenities and features
    amenities: Set[AmenityType] = field(default_factory=set)
    description: str = ""
    
    # Ratings and reviews
    rating: Optional[float] = None
    review_count: int = 0
    
    # Availability
    available_from: Optional[date] = None
    available_to: Optional[date] = None
    
    # Booking information
    booking_url: Optional[str] = None
    host_name: Optional[str] = None
    
    def __post_init__(self):
        """Validate stay data."""
        if not self.name.strip():
            raise ValueError("Stay name cannot be empty")
        if self.max_guests < 1:
            raise ValueError("Max guests must be at least 1")
        if self.bedrooms < 0:
            raise ValueError("Bedrooms cannot be negative")
        if self.bathrooms < 0:
            raise ValueError("Bathrooms cannot be negative")
        if self.rating is not None and not (0 <= self.rating <= 5):
            raise ValueError("Rating must be between 0 and 5")
        if self.review_count < 0:
            raise ValueError("Review count cannot be negative")
    
    def add_amenity(self, amenity: AmenityType) -> None:
        """Add an amenity to the stay."""
        self.amenities.add(amenity)
    
    def remove_amenity(self, amenity: AmenityType) -> None:
        """Remove an amenity from the stay."""
        self.amenities.discard(amenity)
    
    def has_amenity(self, amenity: AmenityType) -> bool:
        """Check if stay has specific amenity."""
        return amenity in self.amenities
    
    def is_available_for_dates(self, check_in: date, check_out: date) -> bool:
        """Check if stay is available for given dates."""
        if not self.available_from or not self.available_to:
            return True  # Assume available if no restrictions
        
        return (self.available_from <= check_in and 
                check_out <= self.available_to)
    
    def can_accommodate(self, guests: int) -> bool:
        """Check if stay can accommodate number of guests."""
        return guests <= self.max_guests
    
    def calculate_total_price(self, check_in: date, check_out: date) -> Optional[Decimal]:
        """Calculate total price for stay duration."""
        if not self.pricing:
            return None
        
        nights = (check_out - check_in).days
        if nights <= 0:
            return None
            
        return self.pricing.calculate_total(nights)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stay to dictionary for serialization."""
        return {
            'id': str(self.id),
            'name': self.name,
            'stay_type': self.stay_type.value,
            'location': self._location_to_dict(),
            'pricing': self._pricing_to_dict(),
            'max_guests': self.max_guests,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'amenities': [amenity.value for amenity in self.amenities],
            'description': self.description,
            'rating': self.rating,
            'review_count': self.review_count,
            'available_from': self.available_from.isoformat() if self.available_from else None,
            'available_to': self.available_to.isoformat() if self.available_to else None,
            'booking_url': self.booking_url,
            'host_name': self.host_name
        }
    
    def _location_to_dict(self) -> Optional[Dict[str, Any]]:
        """Convert location to dictionary."""
        if not self.location:
            return None
        
        return {
            'city': self.location.city,
            'country': self.location.country,
            'address': self.location.address,
            'latitude': self.location.latitude,
            'longitude': self.location.longitude,
            'full_location': self.location.full_location()
        }
    
    def _pricing_to_dict(self) -> Optional[Dict[str, Any]]:
        """Convert pricing to dictionary."""
        if not self.pricing:
            return None
        
        return {
            'price_per_night': str(self.pricing.price_per_night),
            'currency': self.pricing.currency,
            'total_price': str(self.pricing.total_price) if self.pricing.total_price else None,
            'taxes_and_fees': str(self.pricing.taxes_and_fees) if self.pricing.taxes_and_fees else None
        }


@dataclass
class StaySearchCriteria:
    """
    Search criteria for finding stays.
    
    Contains all parameters needed to search for accommodations.
    """
    location: str
    check_in_date: date
    check_out_date: date
    guests: int = 1
    
    # Optional filters
    stay_types: Optional[List[StayType]] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    min_rating: Optional[float] = None
    required_amenities: Optional[List[AmenityType]] = None
    max_results: int = 20
    
    def __post_init__(self):
        """Validate search criteria."""
        if not self.location.strip():
            raise ValueError("Location cannot be empty")
        if self.guests < 1:
            raise ValueError("Guests must be at least 1")
        if self.check_out_date <= self.check_in_date:
            raise ValueError("Check-out date must be after check-in date")
        if self.min_price is not None and self.min_price < 0:
            raise ValueError("Minimum price cannot be negative")
        if self.max_price is not None and self.max_price < 0:
            raise ValueError("Maximum price cannot be negative")
        if (self.min_price is not None and self.max_price is not None and 
            self.min_price > self.max_price):
            raise ValueError("Minimum price cannot be greater than maximum price")
        if self.min_rating is not None and not (0 <= self.min_rating <= 5):
            raise ValueError("Minimum rating must be between 0 and 5")
        if self.max_results < 1:
            raise ValueError("Max results must be at least 1")
    
    @property
    def nights(self) -> int:
        """Calculate number of nights."""
        return (self.check_out_date - self.check_in_date).days
    
    def matches_stay(self, stay: Stay) -> bool:
        """Check if a stay matches the search criteria."""
        # Check basic availability
        if not stay.is_available_for_dates(self.check_in_date, self.check_out_date):
            return False
        
        if not stay.can_accommodate(self.guests):
            return False
        
        # Check stay type filter
        if self.stay_types and stay.stay_type not in self.stay_types:
            return False
        
        # Check price filters
        if stay.pricing and self.min_price:
            if stay.pricing.price_per_night < self.min_price:
                return False
                
        if stay.pricing and self.max_price:
            if stay.pricing.price_per_night > self.max_price:
                return False
        
        # Check rating filter
        if self.min_rating and stay.rating:
            if stay.rating < self.min_rating:
                return False
        
        # Check required amenities
        if self.required_amenities:
            for amenity in self.required_amenities:
                if not stay.has_amenity(amenity):
                    return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert search criteria to dictionary."""
        return {
            'location': self.location,
            'check_in_date': self.check_in_date.isoformat(),
            'check_out_date': self.check_out_date.isoformat(),
            'guests': self.guests,
            'nights': self.nights,
            'stay_types': [st.value for st in self.stay_types] if self.stay_types else None,
            'min_price': str(self.min_price) if self.min_price else None,
            'max_price': str(self.max_price) if self.max_price else None,
            'min_rating': self.min_rating,
            'required_amenities': [a.value for a in self.required_amenities] if self.required_amenities else None,
            'max_results': self.max_results
        }
