"""
Application Settings and Configuration

Centralized configuration for the application.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Application
    app_name: str = "Vacation Planner API"
    debug: bool = False
    
    # Circuit Breaker
    circuit_breaker_min_delay: int = int(
        os.environ.get('MIN_DELAY_ATTEMPT', 60)
    )
    circuit_breaker_min_failures: int = int(
        os.environ.get('MIN_FAILURE_ATTEMPTS', 3)
    )
    
    # Keycloak
    keycloak_base_url: str = os.environ.get(
        'KEYCLOAK_BASE_URL',
        'https://keycloack.dfcubidesc.com'
    )
    keycloak_realm: str = os.environ.get(
        'KEYCLOAK_REALM',
        'habit-tracker'
    )
    keycloak_client_id: str = os.environ.get(
        'KEYCLOAK_CLIENT_ID',
        'habit-tracker-frontend'
    )
    
    # Logging
    log_level: str = os.environ.get('LOG_LEVEL', 'INFO')
    log_file: Optional[str] = os.environ.get('LOG_FILE', None)
    
    # CORS
    cors_origins: list[str] = ["*"]  # Configure per environment
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
