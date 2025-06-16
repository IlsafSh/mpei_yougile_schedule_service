"""
Модель данных для проекта.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class Project(BaseModel):
    """Модель данных для проекта."""
    
    id: Optional[str] = None
    title: str
    users: Optional[Dict[str, Any]] = None
    deleted: Optional[bool] = None
    
    class Config:
        validate_by_name = True
