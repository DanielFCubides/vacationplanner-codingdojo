"""
Faker-based stay data generator.

Generates realistic fake accommodation data for development and testing.
"""
import random
from decimal import Decimal
from typing import List, Optional

from faker import Faker

from config.config_loader import get_app_config
from domain.models.stay import Stay, StayType, Amenities
from domain.services.data_generator_service import DataGeneratorService


class FakerStayGenerator:
    """
    Faker-based stay data generator.
    
    Generates realistic accommodation data with configurable locale and variety.
    """
    
    def __init__(self, locale: str = "en_US"):
        """
        Initialize the stay generator.
        
        Args:
            locale: Faker locale for generating localized data
        """
        self.fake = Faker(locale)
        self._amenities_list = list(Amenities)
        self._stay_types = list(StayType)
        
        # Common location patterns
        self._location_templates = [
            "{city} Downtown",
            "{city} Beach",
            "{city} Historic District", 
            "{city} City Center",
            "{city} Waterfront",
            "Old Town {city}",
            "{city} Marina",
            "{city} Heights"
        ]
        
        # Stay name patterns by type
        self._name_patterns = {
            StayType.HOTEL: [
                "{adjective} {city} Hotel",
                "Hotel {name}",
                "{city} {adjective} Hotel",
                "The {adjective} Hotel"
            ],
            StayType.RESORT: [
                "{adjective} {city} Resort",
                "{city} {adjective} Resort & Spa",
                "The {adjective} Resort",
                "{name} Resort"
            ],
            StayType.APARTMENT: [
                "{adjective} {city} Apartment",
                "{city} {adjective} Suites",
                "Modern {city} Flat",
                "{adjective} City Apartment"
            ],
            StayType.HOUSE: [
                "{adjective} {city} House",
                "Cozy {city} Home",
                "{adjective} Family House",
                "Beautiful {city} Villa"
            ],
            StayType.HOSTEL: [
                "{city} Backpackers Hostel",
                "{adjective} Hostel {city}",
                "Budget {city} Hostel",
                "Travelers {city} Hostel"
            ],
            StayType.VILLA: [
                "{adjective} {city} Villa",
                "Luxury {city} Villa",
                "Private {city} Villa",
                "{name} Villa"
            ]
        }
    
    def generate_stay(
        self, 
        location: Optional[str] = None,
        stay_type: Optional[StayType] = None
    ) -> Stay:
        """
        Generate a single fake stay.
        
        Args:
            location: Optional specific location, otherwise random
            stay_type: Optional specific stay type, otherwise random
            
        Returns:
            Generated Stay instance
        """
        # Generate stay type
        if stay_type is None:
            stay_type = self.fake.random_element(self._stay_types)
        
        # Generate location
        if location is None:
            city = self.fake.city()
            location = self.fake.random_element(self._location_templates).format(city=city)
        
        # Generate stay name
        name = self._generate_stay_name(stay_type, location)
        
        # Generate pricing (varies by stay type)
        price_per_night = self._generate_price(stay_type)
        
        # Generate capacity
        max_guests = self._generate_capacity(stay_type)
        
        # Create the stay
        stay = Stay.create_new(
            name=name,
            stay_type=stay_type,
            location=location,
            price_per_night=price_per_night,
            max_guests=max_guests
        )
        
        # Add amenities
        self._add_amenities(stay, stay_type)
        
        # Add rating and description
        stay.rating = round(random.uniform(3.0, 5.0), 1)
        stay.description = self._generate_description(stay_type)
        
        return stay
    
    def generate_stays(
        self,
        location: str,
        count: int = 5,
        stay_type: Optional[StayType] = None
    ) -> List[Stay]:
        """
        Generate multiple fake stays for a location.
        
        Args:
            location: Location for the stays
            count: Number of stays to generate
            stay_type: Optional specific type, otherwise varied
            
        Returns:
            List of generated stays
        """
        stays = []
        
        for _ in range(count):
            # Vary stay types if not specified
            current_type = stay_type or self.fake.random_element(self._stay_types)
            stay = self.generate_stay(location, current_type)
            stays.append(stay)
        
        return stays
    
    def _generate_stay_name(self, stay_type: StayType, location: str) -> str:
        """Generate a realistic stay name based on type and location."""
        patterns = self._name_patterns.get(stay_type, ["{adjective} {city} Place"])
        pattern = self.fake.random_element(patterns)
        
        # Extract city from location if possible
        city = location.split()[0] if ' ' in location else location
        
        return pattern.format(
            adjective=self.fake.random_element([
                'Grand', 'Royal', 'Luxury', 'Premium', 'Modern', 'Classic',
                'Boutique', 'Elegant', 'Charming', 'Stylish', 'Contemporary'
            ]),
            city=city,
            name=self.fake.last_name()
        )
    
    def _generate_price(self, stay_type: StayType) -> Decimal:
        """Generate realistic pricing based on stay type."""
        price_ranges = {
            StayType.HOSTEL: (15, 50),
            StayType.APARTMENT: (80, 200),
            StayType.HOTEL: (100, 300),
            StayType.HOUSE: (120, 250),
            StayType.RESORT: (200, 500),
            StayType.VILLA: (300, 800)
        }
        
        min_price, max_price = price_ranges.get(stay_type, (50, 200))
        price = random.uniform(min_price, max_price)
        return Decimal(str(round(price, 2)))
    
    def _generate_capacity(self, stay_type: StayType) -> int:
        """Generate realistic guest capacity based on stay type."""
        capacity_ranges = {
            StayType.HOSTEL: (1, 4),
            StayType.HOTEL: (1, 4),
            StayType.APARTMENT: (2, 6),
            StayType.HOUSE: (4, 8),
            StayType.RESORT: (2, 6),
            StayType.VILLA: (6, 12)
        }
        
        min_cap, max_cap = capacity_ranges.get(stay_type, (2, 4))
        return random.randint(min_cap, max_cap)
    
    def _add_amenities(self, stay: Stay, stay_type: StayType) -> None:
        """Add realistic amenities based on stay type."""
        # Common amenities for all types
        common_amenities = [Amenities.WIFI]
        
        # Type-specific amenity probabilities
        type_amenities = {
            StayType.HOTEL: [
                (Amenities.AIR_CONDITIONING, 0.9),
                (Amenities.PARKING, 0.7),
                (Amenities.GYM, 0.4),
                (Amenities.BREAKFAST, 0.6)
            ],
            StayType.RESORT: [
                (Amenities.POOL, 0.95),
                (Amenities.GYM, 0.8),
                (Amenities.AIR_CONDITIONING, 0.9),
                (Amenities.PARKING, 0.8),
                (Amenities.BREAKFAST, 0.9)
            ],
            StayType.APARTMENT: [
                (Amenities.KITCHEN, 0.9),
                (Amenities.LAUNDRY, 0.7),
                (Amenities.AIR_CONDITIONING, 0.6),
                (Amenities.PARKING, 0.5)
            ],
            StayType.HOUSE: [
                (Amenities.KITCHEN, 0.95),
                (Amenities.LAUNDRY, 0.8),
                (Amenities.PARKING, 0.9),
                (Amenities.BALCONY, 0.6)
            ],
            StayType.VILLA: [
                (Amenities.POOL, 0.8),
                (Amenities.KITCHEN, 0.9),
                (Amenities.PARKING, 0.95),
                (Amenities.BALCONY, 0.8),
                (Amenities.AIR_CONDITIONING, 0.9)
            ],
            StayType.HOSTEL: [
                (Amenities.LAUNDRY, 0.8),
                (Amenities.KITCHEN, 0.6)
            ]
        }
        
        # Add common amenities
        for amenity in common_amenities:
            stay.add_amenity(amenity)
        
        # Add type-specific amenities based on probability
        for amenity, probability in type_amenities.get(stay_type, []):
            if random.random() < probability:
                stay.add_amenity(amenity)
    
    def _generate_description(self, stay_type: StayType) -> str:
        """Generate a realistic description for the stay."""
        descriptions = {
            StayType.HOTEL: [
                "Experience comfort and convenience in the heart of the city.",
                "Modern accommodations with excellent service and amenities.",
                "Perfect for business travelers and leisure guests alike."
            ],
            StayType.RESORT: [
                "Luxury resort offering world-class amenities and stunning views.",
                "All-inclusive paradise with spa services and recreational activities.",
                "Escape to luxury with exceptional dining and entertainment."
            ],
            StayType.APARTMENT: [
                "Spacious apartment with all the comforts of home.",
                "Modern furnished apartment in a prime location.",
                "Perfect for extended stays with full kitchen facilities."
            ],
            StayType.HOUSE: [
                "Charming house perfect for families and groups.",
                "Comfortable home away from home with private amenities.",
                "Spacious house ideal for longer stays and relaxation."
            ],
            StayType.VILLA: [
                "Exclusive villa offering privacy and luxury amenities.",
                "Stunning private villa with breathtaking views.",
                "Luxurious retreat perfect for special occasions."
            ],
            StayType.HOSTEL: [
                "Budget-friendly accommodation perfect for backpackers.",
                "Social atmosphere with shared facilities and common areas.",
                "Clean, safe, and affordable lodging for travelers."
            ]
        }
        
        return self.fake.random_element(descriptions.get(stay_type, ["Comfortable accommodation."]))
