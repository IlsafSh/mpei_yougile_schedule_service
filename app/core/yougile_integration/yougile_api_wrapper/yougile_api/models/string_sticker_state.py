"""
Модель данных для состояния строкового стикера.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class StringStickerState(BaseModel):
    """Модель данных для состояния строкового стикера."""
    
    id: Optional[str] = None
    name: str
    color: Optional[int] = None
    deleted: Optional[bool] = None
    
    class Config:
        validate_by_name = True
