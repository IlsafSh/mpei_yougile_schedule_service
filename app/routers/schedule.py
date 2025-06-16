from fastapi import APIRouter, HTTPException
from app.models.schedule import ScheduleParseRequest, ScheduleParseResponse
from app.services.schedule_parser import ScheduleParserService

router = APIRouter(prefix="/api/v1/schedule", tags=["schedule"])
schedule_parser_service = ScheduleParserService()

@router.post("/parse", response_model=ScheduleParseResponse)
async def parse_schedule(request: ScheduleParseRequest):
    """
    Парсинг расписания с сайта БАРС НИУ МЭИ
    
    - **name**: Название группы, аудитории или имя преподавателя
    - **schedule_type**: Тип объекта расписания (group, room, teacher)
    - deprecated: **headless**: Режим запуска браузера (True для невидимого)
    - **cleanup_files**: Удаление вспомогательных файлов
    - **max_weeks**: Максимальное количество недель для парсинга
    - **save_to_file**: Сохранение расписания в файл
    - **filename**: Имя файла для сохранения (опционально)
    """
    try:
        result = await schedule_parser_service.parse_schedule(request)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

