"""
Vacation Plan Repository Interface.

Defines the contract for vacation plan data access.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.models.vacation_plan import VacationPlan


class VacationPlanRepository(ABC):
    """
    Abstract repository for vacation plan persistence.
    
    Follows the repository pattern to decouple domain logic from infrastructure.
    """
    
    @abstractmethod
    async def save(self, vacation_plan: VacationPlan) -> VacationPlan:
        """
        Save a vacation plan.
        
        Args:
            vacation_plan: The vacation plan to save
            
        Returns:
            The saved vacation plan
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, plan_id: UUID) -> Optional[VacationPlan]:
        """
        Find a vacation plan by its ID.
        
        Args:
            plan_id: The vacation plan ID
            
        Returns:
            The vacation plan if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[VacationPlan]:
        """
        Find all vacation plans for a specific user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            List of vacation plans for the user
        """
        pass
    
    @abstractmethod
    async def delete(self, plan_id: UUID) -> bool:
        """
        Delete a vacation plan.
        
        Args:
            plan_id: The vacation plan ID to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        pass
