from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from app.config import settings
from app.routers import schedule_router, yougile_router, analysis_router, health_router

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Веб-сервис для сбора, анализа и интеграции учебного расписания БАРС НИУ МЭИ с YouGile",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настройка шаблонов
templates = Jinja2Templates(directory="templates")

# Подключение роутеров
app.include_router(health_router)
app.include_router(schedule_router)
app.include_router(yougile_router)
app.include_router(analysis_router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница с пользовательским интерфейсом"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения"""
    logger.info(f"Запуск {settings.app_name} v{settings.app_version}")
    logger.info(f"Сервер запущен на {settings.host}:{settings.port}")

@app.on_event("shutdown")
async def shutdown_event():
    """Событие остановки приложения"""
    logger.info(f"Остановка {settings.app_name}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

