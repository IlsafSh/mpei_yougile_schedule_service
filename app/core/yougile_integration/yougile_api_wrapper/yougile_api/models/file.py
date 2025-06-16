"""
Модель данных для файла.
"""
from typing import Optional
from pydantic import BaseModel


class File(BaseModel):
    """Модель данных для файла."""
    
    url: str
    name: Optional[str] = None
    size: Optional[int] = None
    mime_type: Optional[str] = None
    
    class Config:
        validate_by_name = True

