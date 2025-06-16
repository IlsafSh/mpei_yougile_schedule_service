from pydantic import BaseModel, Field
from typing import Optional, List
from .schedule import ScheduleDay

class YouGileIntegrateRequest(BaseModel):
    login: str = Field(..., description="Логин YouGile")
    password: str = Field(..., description="Пароль YouGile")
    schedule_data: List[ScheduleDay] = Field(..., description="Данные расписания")
    schedule_name: str = Field(..., description="Название расписания")
    project_title: str = Field("Учебное расписание", description="Название проекта")

class YouGileIntegrateResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

