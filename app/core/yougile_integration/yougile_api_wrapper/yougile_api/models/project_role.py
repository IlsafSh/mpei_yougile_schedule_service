"""
Модель данных для роли проекта.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ProjectRole(BaseModel):
    """Модель данных для роли проекта."""
    
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    permissions: Dict[str, Any]
    
    class Config:
        validate_by_name = True
