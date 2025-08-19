"""
Vacation Plan domain models.

Core business entities for vacation planning.
"""
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class VacationPlanStatus(Enum):
    """Status of a vacation plan."""
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


@dataclass
class VacationPlan:
    """
    Main vacation plan entity.
    
    Represents a complete vacation plan with basic information.
    """
    id: UUID
    title: str
    status: VacationPlanStatus
    created_at: datetime
    updated_at: datetime
    
    # Optional fields
    description: str = ""
    user_id: Optional[str] = None
    total_budget: Optional[Decimal] = None
    
    @classmethod
    def create_new(cls, title: str, user_id: Optional[str] = None) -> 'VacationPlan':
        """Create a new vacation plan."""
        now = datetime.now()
        return cls(
            id=uuid4(),
            title=title,
            status=VacationPlanStatus.DRAFT,
            created_at=now,
            updated_at=now,
            user_id=user_id
        )
    
    def update_status(self, new_status: VacationPlanStatus) -> None:
        """Update vacation plan status."""
        self.status = new_status
        self.updated_at = datetime.now()
    
    def is_editable(self) -> bool:
        """Check if vacation plan can be edited."""
        return self.status in [VacationPlanStatus.DRAFT, VacationPlanStatus.CONFIRMED]
