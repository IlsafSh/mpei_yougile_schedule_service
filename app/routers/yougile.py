from fastapi import APIRouter, HTTPException
from app.models.yougile import (
    YouGileIntegrateRequest, YouGileIntegrateResponse
)
from app.services.yougile_service import YouGileService

router = APIRouter(prefix="/api/v1/yougile", tags=["yougile"])
yougile_service = YouGileService()


@router.post("/integrate", response_model=YouGileIntegrateResponse)
async def integrate_schedule(request: YouGileIntegrateRequest):
    """
    Интеграция спарсенного расписания в YouGile

    - **login**: Логин YouGile
    - **password**: Пароль YouGile
    - **schedule_data**: Данные расписания
    - **schedule_name**: Название расписания
    - **project_title**: Название проекта в YouGile
    """
    try:
        result = await yougile_service.integrate_schedule(request)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

