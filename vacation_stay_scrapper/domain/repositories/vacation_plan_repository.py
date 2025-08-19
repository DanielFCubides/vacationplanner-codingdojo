"""
Vacation Plan Repository Interface.

Defines contract for vacation plan data access.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from domain.models.vacation_plan import VacationPlan, VacationPlanId


class VacationPlanRepository(ABC):
    """
    Abstract repository for vacation plan persistence.
    
    Follows repository pattern to decouple domain from infrastructure.
    """
    
    @abstractmethod
    async def save(self, vacation_plan: VacationPlan) -> VacationPlan:
        """
        Save a vacation plan.
        
        Args:
            vacation_plan: The vacation plan to save
            
        Returns:
            The saved vacation plan
            
        Raises:
            RepositoryError: If save operation fails
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, plan_id: VacationPlanId) -> Optional[VacationPlan]:
        """
        Find vacation plan by ID.
        
        Args:
            plan_id: The vacation plan ID
            
        Returns:
            The vacation plan if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[VacationPlan]:
        """
        Find all vacation plans for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            List of vacation plans for the user
        """
        pass
    
    @abstractmethod
    async def find_all(self) -> List[VacationPlan]:
        """
        Find all vacation plans.
        
        Returns:
            List of all vacation plans
        """
        pass
    
    @abstractmethod
    async def delete(self, plan_id: VacationPlanId) -> bool:
        """
        Delete a vacation plan.
        
        Args:
            plan_id: The vacation plan ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def exists(self, plan_id: VacationPlanId) -> bool:
        """
        Check if vacation plan exists.
        
        Args:
            plan_id: The vacation plan ID
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def count_by_user(self, user_id: str) -> int:
        """
        Count vacation plans for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Number of vacation plans for the user
        """
        pass
