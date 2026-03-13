"""
Airport Value Object

Represents an airport location.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Airport:
    """
    Immutable Airport representation
    
    Value object representing an airport with code and city.
    """
    code: str  # IATA code (e.g., "JFK", "LAX")
    city: str  # City name (e.g., "New York", "Los Angeles")
    
    def __str__(self) -> str:
        return f"{self.code} ({self.city})"
    
    def __repr__(self) -> str:
        return f"Airport(code='{self.code}', city='{self.city}')"
