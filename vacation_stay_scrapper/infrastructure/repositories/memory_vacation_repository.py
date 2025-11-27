"""
In-memory vacation plan repository implementation.

Fast, simple storage for development and testing.
"""
from typing import Dict, List, Optional
from uuid import UUID

from domain.models.vacation_plan import VacationPlan
from domain.repositories.vacation_plan_repository import VacationPlanRepository


class MemoryVacationRepository(VacationPlanRepository):
    """
    In-memory implementation of vacation plan repository.
    
    Stores vacation plans in memory using a dictionary.
    Data is lost when the application restarts.
    """
    
    def __init__(self):
        """Initialize the in-memory storage."""
        self._plans: Dict[UUID, VacationPlan] = {}
    
    async def save(self, vacation_plan: VacationPlan) -> VacationPlan:
        """
        Save a vacation plan to memory.
        
        Args:
            vacation_plan: The vacation plan to save
            
        Returns:
            The saved vacation plan
        """
        self._plans[vacation_plan.id] = vacation_plan
        return vacation_plan
    
    async def find_by_id(self, plan_id: UUID) -> Optional[VacationPlan]:
        """
        Find a vacation plan by ID.
        
        Args:
            plan_id: The vacation plan ID
            
        Returns:
            The vacation plan if found, None otherwise
        """
        return self._plans.get(plan_id)
    
    async def find_by_user_id(self, user_id: str) -> List[VacationPlan]:
        """
        Find all vacation plans for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            List of vacation plans for the user
        """
        return [
            plan for plan in self._plans.values()
            if plan.user_id == user_id
        ]
    
    async def delete(self, plan_id: UUID) -> bool:
        """
        Delete a vacation plan.
        
        Args:
            plan_id: The vacation plan ID to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        if plan_id in self._plans:
            del self._plans[plan_id]
            return True
        return False
    
    # Additional utility methods for testing and debugging
    
    async def find_all(self) -> List[VacationPlan]:
        """
        Get all vacation plans.
        
        Returns:
            List of all vacation plans
        """
        return list(self._plans.values())
    
    async def count(self) -> int:
        """
        Get the total count of vacation plans.
        
        Returns:
            Total number of vacation plans
        """
        return len(self._plans)
    
    async def clear(self) -> None:
        """Clear all vacation plans (useful for testing)."""
        self._plans.clear()
