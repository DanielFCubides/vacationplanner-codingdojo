"""
Vacation Plan Repository Interface.

Defines contract for vacation plan data access.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.models.vacation_plan import VacationPlan


class VacationPlanRepository(ABC):
    """
    Abstract repository for vacation plan persistence.
    
    Follows repository pattern to decouple domain from infrastructure.
    """
    
    @abstractmethod
    async def save(self, vacation_plan: VacationPlan) -> VacationPlan:
        """Save a vacation plan."""
        pass
    
    @abstractmethod
    async def find_by_id(self, plan_id: UUID) -> Optional[VacationPlan]:
        """Find vacation plan by ID."""
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[VacationPlan]:
        """Find all vacation plans for a user."""
        pass
    
    @abstractmethod
    async def delete(self, plan_id: UUID) -> bool:
        """Delete a vacation plan."""
        pass
