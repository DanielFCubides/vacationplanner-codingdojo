"""
Trip ID Value Object

Represents a unique identifier for a trip.
"""
from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class TripId:
    """
    Immutable Trip ID
    
    Value object representing a unique trip identifier.
    """
    value: str
    
    @classmethod
    def generate(cls) -> "TripId":
        """Generate a new unique trip ID"""
        return cls(value=str(uuid4()))
    
    @classmethod
    def from_string(cls, id_string: str) -> "TripId":
        """
        Create TripId from string
        
        Args:
            id_string: String representation of ID
            
        Returns:
            TripId instance
        """
        return cls(value=id_string)
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"TripId(value='{self.value}')"
