import sys
import os
from typing import Optional, List
import logging

# Добавляем путь к модулям прототипа
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from schedule_parser.parser import MPEIRuzParser
from app.models.schedule import ScheduleParseRequest, ScheduleParseResponse

logger = logging.getLogger(__name__)

class ScheduleParserService:
    """Сервис для парсинга расписания с сайта БАРС НИУ МЭИ"""
    
    def __init__(self):
        self.parser = None
    
    async def parse_schedule(self, request: ScheduleParseRequest) -> ScheduleParseResponse:
        """
        Парсинг расписания с сайта БАРС НИУ МЭИ
        
        Args:
            request: Запрос на парсинг расписания
            
        Returns:
            ScheduleParseResponse: Результат парсинга
        """
        try:
            # Создаем экземпляр парсера
            self.parser = MPEIRuzParser(
                headless=True,
                cleanup_files=request.cleanup_files,
                max_weeks=request.max_weeks
            )
            
            # Генерируем имя файла если не указано
            filename = request.filename
            if request.save_to_file and not filename:
                filename = f"data/json_schedules/schedule_{request.schedule_type}_{request.name}.json"
            
            # Парсим расписание
            schedule = self.parser.parse(
                name=request.name,
                schedule_type=request.schedule_type,
                save_to_file=request.save_to_file,
                filename=filename
            )
            
            if schedule:
                return ScheduleParseResponse(
                    success=True,
                    message=f"Расписание успешно спарсено. Количество дней: {len(schedule)}",
                    data={
                        "schedule": schedule,
                        "days_count": len(schedule),
                        "filename": filename if request.save_to_file else None
                    }
                )
            else:
                return ScheduleParseResponse(
                    success=False,
                    message="Не удалось получить расписание"
                )
                
        except Exception as e:
            logger.error(f"Ошибка при парсинге расписания: {str(e)}")
            return ScheduleParseResponse(
                success=False,
                message=f"Ошибка при парсинге расписания: {str(e)}"
            )
        finally:
            # Закрываем браузер
            if self.parser:
                self.parser.close()
                self.parser = None

