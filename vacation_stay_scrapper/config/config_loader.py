"""
Configuration loader and factory.

Provides a centralized way to load and access application configuration.
"""
from typing import Optional

from config.data_sources import AppConfig


class ConfigurationError(Exception):
    """Raised when configuration is invalid or cannot be loaded."""
    pass


class ConfigLoader:
    """
    Configuration loader and manager.
    
    Provides singleton access to application configuration.
    """
    _instance: Optional[AppConfig] = None
    
    @classmethod
    def get_config(cls) -> AppConfig:
        """
        Get the application configuration.
        
        Loads configuration on first access and caches it.
        
        Returns:
            AppConfig instance
            
        Raises:
            ConfigurationError: If configuration cannot be loaded
        """
        if cls._instance is None:
            try:
                cls._instance = AppConfig.load()
                cls._validate_config(cls._instance)
            except Exception as e:
                raise ConfigurationError(f"Failed to load configuration: {e}")
        
        return cls._instance
    
    @classmethod
    def reload_config(cls) -> AppConfig:
        """
        Force reload of configuration.
        
        Useful for testing or when configuration changes at runtime.
        
        Returns:
            AppConfig instance
        """
        cls._instance = None
        return cls.get_config()
    
    @classmethod
    def _validate_config(cls, config: AppConfig) -> None:
        """
        Validate configuration settings.
        
        Args:
            config: Configuration to validate
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Validate data source config
        if config.data_sources.stays_per_search <= 0:
            raise ConfigurationError("stays_per_search must be positive")
        
        if config.data_sources.flights_per_search <= 0:
            raise ConfigurationError("flights_per_search must be positive")
        
        if config.data_sources.cache_ttl_seconds < 0:
            raise ConfigurationError("cache_ttl_seconds cannot be negative")
        
        # Validate storage configuration
        valid_storage_types = ["memory", "file", "database"]
        if config.data_sources.vacation_storage not in valid_storage_types:
            raise ConfigurationError(
                f"vacation_storage must be one of: {valid_storage_types}"
            )


# Convenience function for easy access
def get_app_config() -> AppConfig:
    """
    Get the application configuration.
    
    Convenience function that delegates to ConfigLoader.
    
    Returns:
        AppConfig instance
    """
    return ConfigLoader.get_config()
