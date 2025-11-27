"""
File-based vacation plan repository implementation.

Persistent storage using JSON files.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID

from domain.models.vacation_plan import VacationPlan, VacationPlanStatus
from domain.repositories.vacation_plan_repository import VacationPlanRepository


class FileVacationRepository(VacationPlanRepository):
    """
    File-based implementation of vacation plan repository.
    
    Stores vacation plans in a JSON file for persistence.
    Suitable for small to medium datasets.
    """
    
    def __init__(self, file_path: str = "/tmp/vacation_plans.json"):
        """
        Initialize the file-based repository.
        
        Args:
            file_path: Path to the JSON file for storage
        """
        self.file_path = Path(file_path)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Ensure the storage file exists."""
        if not self.file_path.exists():
            # Create directory if it doesn't exist
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            # Create empty file with initial structure
            self._write_data({})
    
    def _read_data(self) -> Dict[str, dict]:
        """Read data from the JSON file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _write_data(self, data: Dict[str, dict]) -> None:
        """Write data to the JSON file."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _vacation_plan_to_dict(self, plan: VacationPlan) -> dict:
        """Convert vacation plan to dictionary for JSON storage."""
        return {
            'id': str(plan.id),
            'title': plan.title,
            'status': plan.status.value,
            'created_at': plan.created_at.isoformat(),
            'updated_at': plan.updated_at.isoformat(),
            'description': plan.description,
            'user_id': plan.user_id
        }
    
    def _dict_to_vacation_plan(self, data: dict) -> VacationPlan:
        """Convert dictionary from JSON storage to vacation plan."""
        return VacationPlan(
            id=UUID(data['id']),
            title=data['title'],
            status=VacationPlanStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            description=data.get('description', ''),
            user_id=data.get('user_id')
        )
    
    async def save(self, vacation_plan: VacationPlan) -> VacationPlan:
        """
        Save a vacation plan to the file.
        
        Args:
            vacation_plan: The vacation plan to save
            
        Returns:
            The saved vacation plan
        """
        data = self._read_data()
        data[str(vacation_plan.id)] = self._vacation_plan_to_dict(vacation_plan)
        self._write_data(data)
        return vacation_plan
    
    async def find_by_id(self, plan_id: UUID) -> Optional[VacationPlan]:
        """
        Find a vacation plan by ID.
        
        Args:
            plan_id: The vacation plan ID
            
        Returns:
            The vacation plan if found, None otherwise
        """
        data = self._read_data()
        plan_data = data.get(str(plan_id))
        if plan_data:
            return self._dict_to_vacation_plan(plan_data)
        return None
    
    async def find_by_user_id(self, user_id: str) -> List[VacationPlan]:
        """
        Find all vacation plans for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            List of vacation plans for the user
        """
        data = self._read_data()
        plans = []
        for plan_data in data.values():
            if plan_data.get('user_id') == user_id:
                plans.append(self._dict_to_vacation_plan(plan_data))
        return plans
    
    async def delete(self, plan_id: UUID) -> bool:
        """
        Delete a vacation plan.
        
        Args:
            plan_id: The vacation plan ID to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        data = self._read_data()
        plan_id_str = str(plan_id)
        if plan_id_str in data:
            del data[plan_id_str]
            self._write_data(data)
            return True
        return False
    
    # Additional utility methods
    
    async def find_all(self) -> List[VacationPlan]:
        """Get all vacation plans."""
        data = self._read_data()
        return [self._dict_to_vacation_plan(plan_data) for plan_data in data.values()]
    
    async def count(self) -> int:
        """Get the total count of vacation plans."""
        data = self._read_data()
        return len(data)
    
    def get_file_path(self) -> Path:
        """Get the file path being used for storage."""
        return self.file_path
