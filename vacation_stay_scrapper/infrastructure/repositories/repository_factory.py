"""
Repository factory for creating repository instances based on configuration.

Provides a centralized way to create repositories with proper configuration.
"""
from typing import Protocol

from config.config_loader import get_app_config
from domain.repositories.vacation_plan_repository import VacationPlanRepository
from domain.repositories.stay_repository import StayRepository
from infrastructure.repositories.memory_vacation_repository import MemoryVacationRepository
from infrastructure.repositories.file_vacation_repository import FileVacationRepository
from infrastructure.repositories.memory_stay_repository import MemoryStayRepository


class RepositoryFactory:
    """
    Factory for creating repository instances.
    
    Creates repositories based on application configuration,
    enabling easy switching between storage implementations.
    """
    
    @staticmethod
    def create_vacation_plan_repository() -> VacationPlanRepository:
        """
        Create a vacation plan repository based on configuration.
        
        Returns:
            VacationPlanRepository instance
        """
        config = get_app_config()
        
        if config.data_sources.is_memory_storage():
            return MemoryVacationRepository()
        elif config.data_sources.is_file_storage():
            return FileVacationRepository(config.data_sources.vacation_file_path)
        else:
            # Default to memory storage
            return MemoryVacationRepository()
    
    @staticmethod
    def create_stay_repository() -> StayRepository:
        """
        Create a stay repository based on configuration.
        
        Returns:
            StayRepository instance
        """
        # For now, always use memory storage for stays
        # This can be extended to support file-based storage later
        return MemoryStayRepository()


# Convenience functions for easy access
def get_vacation_plan_repository() -> VacationPlanRepository:
    """
    Get a vacation plan repository instance.
    
    Returns:
        VacationPlanRepository instance
    """
    return RepositoryFactory.create_vacation_plan_repository()


def get_stay_repository() -> StayRepository:
    """
    Get a stay repository instance.
    
    Returns:
        StayRepository instance
    """
    return RepositoryFactory.create_stay_repository()
