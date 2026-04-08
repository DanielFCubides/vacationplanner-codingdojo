"""
Keycloak Client Configuration

Provides configuration settings for Keycloak integration.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class KeycloakConfig:
    """Keycloak configuration settings"""
    
    base_url: str
    realm: str
    client_id: str
    jwks_url: str
    audience: str = "account"
    algorithms: list[str] = None
    
    def __post_init__(self):
        """Set default algorithms if not provided"""
        if self.algorithms is None:
            self.algorithms = ["RS256"]
    
    @classmethod
    def from_env(cls, base_url: str = None, realm: str = None) -> "KeycloakConfig":
        """
        Create configuration from environment or defaults
        
        Args:
            base_url: Keycloak base URL (optional, uses default if not provided)
            realm: Keycloak realm name (optional, uses default if not provided)
            
        Returns:
            KeycloakConfig instance
        """
        # Use provided values or defaults
        base_url = base_url or "https://keycloack.dfcubidesc.com"
        realm = realm or "habit-tracker"
        
        # Construct JWKS URL
        jwks_url = f"{base_url}/realms/{realm}/protocol/openid-connect/certs"
        
        # Construct issuer URL
        issuer = f"{base_url}/realms/{realm}"
        
        return cls(
            base_url=base_url,
            realm=realm,
            client_id="habit-tracker-frontend",  # Can be made configurable
            jwks_url=jwks_url,
            audience="account",
            algorithms=["RS256"]
        )
