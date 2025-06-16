import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""

    # Основные настройки
    app_name: str = "MPEI YouGile Schedule Service"
    app_version: str = "1.0.0"
    debug: bool = True

    # Настройки сервера
    host: str = "0.0.0.0"
    port: int = 8000

    # Настройки логирования
    log_level: str = "INFO"
    log_file: str = "data/logs/app.log"

    # Настройки парсера
    default_headless: bool = True
    default_cleanup_files: bool = False
    default_max_weeks: int = 21

    # Пути к данным
    data_dir: str = "data"
    json_schedules_dir: str = "data/json_schedules"
    logs_dir: str = "data/logs"

    class Config:
        env_file = ".env"


# Создаем экземпляр настроек
settings = Settings()

# Создаем необходимые директории
os.makedirs(settings.json_schedules_dir, exist_ok=True)
os.makedirs(settings.logs_dir, exist_ok=True)

