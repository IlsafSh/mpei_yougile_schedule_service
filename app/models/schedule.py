from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime, time
from enum import Enum


class ScheduleParseRequest(BaseModel):
    name: str = Field(..., description="Название группы, аудитории или имя преподавателя")
    schedule_type: str = Field(..., pattern="^(group|room|teacher)$", description="Тип объекта расписания")
    # headless: bool = Field(True, description="Режим запуска браузера")
    cleanup_files: bool = Field(False, description="Удаление вспомогательных файлов")
    max_weeks: int = Field(21, ge=1, le=52, description="Максимальное количество недель")
    save_to_file: bool = Field(True, description="Сохранение в файл")
    filename: Optional[str] = Field(None, description="Имя файла для сохранения")


class Lesson(BaseModel):
    time: str = Field(..., description="Время занятия")
    subject: str = Field(..., description="Предмет")
    type: str = Field(..., description="Тип занятия")
    room: str = Field(..., description="Аудитория")
    teacher: str = Field(..., description="Преподаватель")


class ScheduleDay(BaseModel):
    day: str = Field(..., description="День недели и дата")
    week: int = Field(..., description="Номер недели")
    lessons: List[Lesson] = Field(..., description="Список занятий")


class ScheduleParseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class WindowType(Enum):
    """Типы окон для поиска."""
    COMMON_WINDOW = "common_window"
    SPLIT_WINDOW = "split_window"


class Window(BaseModel):
    """Найденное окно в расписании."""
    start: datetime
    end: datetime
    duration_hours: float
    window_type: WindowType
    description: str
    participants: Optional[List[str]] = None
    days_count: int = 1


class CommonWindowSearchParameters(BaseModel):
    """Параметры поиска общего окна."""
    start_date: date = Field(..., description="Начальная дата поиска")
    end_date: date = Field(..., description="Конечная дата поиска")
    required_duration: float = Field(..., gt=0, description="Требуемая продолжительность окна в часах")
    participants: List[str] = Field(..., min_items=1, description="Список участников (названия досок)")
    earliest_start_time: time = Field(default=time(hour=7, minute=0), description="Начало рабочего времени")
    latest_end_time: time = Field(default=time(hour=23, minute=0), description="Конец рабочего времени")
    min_gap_hours: float = Field(default=0.0, ge=0, description="Минимальный промежуток между занятиями в часах")
    maximize_participants: bool = Field(default=True, description="Максимизировать количество участников")
    minimize_start_time: bool = Field(default=True, description="Минимизировать время начала")
    minimize_total_idle: bool = Field(default=True, description="Минимизировать суммарное время простоя")
    minimize_max_gap: bool = Field(default=True, description="Минимизировать максимальный промежуток")
    include_holidays: bool = Field(default=False, description="Включать праздничные дни")
    include_weekends: bool = Field(default=False, description="Включать выходные дни")
    weight_participants: float = Field(default=1.0, ge=0, description="Вес критерия количества участников")
    weight_start_time: float = Field(default=1.0, ge=0, description="Вес критерия времени начала")
    weight_total_idle: float = Field(default=1.0, ge=0, description="Вес критерия суммарного простоя")
    weight_max_gap: float = Field(default=1.0, ge=0, description="Вес критерия максимального промежутка")


class CommonWindowRequest(BaseModel):
    """Объединенный запрос для поиска общего окна."""
    # Данные YouGile
    login: str = Field(..., description="Логин YouGile")
    password: str = Field(..., description="Пароль YouGile")
    project_title: str = Field(default="Учебное расписание", description="Название проекта")

    # Параметры поиска
    search_parameters: CommonWindowSearchParameters = Field(..., description="Параметры поиска общего окна")


class SplitWindowSearchParameters(BaseModel):
    """Параметры поиска сплит-окна."""
    start_date: date = Field(..., description="Начальная дата поиска")
    end_date: date = Field(..., description="Конечная дата поиска")
    total_duration: float = Field(..., gt=0, description="Общая продолжительность сплит-окна в часах")
    min_segment_duration: float = Field(default=0.5, gt=0, description="Минимальная продолжительность сегмента в часах")
    max_segments: int = Field(default=5, ge=2, description="Максимальное количество сегментов")
    participants: List[str] = Field(..., min_items=1, description="Список участников (названия досок)")
    earliest_start_time: time = Field(default=time(hour=7, minute=0), description="Начало рабочего времени")
    latest_end_time: time = Field(default=time(hour=23, minute=0), description="Конец рабочего времени")
    min_gap_hours: float = Field(default=0.0, ge=0, description="Минимальный промежуток между занятиями в часах")
    maximize_participants: bool = Field(default=True, description="Максимизировать количество участников")
    minimize_start_time: bool = Field(default=True, description="Минимизировать время начала")
    minimize_total_idle: bool = Field(default=True, description="Минимизировать суммарное время простоя")
    minimize_max_gap: bool = Field(default=True, description="Минимизировать максимальный промежуток")
    include_holidays: bool = Field(default=False, description="Включать праздничные дни")
    include_weekends: bool = Field(default=False, description="Включать выходные дни")
    weight_participants: float = Field(default=1.0, ge=0, description="Вес критерия количества участников")
    weight_start_time: float = Field(default=1.0, ge=0, description="Вес критерия времени начала")
    weight_total_idle: float = Field(default=1.0, ge=0, description="Вес критерия суммарного простоя")
    weight_max_gap: float = Field(default=1.0, ge=0, description="Вес критерия максимального промежутка")


class SplitWindowRequest(BaseModel):
    """Запрос для поиска сплит-окна."""
    # Данные YouGile
    login: str = Field(..., description="Логин YouGile")
    password: str = Field(..., description="Пароль YouGile")
    project_title: str = Field(default="Учебное расписание", description="Название проекта")

    # Параметры поиска
    search_parameters: SplitWindowSearchParameters = Field(..., description="Параметры поиска сплит-окна")


class WindowResponse(BaseModel):
    """Ответ с результатами поиска окон."""
    success: bool = Field(..., description="Успешность операции")
    message: Optional[str] = Field(None, description="Сообщение о результате")
    data: Optional[dict] = Field(None, description="Данные результата")

