"""
Модель данных для группового чата.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class GroupChat(BaseModel):
    """Модель данных для группового чата."""
    
    id: Optional[str] = None
    title: str
    users: Dict[str, Any]
    deleted: Optional[bool] = None
    
    class Config:
        validate_by_name = True
