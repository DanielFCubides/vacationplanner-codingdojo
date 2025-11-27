"""
Complete data generator service implementation.

Implements the domain service interface using Faker generators.
"""
from typing import List

from config.config_loader import get_app_config
from domain.models.stay import Stay, StayType
from domain.models.vacation_plan import VacationPlan
from domain.services.data_generator_service import DataGeneratorService
from infrastructure.generators.faker_stay_generator import FakerStayGenerator
from infrastructure.generators.faker_flight_generator import FakerFlightGenerator


class FakerDataGeneratorService(DataGeneratorService):
    """
    Complete data generator service using Faker.
    
    Implements the domain service interface to provide realistic fake data
    for development and testing.
    """
    
    def __init__(self, locale: str = None):
        """
        Initialize the data generator service.
        
        Args:
            locale: Optional locale override, otherwise uses config
        """
        config = get_app_config()
        self.locale = locale or config.data_sources.faker_locale
        
        self.stay_generator = FakerStayGenerator(self.locale)
        self.flight_generator = FakerFlightGenerator(self.locale)
    
    def generate_stays(
        self, 
        location: str, 
        count: int = 5,
        stay_type: StayType = None
    ) -> List[Stay]:
        """
        Generate fake stay data for a location.
        
        Args:
            location: Location for the stays
            count: Number of stays to generate
            stay_type: Optional specific type of stays
            
        Returns:
            List of generated stays
        """
        return self.stay_generator.generate_stays(location, count, stay_type)
    
    def generate_vacation_plan(
        self, 
        title: str, 
        user_id: str = None
    ) -> VacationPlan:
        """
        Generate a fake vacation plan.
        
        Args:
            title: Title for the vacation plan
            user_id: Optional user identifier
            
        Returns:
            Generated vacation plan
        """
        return VacationPlan.create_new(title, user_id)
    
    def generate_flight_data(
        self,
        origin: str,
        destination: str,
        departure_date,
        return_date = None,
        passengers: int = 1,
        multiple_options: bool = True
    ):
        """
        Generate fake flight data.
        
        Args:
            origin: Origin airport/city
            destination: Destination airport/city  
            departure_date: Departure date
            return_date: Optional return date
            passengers: Number of passengers
            multiple_options: Whether to generate multiple flight options
            
        Returns:
            Generated flight data in expected format
        """
        if multiple_options:
            config = get_app_config()
            options_count = config.data_sources.flights_per_search
            return self.flight_generator.generate_multiple_flight_options(
                origin, destination, departure_date, return_date, 
                passengers, options_count
            )
        else:
            return self.flight_generator.generate_detailed_flight_data(
                origin, destination, departure_date, return_date, passengers
            )
    
    def get_locale(self) -> str:
        """Get the current locale being used."""
        return self.locale
    
    def set_locale(self, locale: str) -> None:
        """
        Change the locale for data generation.
        
        Args:
            locale: New locale to use
        """
        self.locale = locale
        self.stay_generator = FakerStayGenerator(locale)
        self.flight_generator = FakerFlightGenerator(locale)


# Factory function for easy access
def create_data_generator() -> FakerDataGeneratorService:
    """
    Create a data generator service instance.
    
    Returns:
        FakerDataGeneratorService configured with app settings
    """
    return FakerDataGeneratorService()
