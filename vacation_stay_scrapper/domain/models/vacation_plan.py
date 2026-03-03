"""
Vacation Plan domain models.

Core business entities for vacation planning.
"""
from dataclasses import dataclass
from datetime import datetime
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
    Vacation Plan aggregate root.
    
    Represents a complete vacation plan with basic information.
    This is the main entity that coordinates vacation planning activities.
    """
    id: UUID
    title: str
    status: VacationPlanStatus
    created_at: datetime
    updated_at: datetime
    
    # Optional attributes
    description: str = ""
    user_id: Optional[str] = None
    
    @classmethod
    def create_new(cls, title: str, user_id: Optional[str] = None) -> 'VacationPlan':
        """
        Create a new vacation plan.
        
        Args:
            title: The vacation plan title
            user_id: Optional user identifier
            
        Returns:
            New vacation plan in DRAFT status
        """
        now = datetime.now()
        return cls(
            id=uuid4(),
            title=title,
            status=VacationPlanStatus.DRAFT,
            created_at=now,
            updated_at=now,
            description="",
            user_id=user_id
        )
    
    def update_status(self, new_status: VacationPlanStatus) -> None:
        """
        Update the vacation plan status.
        
        Args:
            new_status: The new status to set
        """
        self.status = new_status
        self.updated_at = datetime.now()
    
    def is_editable(self) -> bool:
        """
        Check if the vacation plan can be edited.
        
        Returns:
            True if the plan can be edited, False otherwise
        """
        return self.status in [VacationPlanStatus.DRAFT, VacationPlanStatus.CONFIRMED]
    
    def is_active(self) -> bool:
        """
        Check if the vacation plan is active.
        
        Returns:
            True if the plan is not cancelled, False otherwise
        """
        return self.status != VacationPlanStatus.CANCELLED
