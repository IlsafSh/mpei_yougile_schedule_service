"""
Модель данных для состояния стикера спринта.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class SprintStickerState(BaseModel):
    """Модель данных для состояния стикера спринта."""
    
    id: Optional[str] = None
    name: str
    begin: Optional[int] = None
    end: Optional[int] = None
    deleted: Optional[bool] = None
    
    class Config:
        validate_by_name = True
