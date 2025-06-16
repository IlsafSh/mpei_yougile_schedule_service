"""
Модель данных для компании.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class Company(BaseModel):
    """Модель данных для компании."""
    
    id: Optional[str] = None
    title: str
    deleted: Optional[bool] = False
    timestamp: Optional[int] = None
    api_data: Optional[Dict[str, Any]] = Field(None, alias="apiData")
    
    class Config:
        validate_by_name = True

