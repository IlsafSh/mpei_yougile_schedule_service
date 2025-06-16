"""
Модель данных для сотрудника.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class Employee(BaseModel):
    """Модель данных для сотрудника."""
    
    id: Optional[str] = None
    email: str
    is_admin: Optional[bool] = Field(None, alias="isAdmin")
    
    class Config:
        validate_by_name = True
