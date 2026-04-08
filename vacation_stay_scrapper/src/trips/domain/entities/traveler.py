"""
Traveler Entity

Represents a person traveling on the trip.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Traveler:
    """
    Traveler entity
    
    Represents a person participating in the trip.
    """
    id: str
    name: str
    email: str
    role: str = "viewer"  # owner, editor, viewer
    avatar: Optional[str] = None
    
    def __post_init__(self):
        """Validate traveler data"""
        if not self.name or not self.name.strip():
            raise ValueError("Traveler name cannot be empty")
        if not self.email or "@" not in self.email:
            raise ValueError("Valid email is required")
        if self.role not in ["owner", "editor", "viewer"]:
            raise ValueError(f"Invalid role: {self.role}")
    
    def is_owner(self) -> bool:
        """Check if traveler is the trip owner"""
        return self.role == "owner"
    
    def can_edit(self) -> bool:
        """Check if traveler can edit the trip"""
        return self.role in ["owner", "editor"]
    
    def __str__(self) -> str:
        return f"{self.name} ({self.email})"
