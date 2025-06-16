from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["health"])

@router.get("/health")
async def health_check():
    """
    Проверка работоспособности сервиса
    
    Возвращает статус сервиса и информацию о доступных эндпоинтах
    """
    return {
        "status": "healthy",
        "message": "MPEI Schedule Service is running",
        "version": "1.0.0",
        "endpoints": {
            "schedule_parsing": "/api/v1/schedule/parse",
            "yougile_integration": "/api/v1/yougile/integrate",
            "yougile_init_analyze": "/api/v1/yougile/init-analyze",
            "analysis_window_by_width": "/api/v1/schedule/analyze/window-by-width",
            "analysis_window_by_width_and_length": "/api/v1/schedule/analyze/window-by-width-and-length",
            "analysis_window_by_volume": "/api/v1/schedule/analyze/window-by-volume",
            "analysis_common_window": "/api/v1/schedule/analyze/common-window"
        }
    }

