"""
Data sources configuration.

Configuration for external services and data generation settings.
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DataSourceConfig:
    """
    Configuration for data sources and external services.
    
    Manages URLs, settings, and parameters for both real and fake data sources.
    """
    # External service URLs
    flight_service_url: str = "localhost:8001"
    
    # Storage configuration
    vacation_storage: str = "memory"  # memory, file, database
    vacation_file_path: str = "/tmp/vacation_plans.json"
    
    # Faker configuration
    faker_locale: str = "en_US"
    stays_per_search: int = 10
    flights_per_search: int = 5
    
    # Cache settings
    cache_ttl_seconds: int = 300  # 5 minutes
    max_cache_size: int = 1000
    
    @classmethod
    def from_environment(cls) -> 'DataSourceConfig':
        """
        Create data source configuration from environment variables.
        
        Returns:
            DataSourceConfig instance configured from environment
        """
        return cls(
            flight_service_url=os.getenv('FLIGHT_SERVICE_URL', 'localhost:8001'),
            vacation_storage=os.getenv('VACATION_STORAGE', 'memory'),
            vacation_file_path=os.getenv('VACATION_FILE_PATH', '/tmp/vacation_plans.json'),
            faker_locale=os.getenv('FAKER_LOCALE', 'en_US'),
            stays_per_search=int(os.getenv('STAYS_PER_SEARCH', '10')),
            flights_per_search=int(os.getenv('FLIGHTS_PER_SEARCH', '5')),
            cache_ttl_seconds=int(os.getenv('CACHE_TTL_SECONDS', '300')),
            max_cache_size=int(os.getenv('MAX_CACHE_SIZE', '1000'))
        )
    
    def get_flight_service_url(self) -> str:
        """Get the complete flight service URL."""
        if not self.flight_service_url.startswith(('http://', 'https://')):
            return f"http://{self.flight_service_url}"
        return self.flight_service_url
    
    def is_file_storage(self) -> bool:
        """Check if file-based storage is configured."""
        return self.vacation_storage == "file"
    
    def is_memory_storage(self) -> bool:
        """Check if memory-based storage is configured."""
        return self.vacation_storage == "memory"


@dataclass
class AppConfig:
    """
    Main application configuration.
    
    Combines feature flags and data source configuration.
    """
    feature_flags: 'FeatureFlags'
    data_sources: DataSourceConfig
    
    # Application metadata
    app_name: str = "Vacation Stay Scrapper"
    app_version: str = "1.0.0"
    debug_mode: bool = False
    
    @classmethod
    def load(cls) -> 'AppConfig':
        """
        Load complete application configuration.
        
        Returns:
            AppConfig instance with all configuration loaded
        """
        from config.feature_flags import FeatureFlags
        
        return cls(
            feature_flags=FeatureFlags.from_environment(),
            data_sources=DataSourceConfig.from_environment(),
            debug_mode=os.getenv('DEBUG', 'false').lower() == 'true'
        )
    
    def should_use_fake_data(self, data_type: str) -> bool:
        """
        Determine if fake data should be used for a specific data type.
        
        Args:
            data_type: Type of data ('flights' or 'stays')
            
        Returns:
            True if fake data should be used
        """
        if data_type == 'flights':
            return self.feature_flags.use_fake_flights
        elif data_type == 'stays':
            return self.feature_flags.use_fake_stays
        else:
            return False
