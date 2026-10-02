"""
Application Settings and Configuration

Centralized configuration for the application.
"""
import os
from typing import Optional
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings
from constants import get_secret


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
    
    # Database
    database_host: str = os.environ.get('DATABASE_HOST', 'localhost')
    database_user: str = os.environ.get('DATABASE_USER', 'vacation')
    database_name: str = os.environ.get('DATABASE_NAME', 'vacation_planner')
    database_password: str = get_secret('postgres_password', 'vacation')
    database_echo: bool = False

    # CORS
    cors_origins: list[str] = ["*"]  # Configure per environment
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def database_url(self) -> str:
        password = quote_plus(self.database_password)
        return (
            f"postgresql+asyncpg://{self.database_user}:{password}@"
            f"{self.database_host}:5432/{self.database_name}"
        )


# Global settings instance
settings = Settings()
