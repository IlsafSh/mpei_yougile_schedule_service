"""
Модель данных для задачи.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class Task(BaseModel):
    """Модель данных для задачи."""
    
    id: Optional[str] = None
    title: str
    column_id: Optional[str] = Field(None, alias="columnId")
    description: Optional[str] = None
    archived: Optional[bool] = None
    completed: Optional[bool] = None
    subtasks: Optional[List[str]] = None
    assigned: Optional[List[str]] = None
    createdBy: Optional[str] = None
    deadline: Optional[Dict[str, Any]] = None
    timeTracking: Optional[Dict[str, Any]] = None
    checklists: Optional[List[Dict[str, Any]]] = None
    stickers: Optional[Dict[str, Any]] = None
    color: Optional[str] = None
    idTaskCommon: Optional[str] = None
    idTaskProject: Optional[str] = None
    stopwatch: Optional[Dict[str, Any]] = None
    timer: Optional[Dict[str, Any]] = None
    deleted: Optional[bool] = None
    
    class Config:
        validate_by_name = True
