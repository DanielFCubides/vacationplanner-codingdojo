"""
FastAPI Authentication Dependencies

Provides dependency injection for authentication in FastAPI routes.
"""
from typing import Annotated, Dict, Any
from fastapi import Header, Depends
from .jwt_validator import JWTValidator
from .keycloak_config import KeycloakConfig


# Initialize Keycloak configuration
keycloak_config = KeycloakConfig.from_env()

# Initialize JWT validator
jwt_validator = JWTValidator(
    jwks_url=keycloak_config.jwks_url,
    algorithms=keycloak_config.algorithms,
    audience=keycloak_config.audience,
    issuer=f"{keycloak_config.base_url}/realms/{keycloak_config.realm}"
)


async def get_current_user(
    authorization: Annotated[str, Header()]
) -> Dict[str, Any]:
    """
    FastAPI dependency to validate JWT token and extract user claims
    
    Args:
        authorization: Authorization header from request
        
    Returns:
        Dictionary containing decoded JWT claims (user info)
        
    Raises:
        HTTPException: If token is invalid or expired
        
    Usage:
        @app.get("/protected")
        def protected_route(user: Annotated[dict, Depends(get_current_user)]):
            return {"user_id": user["sub"], "email": user["email"]}
    """
    return jwt_validator.validate_token(authorization)


# Alias for backward compatibility
authenticate = get_current_user
