import sys
import os
import logging

# Добавляем путь к модулям прототипа
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from yougile_integration.yougile_api_wrapper.yougile_api import YouGileClient
from yougile_integration.yougile_integrator.integrator import ScheduleIntegrator
from schedule_analyzer.analyzer import ScheduleAnalyzer
from app.models.schedule import SplitWindowRequest, WindowResponse, CommonWindowRequest
from app.models.yougile import YouGileIntegrateRequest

logger = logging.getLogger(__name__)

class ScheduleAnalyzerService:
    """Сервис для анализа расписания"""

    def __init__(self):
        pass

    async def find_common_window_service(self, request: CommonWindowRequest) -> WindowResponse:
        """
        Поиск общего окна для одного/нескольких расписаний

        Args:
            request: Объединенный запрос с данными YouGile и параметрами поиска

        Returns:
            WindowResponse: Результат поиска
        """
        try:
            # Создаем клиент YouGile
            client = YouGileClient(login=request.login, password=request.password)

            # Получаем токен
            companies = client.auth.get_companies(request.login, request.password)
            if not companies.get('content'):
                return WindowResponse(
                    success=False,
                    message="Не удалось получить список компаний"
                )

            company_id = companies['content'][0].get('id')
            keys = client.auth.get_keys(request.login, request.password, company_id)
            if not keys:
                key = client.auth.create_key(request.login, request.password, company_id)
                keys = [key] if key else []

            if not keys:
                return WindowResponse(
                    success=False,
                    message="Не удалось получить ключи доступа"
                )

            token = keys[0].get('key')
            client.set_token(token)

            # Создаем интегратор и анализатор
            integrator = ScheduleIntegrator(client)
            analyzer = ScheduleAnalyzer(integrator)

            # Извлекаем параметры поиска
            params = request.search_parameters

            # Формируем конфигурацию алгоритма
            algorithm_config = {
                "type": "common_window",
                "start_date": params.start_date,
                "end_date": params.end_date,
                "required_duration": params.required_duration,
                "participants": params.participants,
                "earliest_start_time": params.earliest_start_time,
                "latest_end_time": params.latest_end_time,
                "min_gap_hours": params.min_gap_hours,
                "include_holidays": params.include_holidays,
                "include_weekends": params.include_weekends,
                "maximize_participants": params.maximize_participants,
                "minimize_start_time": params.minimize_start_time,
                "minimize_total_idle": params.minimize_total_idle,
                "minimize_max_gap": params.minimize_max_gap,
                "weight_participants": params.weight_participants,
                "weight_start_time": params.weight_start_time,
                "weight_total_idle": params.weight_total_idle,
                "weight_max_gap": params.weight_max_gap
            }

            # Выполняем анализ расписания
            found_windows = analyzer.analyze_schedule([algorithm_config], board_names=params.participants)

            if not found_windows:
                return WindowResponse(
                    success=True,
                    message="Общее окно не найдено",
                    data={
                        "project_title": request.project_title,
                        "analysis_result": [],
                        "found_windows_count": 0
                    }
                )

            # Преобразуем найденные окна в формат ответа
            windows_data = []
            for window in found_windows:
                window_data = {
                    "start": window.start.isoformat(),
                    "end": window.end.isoformat(),
                    "duration_hours": window.duration_hours,
                    "window_type": window.window_type.value,
                    "description": window.description,
                    "participants": window.participants,
                    "days_count": window.days_count
                }
                windows_data.append(window_data)

            return WindowResponse(
                success=True,
                message=f"Найдено окон: {len(found_windows)}",
                data={
                    "project_title": request.project_title,
                    "analysis_result": windows_data,
                    "found_windows_count": len(found_windows),
                    "search_parameters": {
                        "start_date": params.start_date.isoformat(),
                        "end_date": params.end_date.isoformat(),
                        "required_duration": params.required_duration,
                        "participants": params.participants
                    }
                }
            )

        except Exception as e:
            logger.error(f"Ошибка при поиске общего окна: {e}")
            return WindowResponse(
                success=False,
                message=f"Ошибка при поиске общего окна: {str(e)}"
            )

    async def find_split_window(self, request: SplitWindowRequest) -> WindowResponse:
        """
        Поиск сплит окна заданной общей продолжительностью

        Args:
            request: Запрос на поиск сплит-окна

        Returns:
            WindowResponse: Результат поиска
        """
        try:
            # Создаем клиент YouGile
            client = YouGileClient(login=request.login, password=request.password)

            # Получаем токен
            companies = client.auth.get_companies(request.login, request.password)
            if not companies.get('content'):
                return WindowResponse(
                    success=False,
                    message="Не удалось получить список компаний"
                )

            company_id = companies['content'][0].get('id')
            keys = client.auth.get_keys(request.login, request.password, company_id)
            if not keys:
                key = client.auth.create_key(request.login, request.password, company_id)
                keys = [key] if key else []

            if not keys:
                return WindowResponse(
                    success=False,
                    message="Не удалось получить ключи доступа"
                )

            token = keys[0].get('key')
            client.set_token(token)

            # Создаем интегратор и анализатор
            integrator = ScheduleIntegrator(client)
            analyzer = ScheduleAnalyzer(integrator)

            # Извлекаем параметры поиска
            params = request.search_parameters

            # Формируем конфигурацию алгоритма для сплит-окна
            algorithm_config = {
                "type": "split_window",
                "start_date": params.start_date,
                "end_date": params.end_date,
                "total_duration": params.total_duration,
                "min_segment_duration": params.min_segment_duration,
                "max_segments": params.max_segments,
                "participants": params.participants,
                "earliest_start_time": params.earliest_start_time,
                "latest_end_time": params.latest_end_time,
                "min_gap_hours": params.min_gap_hours,
                "include_holidays": params.include_holidays,
                "include_weekends": params.include_weekends,
                "maximize_participants": params.maximize_participants,
                "minimize_start_time": params.minimize_start_time,
                "minimize_total_idle": params.minimize_total_idle,
                "minimize_max_gap": params.minimize_max_gap,
                "weight_participants": params.weight_participants,
                "weight_start_time": params.weight_start_time,
                "weight_total_idle": params.weight_total_idle,
                "weight_max_gap": params.weight_max_gap
            }

            # Выполняем анализ расписания
            found_windows = analyzer.analyze_schedule([algorithm_config], board_names=params.participants)

            # Поскольку метод find_split_window в анализаторе еще не реализован,
            # возвращаем соответствующее сообщение
            return WindowResponse(
                success=False,
                message="Алгоритм поиска сплит-окна еще не реализован в ScheduleAnalyzer",
                data={
                    "project_title": request.project_title,
                    "analysis_result": [],
                    "found_windows_count": 0,
                    "search_parameters": {
                        "start_date": params.start_date.isoformat(),
                        "end_date": params.end_date.isoformat(),
                        "total_duration": params.total_duration,
                        "participants": params.participants
                    }
                }
            )

        except Exception as e:
            logger.error(f"Ошибка при поиске сплит-окна: {e}")
            return WindowResponse(
                success=False,
                message=f"Ошибка при поиске сплит-окна: {str(e)}"
            )