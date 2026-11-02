"""
Application Settings and Configuration

Centralized configuration for the application.
"""
import os
from typing import Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL


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
    
    # Database. Prefer DATABASE_URL when explicitly supplied; otherwise compose
    # the URL from non-secret connection settings and an optional password file.
    database_url: Optional[str] = None
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "vacation"
    postgres_db: str = "vacation_planner"
    postgres_password: Optional[str] = None
    postgres_password_file: Optional[str] = None
    database_echo: bool = False

    # CORS
    cors_origins: list[str] = ["*"]  # Configure per environment
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @model_validator(mode="after")
    def configure_database_url(self):
        if not self.database_url:
            password = self.postgres_password
            password_file = self.postgres_password_file
            if password_file:
                try:
                    with open(password_file, encoding="utf-8") as file:
                        password = file.read().strip()
                except OSError as exc:
                    raise RuntimeError("Unable to read PostgreSQL password file") from exc

            self.database_url = URL.create(
                "postgresql+asyncpg",
                username=self.postgres_user,
                password=password,
                host=self.postgres_host,
                port=self.postgres_port,
                database=self.postgres_db,
            ).render_as_string(hide_password=False)
        return self


# Global settings instance
settings = Settings()
