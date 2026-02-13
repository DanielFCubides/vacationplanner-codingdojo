"""
JWT Token Validator

Handles JWT token validation using Keycloak public keys.
"""
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from jwcrypto import jwk
from fastapi import HTTPException
import requests
from typing import Dict, Any


class JWTValidator:
    """Validates JWT tokens against Keycloak"""
    
    def __init__(
        self,
        jwks_url: str,
        algorithms: list[str] = None,
        audience: str = "account",
        issuer: str = None
    ):
        """
        Initialize JWT Validator
        
        Args:
            jwks_url: URL to Keycloak JWKS endpoint
            algorithms: List of allowed algorithms (default: ["RS256"])
            audience: Expected audience claim
            issuer: Expected issuer claim
        """
        self.jwks_url = jwks_url
        self.algorithms = algorithms or ["RS256"]
        self.audience = audience
        self.issuer = issuer
        self._public_key_cache = None
    
    def validate_token(self, authorization: str) -> Dict[str, Any]:
        """
        Validate JWT token from Authorization header
        
        Args:
            authorization: Authorization header value (e.g., "Bearer <token>")
            
        Returns:
            Decoded token claims as dictionary
            
        Raises:
            HTTPException: If token is invalid, expired, or malformed
        """
        # Validate Authorization header format
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Invalid Token - must start with 'Bearer '"
            )
        
        # Extract token
        token = authorization[7:]  # Remove "Bearer " prefix
        if not token:
            raise HTTPException(
                status_code=401,
                detail="No token provided"
            )
        
        try:
            # Get public key from Keycloak
            public_key_pem = self._get_public_key()
            
            # Decode and validate token
            decoded = jwt.decode(
                token,
                public_key_pem,
                algorithms=self.algorithms,
                audience=self.audience,
                issuer=self.issuer
            )
            
            return decoded
            
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Unauthorized: {str(e)}"
            )
    
    def _get_public_key(self) -> bytes:
        """
        Fetch public key from Keycloak JWKS endpoint
        
        Returns:
            Public key in PEM format
            
        Raises:
            HTTPException: If JWKS endpoint is unavailable or returns no keys
        """
        # Use cached key if available
        if self._public_key_cache:
            return self._public_key_cache
        
        try:
            response = requests.get(self.jwks_url)
            response.raise_for_status()
            
            jwks_data = response.json()
            
            # Validate response contains keys
            if "keys" not in jwks_data or len(jwks_data["keys"]) == 0:
                raise HTTPException(
                    status_code=500,
                    detail="Keycloak JWKS endpoint returned no keys"
                )
            
            # Get first key (typically the active signing key)
            public_key_jwk = jwks_data["keys"][0]
            
            # Convert JWK to PEM format
            public_key = jwk.JWK(**public_key_jwk)
            public_key_pem = public_key.export_to_pem(private_key=False)
            
            # Cache the key
            self._public_key_cache = public_key_pem
            
            return public_key_pem
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch public key from Keycloak: {str(e)}"
            )
