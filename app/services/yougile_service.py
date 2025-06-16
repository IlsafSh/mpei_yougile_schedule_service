import sys
import os
from typing import Optional, List
import logging

# Добавляем путь к модулям прототипа
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from yougile_integration.yougile_api_wrapper.yougile_api import YouGileClient
from yougile_integration.yougile_integrator.integrator import ScheduleIntegrator
from app.models.yougile import (
    YouGileIntegrateRequest, YouGileIntegrateResponse
)

logger = logging.getLogger(__name__)


class YouGileService:
    """Сервис для интеграции с YouGile"""

    def __init__(self):
        pass

    async def integrate_schedule(self, request: YouGileIntegrateRequest) -> YouGileIntegrateResponse:
        """
        Интеграция расписания в YouGile

        Args:
            request: Запрос на интеграцию

        Returns:
            YouGileIntegrateResponse: Результат интеграции
        """
        try:
            # Создаем клиент YouGile
            client = YouGileClient(login=request.login, password=request.password)

            # Получаем токен
            companies = client.auth.get_companies(request.login, request.password)
            if not companies.get('content'):
                return YouGileIntegrateResponse(
                    success=False,
                    message="Не удалось получить список компаний"
                )

            company_id = companies['content'][0].get('id')
            keys = client.auth.get_keys(request.login, request.password, company_id)
            if not keys:
                key = client.auth.create_key(request.login, request.password,
                                             client.auth.get_companies(request.login, request.password)['content'][
                                                 0].get('id'))
                keys = [key]

                if not key:
                    return YouGileIntegrateResponse(
                        success=False,
                        message="Не удалось получить ключи доступа"
                    )

            token = keys[0].get('key')
            client.set_token(token)

            # Преобразуем данные расписания в формат для интегратора
            schedule_data = [day.dict() for day in request.schedule_data]

            # Создаем интегратор и интегрируем расписание
            integrator = ScheduleIntegrator(client)
            result = integrator.integrate_schedule(
                schedule_data,
                request.schedule_name,
                project_title=request.project_title
            )

            return YouGileIntegrateResponse(
                success=True,
                message="Расписание успешно интегрировано в YouGile",
                data={
                    "schedule_name": request.schedule_name,
                    "project_title": request.project_title,
                    "integration_result": result
                }
            )

        except Exception as e:
            logger.error(f"Ошибка при интеграции с YouGile: {str(e)}")
            return YouGileIntegrateResponse(
                success=False,
                message=f"Ошибка при интеграции с YouGile: {str(e)}"
            )

