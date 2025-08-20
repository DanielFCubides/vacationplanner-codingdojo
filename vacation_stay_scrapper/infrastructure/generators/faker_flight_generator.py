"""
Faker-based flight data generator.

Generates realistic fake flight information for development and testing.
"""
import random
from datetime import datetime, timedelta, date, time
from decimal import Decimal
from typing import List, Optional, Dict

from faker import Faker

from domain.models.vacation_plan import VacationPlan


class FlightInfo:
    """
    Simple flight information model for faker generation.
    
    This is a simplified version for generating fake flight data.
    """
    def __init__(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date] = None,
        passengers: int = 1,
        price: Optional[Decimal] = None
    ):
        self.origin = origin
        self.destination = destination
        self.departure_date = departure_date
        self.return_date = return_date
        self.passengers = passengers
        self.price = price


class FakerFlightGenerator:
    """
    Faker-based flight data generator.
    
    Generates realistic flight information with pricing and schedules.
    """
    
    def __init__(self, locale: str = "en_US"):
        """
        Initialize the flight generator.
        
        Args:
            locale: Faker locale for generating localized data
        """
        self.fake = Faker(locale)
        
        # Common airport codes and cities
        self._airports = {
            'BOG': 'Bogotá',
            'MIA': 'Miami', 
            'NYC': 'New York',
            'LAX': 'Los Angeles',
            'LHR': 'London',
            'CDG': 'Paris',
            'MAD': 'Madrid',
            'BCN': 'Barcelona',
            'FCO': 'Rome',
            'AMS': 'Amsterdam',
            'FRA': 'Frankfurt',
            'SYD': 'Sydney',
            'NRT': 'Tokyo',
            'DXB': 'Dubai',
            'SIN': 'Singapore'
        }
        
        # Airlines for realistic flight generation
        self._airlines = [
            'Avianca', 'LATAM', 'American Airlines', 'Delta', 'United',
            'British Airways', 'Air France', 'Lufthansa', 'KLM', 'Iberia'
        ]
        
        # Typical flight durations between regions (in hours)
        self._flight_durations = {
            'domestic': (1, 6),
            'continental': (2, 8),
            'intercontinental': (8, 16)
        }
    
    def generate_flight_info(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date] = None,
        passengers: int = 1
    ) -> FlightInfo:
        """
        Generate fake flight information.
        
        Args:
            origin: Origin airport code or city
            destination: Destination airport code or city
            departure_date: Departure date
            return_date: Optional return date
            passengers: Number of passengers
            
        Returns:
            Generated FlightInfo
        """
        # Calculate base price
        base_price = self._calculate_flight_price(origin, destination)
        total_price = base_price * passengers
        
        return FlightInfo(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            passengers=passengers,
            price=total_price
        )
    
    def generate_detailed_flight_data(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date] = None,
        passengers: int = 1
    ) -> Dict:
        """
        Generate detailed flight data in the format expected by the flight service.
        
        Args:
            origin: Origin airport code or city
            destination: Destination airport code or city
            departure_date: Departure date
            return_date: Optional return date
            passengers: Number of passengers
            
        Returns:
            Dictionary with detailed flight information
        """
        # Generate outbound flight
        outbound = self._generate_flight_details(origin, destination, departure_date)
        
        result = {
            "flights": [{
                "outbound": outbound
            }]
        }
        
        # Generate return flight if return date provided
        if return_date:
            return_flight = self._generate_flight_details(destination, origin, return_date)
            result["flights"][0]["return_in"] = return_flight
        else:
            result["flights"][0]["return_in"] = []
        
        return result
    
    def generate_multiple_flight_options(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date] = None,
        passengers: int = 1,
        options_count: int = 3
    ) -> Dict:
        """
        Generate multiple flight options for variety.
        
        Args:
            origin: Origin airport code or city
            destination: Destination airport code or city
            departure_date: Departure date
            return_date: Optional return date
            passengers: Number of passengers
            options_count: Number of flight options to generate
            
        Returns:
            Dictionary with multiple flight options
        """
        flights = []
        
        for _ in range(options_count):
            flight_option = {
                "outbound": self._generate_flight_details(origin, destination, departure_date)
            }
            
            if return_date:
                flight_option["return_in"] = self._generate_flight_details(
                    destination, origin, return_date
                )
            else:
                flight_option["return_in"] = []
            
            flights.append(flight_option)
        
        return {"flights": flights}
    
    def _generate_flight_details(self, origin: str, destination: str, flight_date: date) -> Dict:
        """Generate detailed flight information for a single flight."""
        # Generate realistic departure time (6 AM to 11 PM)
        departure_hour = random.randint(6, 23)
        departure_minute = random.choice([0, 15, 30, 45])
        departure_time = time(departure_hour, departure_minute)
        
        # Calculate flight duration based on route
        duration_hours = self._estimate_flight_duration(origin, destination)
        duration_minutes = random.randint(0, 59)
        flight_duration = timedelta(hours=duration_hours, minutes=duration_minutes)
        
        # Calculate landing time
        departure_datetime = datetime.combine(flight_date, departure_time)
        landing_datetime = departure_datetime + flight_duration
        landing_time = landing_datetime.time()
        
        # Generate price
        base_price = self._calculate_flight_price(origin, destination)
        # Add some price variation
        price_variation = random.uniform(0.8, 1.3)
        final_price = base_price * Decimal(str(price_variation))
        
        return {
            "date": flight_date.strftime("%Y-%m-%d"),
            "departure_time": departure_time.strftime("%H:%M"),
            "landing_time": landing_time.strftime("%H:%M"),
            "price": str(round(final_price, 2)),
            "flight_time": str(int(flight_duration.total_seconds())),
            "airline": self.fake.random_element(self._airlines),
            "flight_number": f"{self.fake.random_element(['AV', 'LA', 'AA', 'DL', 'UA'])}{random.randint(100, 9999)}"
        }
    
    def _calculate_flight_price(self, origin: str, destination: str) -> Decimal:
        """Calculate realistic flight price based on route."""
        # Base prices by route type
        base_prices = {
            'domestic': 150,
            'continental': 400, 
            'intercontinental': 800
        }
        
        # Determine route type (simplified logic)
        route_type = self._determine_route_type(origin, destination)
        base_price = base_prices[route_type]
        
        # Add randomness for market conditions
        price_factor = random.uniform(0.7, 1.5)
        final_price = base_price * price_factor
        
        return Decimal(str(round(final_price, 2)))
    
    def _estimate_flight_duration(self, origin: str, destination: str) -> int:
        """Estimate flight duration in hours."""
        route_type = self._determine_route_type(origin, destination)
        min_hours, max_hours = self._flight_durations[route_type]
        return random.randint(min_hours, max_hours)
    
    def _determine_route_type(self, origin: str, destination: str) -> str:
        """Determine if route is domestic, continental, or intercontinental."""
        # Simplified logic - in reality would use geographic data
        origin_region = self._get_region(origin)
        dest_region = self._get_region(destination)
        
        if origin_region == dest_region:
            return 'domestic'
        elif self._are_same_continent(origin_region, dest_region):
            return 'continental'
        else:
            return 'intercontinental'
    
    def _get_region(self, location: str) -> str:
        """Get region for a location (simplified)."""
        # Very simplified regional mapping
        south_america = ['BOG', 'Bogotá', 'Lima', 'Santiago']
        north_america = ['MIA', 'NYC', 'LAX', 'Miami', 'New York', 'Los Angeles']
        europe = ['LHR', 'CDG', 'MAD', 'London', 'Paris', 'Madrid']
        
        location_upper = location.upper()
        if any(loc in location_upper for loc in south_america):
            return 'south_america'
        elif any(loc in location_upper for loc in north_america):
            return 'north_america'
        elif any(loc in location_upper for loc in europe):
            return 'europe'
        else:
            return 'other'
    
    def _are_same_continent(self, region1: str, region2: str) -> bool:
        """Check if two regions are on the same continent."""
        continents = {
            'americas': ['north_america', 'south_america'],
            'europe': ['europe'],
            'other': ['other']
        }
        
        for continent, regions in continents.items():
            if region1 in regions and region2 in regions:
                return True
        return False
