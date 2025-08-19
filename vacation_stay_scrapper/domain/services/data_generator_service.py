"""
Data Generator Service Interface.

Defines contract for generating fake/test data.
"""
from abc import ABC, abstractmethod
from typing import List

from domain.models.stay import Stay, StayType
from domain.models.vacation_plan import VacationPlan


class DataGeneratorService(ABC):
    """
    Abstract service for generating fake data.
    
    Used for development and testing without external dependencies.
    """
    
    @abstractmethod
    def generate_stays(
        self, 
        location: str, 
        count: int = 5,
        stay_type: StayType = None
    ) -> List[Stay]:
        """Generate fake stay data for a location."""
        pass
    
    @abstractmethod
    def generate_vacation_plan(self, title: str, user_id: str = None) -> VacationPlan:
        """Generate a fake vacation plan."""
        pass
