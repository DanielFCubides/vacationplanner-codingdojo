"""
Data Generator Service Interface.

Defines the contract for generating fake/test data for development and testing.
"""
from abc import ABC, abstractmethod
from typing import List

from domain.models.stay import Stay, StayType
from domain.models.vacation_plan import VacationPlan


class DataGeneratorService(ABC):
    """
    Abstract service for generating fake data.
    
    Used for development and testing without external dependencies.
    Enables rapid development and consistent test data.
    """
    
    @abstractmethod
    def generate_stays(
        self, 
        location: str, 
        count: int = 5,
        stay_type: StayType = None
    ) -> List[Stay]:
        """
        Generate fake stay data for a specific location.
        
        Args:
            location: The location for generated stays
            count: Number of stays to generate
            stay_type: Optional specific type of stays to generate
            
        Returns:
            List of generated stays
        """
        pass
    
    @abstractmethod
    def generate_vacation_plan(
        self, 
        title: str, 
        user_id: str = None
    ) -> VacationPlan:
        """
        Generate a fake vacation plan.
        
        Args:
            title: Title for the vacation plan
            user_id: Optional user identifier
            
        Returns:
            Generated vacation plan
        """
        pass
