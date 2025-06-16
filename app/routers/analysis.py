from fastapi import APIRouter, HTTPException
from typing import Optional
from app.models.schedule import SplitWindowRequest, WindowResponse, CommonWindowRequest
from app.services.schedule_analyzer import ScheduleAnalyzerService

router = APIRouter(prefix="/api/v1/schedule/analyze", tags=["analysis"])
schedule_analyzer_service = ScheduleAnalyzerService()

@router.post("/common-window", response_model=WindowResponse)
async def find_common_window(request: CommonWindowRequest):
    """
    Поиск общего окна для нескольких расписаний.
    """
    try:
        result = await schedule_analyzer_service.find_common_window_service(request)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

@router.post("/split-window", response_model=WindowResponse)
async def find_split_window(request: SplitWindowRequest):
    """
    Поиск сплит окна с заданной общей продолжительностью.
    """
    try:
        result = await schedule_analyzer_service.find_split_window(request)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")
