"""
Класс для интеграции расписания в YouGile.
"""

import logging
from datetime import datetime
import time
import random
from typing import List, Dict, Any, Optional

from yougile_integration.yougile_api_wrapper.yougile_api import YouGileClient
from yougile_integration.yougile_api_wrapper.yougile_api.models import (
    Project, Board, Column, Task, Employee, StringSticker
)


class ScheduleIntegrator:
    """
    Класс для интеграции расписания в YouGile.

    Управляет проектами, досками, колонками, задачами и стикерами на основе данных расписания.
    """

    def __init__(self, client: YouGileClient, max_retries=5, base_delay=10, max_delay=60):
        """
        Инициализация интегратора.

        Args:
            client: Клиент YouGile API.
            max_retries: Максимальное количество повторных попыток при ошибке API.
            base_delay: Базовая задержка между запросами в секундах.
            max_delay: Максимальная задержка между запросами в секундах.
        """
        self.logger = logging.getLogger('ScheduleIntegrator')
        self._setup_logging()

        self.client = client
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

        # Кэши для данных
        self._projects_cache = {}
        self._boards_cache = {}
        self._columns_cache = {}
        self._tasks_cache = {}
        self._employees_cache = {}
        self._stickers_cache = {}

        self.schedule_project = None
        self.schedule_boards = []
        self.schedule_columns = []
        self.schedule_tasks = []
        self.schedule_stickers = []
        self.analyze_board = None
        self.analyze_columns = []
        self.analyze_tasks = []

        self._setup_attributes()

    def _setup_logging(self):
        """Настройка логирования."""
        self.logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)

    def _setup_attributes(self):
        self.get_projects()
        self.get_boards()
        self.get_columns()
        self.get_tasks()
        self.get_string_stickers()

    def _api_call_with_retry(self, api_method, *args, **kwargs):
        """
        Выполнение API-запроса с повторами при ошибке Too Many Requests.

        Args:
            api_method: Метод API для вызова.
            *args: Позиционные аргументы.
            **kwargs: Именованные аргументы.

        Returns:
            Результат API-запроса.
        """
        retries = 0
        while retries <= self.max_retries:
            try:
                if retries > 0:
                    delay = min(self.base_delay * (2 ** retries) + random.uniform(0, 1), self.max_delay)
                    self.logger.info(f"Повторная попытка {retries}/{self.max_retries} через {delay:.2f} сек...")
                    time.sleep(delay)
                return api_method(*args, **kwargs)
            except Exception as e:
                if "Too Many Requests" in str(e) or "429" in str(e):
                    retries += 1
                    if retries > self.max_retries:
                        raise
                else:
                    raise

    def _fetch_and_cache(self, api_method, cache_dict, model_class, key='id', limit=None):
        """Получение данных из API и кэширование."""
        try:
            params = {} if limit is None else {'limit': limit}
            response = self._api_call_with_retry(api_method, **params)
            items = []
            if 'content' in response:
                for item in response['content']:
                    obj = model_class.model_validate(item)
                    cache_dict[obj.__getattribute__(key)] = obj
                    items.append(obj)
            return items
        except Exception as e:
            self.logger.error(f"Ошибка при получении данных: {e}")
            return []

    def get_projects(self) -> List[Project]:
        """Получение списка проектов из кэша или API."""
        if not self._projects_cache:
            self._fetch_and_cache(self.client.projects.list, self._projects_cache, Project)
        return list(self._projects_cache.values())

    def get_boards(self) -> List[Board]:
        """Получение списка досок из кэша или API."""
        if not self._boards_cache:
            self._fetch_and_cache(self.client.boards.list, self._boards_cache, Board, limit=1000)
        return list(self._boards_cache.values())

    def get_columns(self) -> List[Column]:
        """Получение списка колонок из кэша или API."""
        if not self._columns_cache:
            self._fetch_and_cache(self.client.columns.list, self._columns_cache, Column, limit=1000)
        return list(self._columns_cache.values())

    def get_tasks(self) -> List[Task]:
        """Получение списка задач из кэша или API."""
        if not self._tasks_cache:
            self._fetch_and_cache(self.client.tasks.list, self._tasks_cache, Task, limit=1000)
        return list(self._tasks_cache.values())

    def get_employees(self) -> List[Employee]:
        """Получение списка сотрудников из кэша или API."""
        if not self._employees_cache:
            self._fetch_and_cache(self.client.employees.list, self._employees_cache, Employee)
        return list(self._employees_cache.values())

    def get_string_stickers(self) -> List[StringSticker]:
        """Получение списка стикеров из кэша или API."""
        if not self._stickers_cache:
            self._fetch_and_cache(self.client.string_stickers.list, self._stickers_cache, StringSticker)
        return list(self._stickers_cache.values())

    def _get_admin_id(self) -> Optional[str]:
        """Получение ID администратора."""
        if not hasattr(self, '_admin_id'):
            employees = self.get_employees()
            admin = next((emp for emp in employees if emp.is_admin and emp.email == self.client.login), None)
            self._admin_id = admin.id if admin else None
        return self._admin_id

    def create_schedule_project(self, project_title: Optional[str] = 'Учебное расписание') -> Optional[Project]:
        """Создание проекта для расписания."""
        try:
            if self.schedule_project is None:
                admin_id = self._get_admin_id()
                if not admin_id:
                    self.logger.error("Администратор с указанным email не найден")
                    return None

                self.logger.info(f"Создание проекта: {project_title}")
                create_response = self._api_call_with_retry(
                    self.client.projects.create,
                    title=project_title,
                    users={admin_id: "admin"}
                )
                project_id = create_response.get('id')
                if not project_id:
                    self.logger.error("Не получен ID созданного проекта")
                    return None

                # Получаем полные данные проекта
                project_data = self._api_call_with_retry(self.client.projects.get, id=project_id)
                self.schedule_project = Project.model_validate(project_data)
                self._projects_cache[self.schedule_project.id] = self.schedule_project
                self.logger.info(f"Проект создан: {self.schedule_project.title} (ID: {self.schedule_project.id})")
            return self.schedule_project
        except Exception as e:
            self.logger.error(f"Ошибка при создании проекта: {e}")
            return None

    def get_schedule_project(self, project_title: Optional[str] = 'Учебное расписание') -> Optional[Project]:
        """Получение проекта расписания."""
        try:
            projects = self.get_projects()
            self.schedule_project = next(
                (p for p in projects if p.title == project_title and not getattr(p, 'deleted', False)),
                None
            )
            if self.schedule_project:
                self.logger.info(f"Найден проект: {self.schedule_project.title} (ID: {self.schedule_project.id})")
            else:
                self.logger.info(f"Проект '{project_title}' не найден")
            return self.schedule_project
        except Exception as e:
            self.logger.error(f"Ошибка при получении проекта: {e}")
            return None

    def get_schedule_boards(self) -> List[Board]:
        """Получение досок проекта расписания."""
        try:
            if not self.schedule_project:
                self.logger.warning("Проект расписания не найден")
                return []
            boards = self.get_boards()
            self.schedule_boards = [b for b in boards if b.project_id == self.schedule_project.id and not getattr(b, 'deleted', False)]
            self.logger.info(f"Найдено досок: {len(self.schedule_boards)}")
            return self.schedule_boards
        except Exception as e:
            self.logger.error(f"Ошибка при получении досок: {e}")
            return []

    def get_schedule_columns(self) -> List[Column]:
        """Получение колонок проекта расписания."""
        try:
            self.get_schedule_boards()
            columns = self.get_columns()
            board_ids = {b.id for b in self.schedule_boards}
            self.schedule_columns = [c for c in columns if c.board_id in board_ids and not getattr(c, 'deleted', False)]
            self.logger.info(f"Найдено колонок: {len(self.schedule_columns)}")
            return self.schedule_columns
        except Exception as e:
            self.logger.error(f"Ошибка при получении колонок: {e}")
            return []

    def get_schedule_tasks(self) -> List[Task]:
        """Получение задач проекта расписания."""
        try:
            self.get_schedule_columns()
            tasks = self.get_tasks()
            column_ids = {c.id for c in self.schedule_columns}
            self.schedule_tasks = [t for t in tasks if t.column_id in column_ids and not getattr(t, 'deleted', False)]
            self.logger.info(f"Найдено задач: {len(self.schedule_tasks)}")
            return self.schedule_tasks
        except Exception as e:
            self.logger.error(f"Ошибка при получении задач: {e}")
            return []

    def get_schedule_stickers(self) -> List[StringSticker]:
        """Получение стикеров для расписания."""
        try:
            stickers = self.get_string_stickers()
            self.schedule_stickers = [s for s in stickers if s.name in ['Тип занятия', 'Аудитория', 'Преподаватель']]
            self.logger.info(f"Найдено стикеров: {len(self.schedule_stickers)}")
            return self.schedule_stickers
        except Exception as e:
            self.logger.error(f"Ошибка при получении стикеров: {e}")
            return []

    def create_schedule_board(self, schedule_data: List[Dict[str, Any]], schedule_name: str, project_id: str) -> Optional[Board]:
        """Создание доски для расписания."""
        try:
            self.logger.info(f"Создание доски: {schedule_name}")
            self.get_schedule_stickers()
            if not self.schedule_stickers:
                self.create_schedule_stickers(schedule_data)
            else:
                self.update_schedule_stickers(schedule_data)

            custom_stickers = {s.id: True for s in self.schedule_stickers}
            stickers = {
                "timer": False,
                "deadline": True,
                "stopwatch": True,
                "timeTracking": False,
                "assignee": True,
                "repeat": False,
                "custom": custom_stickers
            }

            create_response = self._api_call_with_retry(
                self.client.boards.create,
                title=schedule_name,
                project_id=project_id,
                stickers=stickers
            )
            board_id = create_response.get('id')
            if not board_id:
                self.logger.error("Не получен ID созданной доски")
                return None

            # Получаем полные данные доски
            board_data = self._api_call_with_retry(self.client.boards.get, id=board_id)
            new_board = Board.model_validate(board_data)
            self._boards_cache[new_board.id] = new_board
            self.get_schedule_boards()
            self.logger.info(f"Доска создана: {new_board.title} (ID: {new_board.id})")
            return new_board
        except Exception as e:
            self.logger.error(f"Ошибка при создании доски: {e}")
            return None

    def create_schedule_stickers(self, schedule_data: List[Dict[str, Any]]):
        """Создание стикеров для расписания."""
        try:
            self.logger.info("Создание стикеров для расписания")

            if not self.schedule_stickers:
                # Создание стикера для типов занятий, аудиторий, преподавателей
                type_states = []
                room_states = []
                teacher_states = []
                for day in schedule_data:
                    for lesson in day.get('lessons', []):
                        lesson_type = lesson.get('type', '').strip()
                        if lesson_type and lesson_type not in [state.get('name') for state in type_states]:
                            type_states.append({
                                "name": lesson_type,
                                "color": "#FF0000"
                            })

                        room = lesson.get('room', '').strip()
                        if room and room not in [state.get('name') for state in room_states]:
                            room_states.append({
                                "name": room,
                                "color": "#00FF00"
                            })

                        teacher = lesson.get('teacher', '').strip()
                        if teacher and teacher not in [state.get('name') for state in teacher_states]:
                            teacher_states.append({
                                "name": teacher,
                                "color": "#0000FF"
                            })

                if type_states:
                    type_sticker_response = self._api_call_with_retry(
                        self.client.string_stickers.create,
                        name='Тип занятия',
                        states=type_states,
                        icon='bookmark'
                    )

                    type_sticker_id = type_sticker_response.get('id')
                    if type_sticker_id:
                        sticker_data = self._api_call_with_retry(self.client.string_stickers.get, id=type_sticker_id)
                        sticker_id = sticker_data.get('id')
                        # Получаем полные данные стикера
                        sticker_data = self._api_call_with_retry(self.client.string_stickers.get, id=sticker_id)
                        sticker = StringSticker.model_validate(sticker_data)
                        self._stickers_cache[sticker.id] = sticker

                if room_states:
                    room_sticker_response = self._api_call_with_retry(
                        self.client.string_stickers.create,
                        name='Аудитория',
                        states=room_states,
                        icon='key'
                    )

                    room_sticker_id = room_sticker_response.get('id')
                    if room_sticker_id:
                        sticker_data = self._api_call_with_retry(self.client.string_stickers.get, id=room_sticker_id)
                        sticker_id = sticker_data.get('id')
                        # Получаем полные данные стикера
                        sticker_data = self._api_call_with_retry(self.client.string_stickers.get, id=sticker_id)
                        sticker = StringSticker.model_validate(sticker_data)
                        self._stickers_cache[sticker.id] = sticker

                if teacher_states:
                    teacher_sticker_response = self._api_call_with_retry(
                        self.client.string_stickers.create,
                        name='Преподаватель',
                        states=teacher_states,
                        icon='user'
                    )

                    teacher_sticker_id = teacher_sticker_response.get('id')
                    if teacher_sticker_id:
                        sticker_data = self._api_call_with_retry(self.client.string_stickers.get, id=teacher_sticker_id)
                        sticker_id = sticker_data.get('id')
                        # Получаем полные данные стикера
                        sticker_data = self._api_call_with_retry(self.client.string_stickers.get, id=sticker_id)
                        sticker = StringSticker.model_validate(sticker_data)
                        self._stickers_cache[sticker.id] = sticker
            self.get_schedule_stickers()
            self.logger.info(f"Создано стикеров: {len(self.schedule_stickers)}")
        except Exception as e:
            self.logger.error(f"Ошибка при создании стикеров: {e}")

    def update_schedule_stickers(self, schedule_data: List[Dict[str, Any]]):
        """Обновление стикеров для расписания."""
        try:
            self.logger.info("Обновление стикеров")
            self.get_schedule_stickers()
            type_sticker = [sticker for sticker in self.schedule_stickers if sticker.name == 'Тип занятия'][0]
            room_sticker = [sticker for sticker in self.schedule_stickers if sticker.name == 'Аудитория'][0]
            teacher_sticker = [sticker for sticker in self.schedule_stickers if sticker.name == 'Преподаватель'][0]

            type_sticker_states_names = [state.get('name') for state in type_sticker.states]
            room_sticker_states_names = [state.get('name') for state in room_sticker.states]
            teacher_sticker_states_names = [state.get('name') for state in teacher_sticker.states]

            for day in schedule_data:
                for lesson in day.get('lessons', []):
                    lesson_type = lesson.get('type', '').strip()
                    if lesson_type and lesson_type not in type_sticker_states_names:
                        type_sticker_states_names.append(lesson_type)
                        type_sticker_state_response = self._api_call_with_retry(
                            self.client.string_sticker_states.create,
                            sticker_id=type_sticker.id,
                            name=lesson_type,
                            color="#FF0000"
                        )
                        # Обновляем кэш стикера после добавления нового состояния
                        sticker_data = self._api_call_with_retry(self.client.string_stickers.get, id=type_sticker.id)
                        self._stickers_cache[type_sticker.id] = StringSticker.model_validate(sticker_data)

                    room = lesson.get('room', '').strip()
                    if room and room not in room_sticker_states_names:
                        room_sticker_states_names.append(room)
                        room_sticker_state_response = self._api_call_with_retry(
                            self.client.string_sticker_states.create,
                            sticker_id=room_sticker.id,
                            name=room,
                            color="#FF0000"
                        )
                        # Обновляем кэш стикера после добавления нового состояния
                        sticker_data = self._api_call_with_retry(self.client.string_stickers.get, id=room_sticker.id)
                        self._stickers_cache[room_sticker.id] = StringSticker.model_validate(sticker_data)

                    teacher = lesson.get('teacher', '').strip()
                    if teacher and teacher not in teacher_sticker_states_names:
                        teacher_sticker_states_names.append(teacher)
                        teacher_sticker_state_response = self._api_call_with_retry(
                            self.client.string_sticker_states.create,
                            sticker_id=teacher_sticker.id,
                            name=teacher,
                            color="#FF0000"
                        )
                        # Обновляем кэш стикера после добавления нового состояния
                        sticker_data = self._api_call_with_retry(self.client.string_stickers.get, id=teacher_sticker.id)
                        self._stickers_cache[teacher_sticker.id] = StringSticker.model_validate(sticker_data)
            self.get_schedule_stickers()
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении стикеров: {e}")

    def create_schedule_columns(self, schedule_data: List[Dict[str, Any]], board_id: str) -> List[Column]:
        """Создание колонок для недель."""
        try:
            self.logger.info("Создание колонок для недель")
            weeks = sorted({d.get('week') for d in schedule_data if d.get('week') is not None})
            for week in weeks:
                title = f"Неделя {week}"
                if not any(c.board_id == board_id and c.title == title for c in self.schedule_columns):
                    create_response = self._api_call_with_retry(
                        self.client.columns.create,
                        title=title,
                        board_id=board_id,
                        color=(week % 16) + 1
                    )
                    column_id = create_response.get('id')
                    if not column_id:
                        self.logger.error(f"Не получен ID колонки '{title}'")
                        continue
                    # Получаем полные данные колонки
                    column_data = self._api_call_with_retry(self.client.columns.get, id=column_id)
                    column = Column.model_validate(column_data)
                    self._columns_cache[column.id] = column
            self.get_schedule_columns()
            self.logger.info(f"Всего колонок: {len(self.schedule_columns)}")
            return self.schedule_columns
        except Exception as e:
            self.logger.error(f"Ошибка при создании колонок: {e}")
            return []

    def _get_column_by_week(self, week: int, board_id: str) -> Optional[Column]:
        """Получение колонки по номеру недели."""
        for column in self.schedule_columns:
            if column.board_id == board_id and column.title == f"Неделя {week}":
                return column
        self.logger.warning(f"Колонка для недели {week} не найдена")
        return None

    def _parse_timestamp(self, date_str: str, time_str: str) -> tuple[int, int]:
        """Преобразование даты и времени в timestamp."""
        try:
            month_map = {
                "января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6,
                "июля": 7, "августа": 8, "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
            }
            year = 2025
            day, month_name = date_str.split(',')[1].strip().split()
            month = month_map[month_name]
            start_time, end_time = time_str.split('-')
            start_dt = datetime(year, month, int(day), *map(int, start_time.split(':')))
            end_dt = datetime(year, month, int(day), *map(int, end_time.split(':')))
            return int(start_dt.timestamp() * 1000), int(end_dt.timestamp() * 1000)
        except Exception as e:
            self.logger.error(f"Ошибка парсинга времени '{date_str} {time_str}': {e}")
            current = int(time.time() * 1000)
            return current, current + 3600000

    def create_schedule_tasks(self, schedule_data: List[Dict[str, Any]], board_id: str) -> List[Task]:
        """Создание задач для занятий."""
        try:
            self.logger.info("Создание задач для занятий")
            created_tasks = 0
            for day in schedule_data:
                week = day.get('week')
                column = self._get_column_by_week(week, board_id)
                if not column:
                    continue
                for lesson in day.get('lessons', []):
                    subject = lesson.get('subject', '').strip()
                    if not subject:
                        continue
                    # Формируем стикеры
                    custom_stickers = {}
                    lesson_values = {
                        'Тип занятия': lesson.get('type', '').strip(),
                        'Аудитория': lesson.get('room', '').strip(),
                        'Преподаватель': lesson.get('teacher', '').strip()
                    }

                    if not self.schedule_stickers:
                        self.get_schedule_stickers()

                    for sticker in self.schedule_stickers:
                        value = lesson_values.get(sticker.name, '')
                        if value:
                            state = next((st for st in sticker.states if st.get('name') == value), None)
                            custom_stickers[sticker.id] = state.get('id') if state else "-"
                        else:
                            custom_stickers[sticker.id] = "-"
                    start_ts, end_ts = self._parse_timestamp(day.get('day', ''), lesson.get('time', ''))
                    task_data = {
                        "title": subject,
                        "column_id": column.id,
                        "deadline": {"deadline": end_ts, "startDate": start_ts, "withTime": True},
                        "stickers": custom_stickers,
                        "description": "\n".join(
                            f"{k}: {v}" for k, v in [
                                ("Тип", lesson.get('type')),
                                ("Аудитория", lesson.get('room')),
                                ("Преподаватель", lesson.get('teacher')),
                                ("Время", lesson.get('time'))
                            ] if v
                        )
                    }
                    create_response = self._api_call_with_retry(self.client.tasks.create, **task_data)
                    task_id = create_response.get('id')
                    if not task_id:
                        self.logger.error(f"Не получен ID задачи '{subject}'")
                        continue
                    # Получаем полные данные задачи
                    task_data = self._api_call_with_retry(self.client.tasks.get, id=task_id)
                    task = Task.model_validate(task_data)
                    self._tasks_cache[task.id] = task
                    created_tasks += 1
            self.get_schedule_tasks()
            self.logger.info(f"Создано задач: {created_tasks}")
            return self.schedule_tasks
        except Exception as e:
            self.logger.error(f"Ошибка при создании задач: {e}")
            return []

    def integrate_schedule(self, schedule_data: List[Dict[str, Any]], schedule_name: str, project_title: Optional[str] = 'Учебное расписание') -> bool:
        """Интеграция расписания в YouGile."""
        try:
            self.logger.info(f"Интеграция расписания: {schedule_name}")
            self.schedule_project = self.get_schedule_project(project_title) or self.create_schedule_project(project_title)
            if not self.schedule_project:
                return False
            self.get_schedule_boards()
            board = next((b for b in self.schedule_boards if b.title == schedule_name), None)
            if board:
                self._clean_up_board(board.id)
            else:
                board = self.create_schedule_board(schedule_data, schedule_name, self.schedule_project.id)
            if not board:
                return False
            self.create_schedule_columns(schedule_data, board.id)
            self.create_schedule_tasks(schedule_data, board.id)
            self.logger.info(f"Интеграция '{schedule_name}' завершена")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка интеграции: {e}")
            return False

    def _clean_up_board(self, board_id: str):
        """Очистка задач на доске."""
        try:
            self.get_schedule_tasks()
            for task in self.schedule_tasks:
                if task.column_id in {c.id for c in self.schedule_columns if c.board_id == board_id}:
                    self._api_call_with_retry(self.client.tasks.update, id=task.id, deleted=True)
                    self._tasks_cache[task.id].deleted = True
        except Exception as e:
            self.logger.error(f"Ошибка при очистке доски: {e}")

    def get_analyze_board(self, board_name: Optional[str] = "Анализ расписания") -> Optional[Board]:
        """Получение доски анализа."""
        try:
            self.get_schedule_project()
            if not self.schedule_project:
                self.get_schedule_project()
            if not self.schedule_project:
                return None
            self.get_schedule_boards()
            self.analyze_board = next((b for b in self.schedule_boards if b.title == board_name and not getattr(b, 'deleted', False)), None)
            return self.analyze_board
        except Exception as e:
            self.logger.error(f"Ошибка при получении доски анализа: {e}")
            return None

    def get_analyze_columns(self, board_name: Optional[str] = "Анализ расписания") -> List[Column]:
        """Получение колонок доски анализа."""
        try:
            self.get_analyze_board(board_name)
            if not self.analyze_board:
                return []
            self.get_schedule_columns()
            self.analyze_columns = [c for c in self.schedule_columns if c.board_id == self.analyze_board.id and not getattr(c, 'deleted', False)]
            self.logger.info(f"Найдено колонок анализа: {len(self.analyze_columns)}")
            return self.analyze_columns
        except Exception as e:
            self.logger.error(f"Ошибка при получении колонок анализа: {e}")
            return []

    def get_analyze_tasks(self) -> List[Task]:
        """Получение задач доски анализа."""
        try:
            self.get_analyze_columns()
            if not self.analyze_board:
                return []
            self.get_schedule_tasks()
            column_ids = {c.id for c in self.analyze_columns}
            self.analyze_tasks = [t for t in self.schedule_tasks if t.column_id in column_ids and not getattr(t, 'deleted', False)]
            self.logger.info(f"Найдено задач анализа: {len(self.analyze_tasks)}")
            return self.analyze_tasks
        except Exception as e:
            self.logger.error(f"Ошибка при получении задач анализа: {e}")
            return []

    def create_schedule_analyzing_board(self, analyze_board_name: Optional[str] = "Анализ расписания") -> Optional[Board]:
        """Создание доски для анализа."""
        try:
            self.logger.info(f"Создание доски анализа: {analyze_board_name}")
            self.get_schedule_project()
            if not self.schedule_project:
                self.create_schedule_project()
            self.get_analyze_board(analyze_board_name)
            if not self.analyze_board:
                self.get_schedule_stickers()
                custom_stickers = {s.id: True for s in self.schedule_stickers}
                stickers = {
                    "timer": False,
                    "deadline": True,
                    "stopwatch": True,
                    "timeTracking": False,
                    "assignee": True,
                    "repeat": False,
                    "custom": custom_stickers
                }
                create_response = self._api_call_with_retry(
                    self.client.boards.create,
                    title=analyze_board_name,
                    project_id=self.schedule_project.id,
                    stickers=stickers
                )
                board_id = create_response.get('id')
                if not board_id:
                    self.logger.error("Не получен ID созданной доски")
                    return None
                # Получаем полные данные доски
                board_data = self._api_call_with_retry(self.client.boards.get, id=board_id)
                self.analyze_board = Board.model_validate(board_data)
                self._boards_cache[self.analyze_board.id] = self.analyze_board
                self.get_schedule_boards()
                self.logger.info(f"Доска создана: {self.analyze_board.title} (ID: {self.analyze_board.id})")
            else:
                self._clean_up_board(self.analyze_board.id)
            return self.analyze_board
        except Exception as e:
            self.logger.error(f"Ошибка при создании доски анализа: {e}")
            return None

    def create_schedule_analyzing_columns(self, board_id: str) -> List[Column]:
        """Создание колонок для анализа."""
        try:
            self.logger.info("Создание колонок анализа")
            self.get_analyze_columns()
            titles = [f"Неделя {w}" for w in range(22)] + ["Найденные окна"]
            for title in titles:
                if not any(c.title == title and c.board_id == board_id for c in self.analyze_columns):
                    week = int(title.split()[1]) if "Неделя" in title else 13
                    create_response = self._api_call_with_retry(
                        self.client.columns.create,
                        title=title,
                        board_id=board_id,
                        color=(week % 16) + 1
                    )
                    column_id = create_response.get('id')
                    if not column_id:
                        self.logger.error(f"Не получен ID колонки '{title}'")
                        continue
                    # Получаем полные данные колонки
                    column_data = self._api_call_with_retry(self.client.columns.get, id=column_id)
                    column = Column.model_validate(column_data)
                    self._columns_cache[column.id] = column
            self.get_schedule_columns()
            self.logger.info(f"Всего колонок: {len(self.schedule_columns)}")
            return self.schedule_columns
        except Exception as e:
            self.logger.error(f"Ошибка при создании колонок анализа: {e}")
            return []

    def create_schedule_analyzing_tasks(self, board_id: str) -> List[Task]:
        """Создание задач для анализа."""
        try:
            self.logger.info("Создание задач анализа")
            created_tasks = 0
            self.get_schedule_tasks()
            for task in self.schedule_tasks:
                week = next((int(c.title.split()[1]) for c in self.schedule_columns if c.id == task.column_id and "Неделя" in c.title), None)
                if week is not None:
                    column = self._get_column_by_week(week, board_id)
                    if column:
                        task_data = {"title": task.title, "column_id": column.id}
                        if task.deadline:
                            task_data["deadline"] = task.deadline
                        if task.stickers:
                            task_data["stickers"] = task.stickers
                        if task.description:
                            task_data["description"] = task.description
                        create_response = self._api_call_with_retry(self.client.tasks.create, **task_data)
                        task_id = create_response.get('id')
                        if not task_id:
                            self.logger.error(f"Не получен ID задачи '{task.title}'")
                            continue
                        # Получаем полные данные задачи
                        task_data = self._api_call_with_retry(self.client.tasks.get, id=task_id)
                        task = Task.model_validate(task_data)
                        self._tasks_cache[task.id] = task
                        created_tasks += 1
            self.get_schedule_tasks()
            self.logger.info(f"Создано задач: {created_tasks}")
            return self.schedule_tasks
        except Exception as e:
            self.logger.error(f"Ошибка при создании задач анализа: {e}")
            return []

    def init_analyze(self, analyze_board_name: Optional[str] = "Анализ расписания"):
        """Инициализация доски анализа."""
        self.analyze_board = self.create_schedule_analyzing_board(analyze_board_name)
        if self.analyze_board:
            self.create_schedule_analyzing_columns(self.analyze_board.id)

    def copy_tasks_to_analysis_board(self, board_name: str):
        """Копирование задач на доску анализа."""
        try:
            self.logger.info("Копирование задач на доску анализа")
            self.get_analyze_board()
            if not self.analyze_board:
                self.create_schedule_analyzing_board()
            if not self.analyze_board:
                return
            self.get_schedule_tasks()
            board = next((b for b in self.schedule_boards if board_name == b.title), None)
            if not board:
                return
            column_ids = {c.id for c in self.schedule_columns if c.board_id == board.id}
            copied_count = 0
            for task in self.schedule_tasks:
                if task.column_id in column_ids:
                    week = next((int(c.title.split()[1]) for c in self.schedule_columns if c.id == task.column_id and "Неделя" in c.title), None)
                    if week is not None:
                        column = self._get_column_by_week(week, self.analyze_board.id)
                        if column:
                            task_data = {
                                "title": task.title,
                                "column_id": column.id,
                                "description": getattr(task, 'description', '')
                            }
                            if hasattr(task, 'deadline') and task.deadline:
                                task_data["deadline"] = task.deadline
                            if hasattr(task, 'stickers') and task.stickers:
                                task_data["stickers"] = task.stickers
                            create_response = self._api_call_with_retry(self.client.tasks.create, **task_data)
                            task_id = create_response.get('id')
                            if not task_id:
                                self.logger.error(f"Не получен ID задачи '{task.title}'")
                                continue
                            # Получаем полные данные задачи
                            task_data = self._api_call_with_retry(self.client.tasks.get, id=task_id)
                            task = Task.model_validate(task_data)
                            self._tasks_cache[task.id] = task
                            copied_count += 1
            self.get_schedule_tasks()
            self.logger.info(f"Скопировано задач: {copied_count}")
        except Exception as e:
            self.logger.error(f"Ошибка при копировании задач: {e}")