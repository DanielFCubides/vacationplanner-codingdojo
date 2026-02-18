"""
Generator factory for creating data generators based on configuration.

Provides centralized access to data generation services.
"""
from config.config_loader import get_app_config
from domain.services.data_generator_service import DataGeneratorService
from infrastructure.generators.faker_data_generator_service import FakerDataGeneratorService


class GeneratorFactory:
    """
    Factory for creating data generator instances.
    
    Creates generators based on application configuration.
    """
    
    @staticmethod
    def create_data_generator() -> DataGeneratorService:
        """
        Create a data generator service based on configuration.
        
        Returns:
            DataGeneratorService instance
        """
        config = get_app_config()
        return FakerDataGeneratorService(config.data_sources.faker_locale)
    
    @staticmethod
    def create_stay_generator():
        """
        Create a stay generator directly.
        
        Returns:
            FakerStayGenerator instance
        """
        config = get_app_config()
        from infrastructure.generators.faker_stay_generator import FakerStayGenerator
        return FakerStayGenerator(config.data_sources.faker_locale)
    
    @staticmethod
    def create_flight_generator():
        """
        Create a flight generator directly.
        
        Returns:
            FakerFlightGenerator instance
        """
        config = get_app_config()
        from infrastructure.generators.faker_flight_generator import FakerFlightGenerator
        return FakerFlightGenerator(config.data_sources.faker_locale)


# Convenience functions
def get_data_generator() -> DataGeneratorService:
    """
    Get a data generator service instance.
    
    Returns:
        DataGeneratorService instance
    """
    return GeneratorFactory.create_data_generator()


def get_stay_generator():
    """
    Get a stay generator instance.
    
    Returns:
        FakerStayGenerator instance
    """
    return GeneratorFactory.create_stay_generator()


def get_flight_generator():
    """
    Get a flight generator instance.
    
    Returns:
        FakerFlightGenerator instance
    """
    return GeneratorFactory.create_flight_generator()
