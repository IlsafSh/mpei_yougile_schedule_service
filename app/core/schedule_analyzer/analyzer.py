"""
Модуль для анализа расписания и поиска окон в YouGile.

Предоставляет класс ScheduleAnalyzer для анализа расписания, поиска свободных окон
различными алгоритмами и создания отчетов в YouGile.
"""

import logging
from datetime import datetime, timedelta, date, time
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from intervaltree import IntervalTree
import holidays

from yougile_integration.yougile_integrator import ScheduleIntegrator


class WindowType(Enum):
    """Типы окон для поиска."""
    COMMON_WINDOW = "common_window"
    SPLIT_WINDOW = "split_window"


@dataclass
class TimeSlot:
    """Временной слот для занятия."""
    start: datetime
    end: datetime
    title: str
    description: str = ""
    board_name: str = ""

    def duration_hours(self) -> float:
        """Возвращает продолжительность слота в часах."""
        return (self.end - self.start).total_seconds() / 3600

    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """Проверяет пересечение с другим временным слотом."""
        return self.start < other.end and self.end > other.start


@dataclass
class Window:
    """Найденное окно в расписании."""
    start: datetime
    end: datetime
    duration_hours: float
    window_type: WindowType
    description: str
    participants: List[str] = None
    days_count: int = 1

    def to_task_data(self) -> Dict[str, Any]:
        """Преобразует окно в данные для создания задачи в YouGile."""
        start_timestamp = int(self.start.timestamp() * 1000)
        end_timestamp = int(self.end.timestamp() * 1000)

        title = f"Окно {self.duration_hours:.1f}ч"
        if self.days_count > 1:
            title += f" ({self.days_count} дн.)"

        description_parts = [
            f"Тип: {self.window_type.value}",
            f"Начало: {self.start.strftime('%d.%m.%Y %H:%M')}",
            f"Конец: {self.end.strftime('%d.%m.%Y %H:%M')}",
            f"Продолжительность: {self.duration_hours:.1f} часов",
            self.description
        ]
        if self.participants:
            description_parts.append(f"Участники: {', '.join(self.participants)}")

        return {
            "title": title,
            "description": "\n".join(description_parts),
            "deadline": {
                "deadline": end_timestamp,
                "startDate": start_timestamp,
                "withTime": True
            }
        }


class ScheduleAnalyzer:
    """
    Класс для анализа расписания и поиска окон в YouGile.

    Использует различные алгоритмы для поиска свободных окон и создаёт задачи
    в YouGile для отображения результатов анализа.
    """

    def __init__(self, integrator: ScheduleIntegrator):
        """
        Инициализация анализатора.

        Args:
            integrator: Экземпляр ScheduleIntegrator.
        """
        self.integrator = integrator
        self.logger = logging.getLogger('ScheduleAnalyzer')
        self._setup_logging()

        # Кэши
        self._time_slots_cache: Dict[str, List[TimeSlot]] = {}
        self._windows_column_cache: Optional[str] = None

        # Ограничения по времени
        self.weekend_days = {5, 6}  # Суббота, воскресенье (0=понедельник)
        self.holidays = self._get_holidays()

    def _setup_logging(self):
        """Настройка логирования."""
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def _get_holidays(self) -> Set[date]:
        """Получение праздничных дней для России на 2025 год."""
        try:
            ru_holidays = holidays.RU(years=2025)
            return set(ru_holidays.keys())
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке праздников: {e}")
            return set()

    def _get_board_id(self, board_name: str) -> Optional[str]:
        """Получение ID доски по её названию."""
        for board in self.integrator.schedule_boards:
            if board.title == board_name:
                return board.id
        self.logger.warning(f"Доска '{board_name}' не найдена")
        return None

    def _get_windows_column_id(self) -> Optional[str]:
        """Получение ID колонки 'Найденные окна' из кэша или API."""
        if self._windows_column_cache:
            return self._windows_column_cache

        self.integrator.get_analyze_columns()
        for column in self.integrator.analyze_columns:
            if column.title == "Найденные окна":
                self._windows_column_cache = column.id
                return column.id

        self.logger.warning("Колонка 'Найденные окна' не найдена")
        return None

    def load_time_slots(self, board_name: str) -> List[TimeSlot]:
        """
        Загружает временные слоты из задач указанной доски.

        Args:
            board_name: Название доски для загрузки слотов.

        Returns:
            List[TimeSlot]: Список временных слотов.
        """
        if board_name in self._time_slots_cache:
            self.logger.info(f"Загружено {len(self._time_slots_cache[board_name])} слотов из кэша для доски '{board_name}'")
            return self._time_slots_cache[board_name]

        try:
            self.logger.info(f"Загрузка временных слотов для доски '{board_name}'")
            self.integrator.get_schedule_tasks()
            board_id = self._get_board_id(board_name)
            if not board_id:
                return []

            # Фильтруем задачи по доске
            column_ids = {c.id for c in self.integrator.schedule_columns if c.board_id == board_id}
            time_slots = []

            for task in self.integrator.schedule_tasks:
                if task.column_id not in column_ids:
                    continue

                try:
                    if not hasattr(task, 'deadline') or not task.deadline:
                        continue

                    deadline = task.deadline
                    if not isinstance(deadline, dict):
                        continue

                    start_timestamp = deadline.get('startDate')
                    end_timestamp = deadline.get('deadline')
                    if not start_timestamp or not end_timestamp:
                        continue

                    start_dt = datetime.fromtimestamp(start_timestamp / 1000)
                    end_dt = datetime.fromtimestamp(end_timestamp / 1000)

                    time_slot = TimeSlot(
                        start=start_dt,
                        end=end_dt,
                        title=task.title,
                        description=getattr(task, 'description', ''),
                        board_name=board_name
                    )
                    time_slots.append(time_slot)

                except Exception as e:
                    self.logger.warning(f"Ошибка при обработке задачи '{task.title}': {e}")

            time_slots.sort(key=lambda x: x.start)
            self._time_slots_cache[board_name] = time_slots
            self.logger.info(f"Загружено {len(time_slots)} временных слотов для доски '{board_name}'")
            return time_slots

        except Exception as e:
            self.logger.error(f"Ошибка при загрузке слотов для доски '{board_name}': {e}")
            return []

    def is_working_time(self, dt: datetime, earliest_start_hour: int, latest_end_hour: int) -> bool:
        """
        Проверяет, является ли указанное время рабочим.

        Args:
            dt: Проверяемое время.
            earliest_start_hour: Начало рабочего времени.
            latest_end_hour: Конец рабочего времени.

        Returns:
            bool: True, если время рабочее.
        """
        if dt.hour < earliest_start_hour or dt.hour >= latest_end_hour:
            return False
        if dt.weekday() in self.weekend_days:
            return False
        if dt.date() in self.holidays:
            return False
        return True

    def is_time_slot_free(self, start: datetime, end: datetime, exclude_boards: Optional[Set[str]] = None) -> bool:
        """
        Проверяет, свободен ли временной слот.

        Args:
            start: Начало слота.
            end: Конец слота.
            exclude_boards: Множество названий досок для исключения.

        Returns:
            bool: True, если слот свободен.
        """
        test_slot = TimeSlot(start=start, end=end, title="test")
        exclude_boards = exclude_boards or set()

        for board_name, slots in self._time_slots_cache.items():
            if board_name in exclude_boards:
                continue
            for slot in slots:
                if test_slot.overlaps_with(slot):
                    return False
        return True

    def find_split_window(self, start_date: date, end_date: date, total_duration: float,
                           min_segment_duration: float, max_segments: int, participants: List[str],
                           earliest_start_time: time = time(hour=7, minute=0),
                           latest_end_time: time = time(hour=23, minute=0), min_gap_hours: float = 0.0,
                           maximize_participants: bool = True, minimize_start_time: bool = True,
                           minimize_total_idle: bool = True, minimize_max_gap: bool = True,
                           include_holidays: bool = False, include_weekends: bool = False,
                           weight_participants: float = 1.0, weight_start_time: float = 1.0,
                           weight_total_idle: float = 1.0, weight_max_gap: float = 1.0) -> Optional[Window]:
        """
        Алгоритм поиска сплит-окна заданной общей продолжительностью.

        Args:
            start_date: Начальная дата поиска.
            end_date: Конечная дата поиска.
            total_duration: Общая продолжительность сплит-окна в часах.
            min_segment_duration: Минимальная продолжительность сегмента в часах.
            max_segments: Максимальное количество сегментов.
            participants: Список названий досок участников.
            earliest_start_time: Начало рабочего времени (время).
            latest_end_time: Конец рабочего времени (время).
            min_gap_hours: Минимальный промежуток между занятиями (часы).
            maximize_participants: Учитывать максимизацию участников.
            minimize_start_time: Учитывать минимизацию времени начала.
            minimize_total_idle: Учитывать минимизацию суммарного простоя.
            minimize_max_gap: Учитывать минимизацию максимального промежутка.
            include_holidays: Включать праздничные дни.
            include_weekends: Включать выходные дни.

        Returns:
            Window: Найденное окно или None.
        """
        try:
            self.logger.info(f"Поиск сплит-окна с {start_date} по {end_date} для участников: {participants}")
            if not participants or total_duration <= 0 or min_segment_duration <= 0 or \
               earliest_start_time >= latest_end_time or max_segments < 1:
                self.logger.warning("Некорректные входные параметры для сплит-окна")
                return None

            # Загрузка временных слотов
            for participant in participants:
                self.load_time_slots(participant)

            possible_split_windows = []
            current_date = start_date

            while current_date <= end_date:
                if (not include_holidays and current_date in self.holidays) or \
                   (not include_weekends and current_date.weekday() in self.weekend_days):
                    current_date += timedelta(days=1)
                    continue

                day_start_dt = datetime.combine(current_date, earliest_start_time)
                day_end_dt = datetime.combine(current_date, latest_end_time)

                # Генерируем все возможные сегменты в течение дня
                segments = []
                t = day_start_dt
                while t <= day_end_dt:
                    segment_end = t + timedelta(hours=min_segment_duration)
                    if segment_end <= day_end_dt:
                        segments.append((t, segment_end))
                    t += timedelta(minutes=min_gap_hours if min_gap_hours else 15) # Шаг в 15 минут для генерации сегментов

                # Поиск комбинаций сегментов
                for num_segments in range(1, max_segments + 1):
                    for segment_combination in combinations(segments, num_segments):
                        # Проверяем, что сегменты не пересекаются и идут по порядку
                        is_valid_combination = True
                        combined_duration = 0.0
                        current_end = None
                        for seg_start, seg_end in segment_combination:
                            if current_end and seg_start < current_end:
                                is_valid_combination = False
                                break
                            combined_duration += (seg_end - seg_start).total_seconds() / 3600
                            current_end = seg_end

                        if not is_valid_combination or combined_duration < total_duration:
                            continue

                        # Проверяем, что все сегменты свободны для всех участников
                        all_segments_free = True
                        for participant_subset in combinations(participants, len(participants)):
                            adjusted_tree = self._build_adjusted_tree(set(participant_subset), min_gap_hours)
                            for seg_start, seg_end in segment_combination:
                                if adjusted_tree.overlap(seg_start, seg_end):
                                    all_segments_free = False
                                    break
                            if not all_segments_free: break

                        if not all_segments_free:
                            continue

                        # Если комбинация валидна и свободна, создаем сплит-окно
                        split_window_start = segment_combination[0][0]
                        split_window_end = segment_combination[-1][1]

                        window = Window(
                            start=split_window_start,
                            end=split_window_end,
                            duration_hours=combined_duration,
                            window_type=WindowType.SPLIT_WINDOW,
                            description=f"Сплит-окно для участников: {', '.join(participants)}",
                            participants=list(participants),
                            days_count=(split_window_end.date() - split_window_start.date()).days + 1
                        )
                        possible_split_windows.append(window)

                current_date += timedelta(days=1)

            if not possible_split_windows:
                self.logger.info("Сплит-окно не найдено")
                return None

            # Оценка и выбор лучшего сплит-окна
            now = datetime.combine(start_date, earliest_start_time)
            best_split_window = max(
                possible_split_windows,
                key=lambda w: self._score_window(
                    w, now, participants, maximize_participants,
                    minimize_start_time, minimize_total_idle, minimize_max_gap, earliest_start_time, latest_end_time,
                    weight_participants, weight_start_time, weight_total_idle, weight_max_gap
                )
            )

            self.logger.info(f"Найдено сплит-окно: {best_split_window.start} - {best_split_window.end} для участников: {best_split_window.participants}")
            return best_split_window

        except Exception as e:
            self.logger.error(f"Ошибка при поиске сплит-окна: {e}")
            return None

    def _build_adjusted_tree(self, participants: Set[str], min_gap_hours: float) -> IntervalTree:
        """
        Создает интервальное дерево с интервалами, расширенными на min_gap_hours.

        Args:
            participants: Множество участников.
            min_gap_hours: Минимальный промежуток в часах.

        Returns:
            IntervalTree: Дерево с расширенными интервалами.
        """
        tree = IntervalTree()
        gap = timedelta(hours=min_gap_hours)
        for participant in participants:
            for slot in self._time_slots_cache.get(participant, []):
                adjusted_start = slot.start - gap
                adjusted_end = slot.end + gap
                tree.addi(adjusted_start, adjusted_end)
        return tree

    def find_common_window(self, start_date: date, end_date: date, required_duration: float,
                           participants: List[str], earliest_start_time: time = time(hour=7, minute=0),
                           latest_end_time: time = time(hour=23, minute=0), min_gap_hours: float = 0.0,
                           maximize_participants: bool = True, minimize_start_time: bool = True,
                           minimize_total_idle: bool = True, minimize_max_gap: bool = True,
                           include_holidays: bool = False, include_weekends: bool = False,
                           weight_participants: float = 1.0, weight_start_time: float = 1.0,
                           weight_total_idle: float = 1.0, weight_max_gap: float = 1.0) -> Optional[Window]:
        """
        Находит общее окно строго заданной продолжительности для участников.

        Args:
            start_date: Начальная дата поиска.
            end_date: Конечная дата поиска.
            required_duration: Точная продолжительность окна в часах.
            participants: Список названий досок участников.
            earliest_start_time: Начало рабочего времени (время).
            latest_end_time: Конец рабочего времени (время).
            min_gap_hours: Минимальный промежуток между занятиями (часы).
            maximize_participants: Учитывать максимизацию участников.
            minimize_start_time: Учитывать минимизацию времени начала.
            minimize_total_idle: Учитывать минимизацию суммарного простоя.
            minimize_max_gap: Учитывать минимизацию максимального промежутка.
            include_holidays: Включать праздничные дни.
            include_weekends: Включать выходные дни.

        Returns:
            Window: Найденное окно или None.
        """
        try:
            self.logger.info(f"Поиск окна с {start_date} по {end_date} для участников: {participants}")
            if not participants or required_duration <= 0 or earliest_start_time >= latest_end_time:
                self.logger.warning("Некорректные входные параметры")
                return None

            # Загрузка временных слотов
            for participant in participants:
                self.load_time_slots(participant)

            possible_windows = []
            if maximize_participants and len(participants) > 1:
                for r in range(len(participants), 0, -1):
                    for subset in combinations(participants, r):
                        subset = set(subset)
                        windows = self._find_windows_for_subset(
                            subset, required_duration, start_date, end_date,
                            earliest_start_time, latest_end_time, min_gap_hours,
                            include_holidays, include_weekends
                        )
                        possible_windows.extend(windows)
            else:
                windows = self._find_windows_for_subset(
                    set(participants), required_duration, start_date, end_date,
                    earliest_start_time, latest_end_time, min_gap_hours,
                    include_holidays, include_weekends
                )
                possible_windows.extend(windows)

            if not possible_windows:
                self.logger.info("Общее окно не найдено")
                return None

            now = datetime.combine(start_date, earliest_start_time)
            best_window = max(
                possible_windows,
                key=lambda w: self._score_window(
                    w, now, participants, maximize_participants,
                    minimize_start_time, minimize_total_idle, minimize_max_gap, earliest_start_time, latest_end_time,
                    weight_participants, weight_start_time, weight_total_idle, weight_max_gap
                )
            )

            self.logger.info(f"Найдено окно: {best_window.start} - {best_window.end} для участников: {best_window.participants}")
            return best_window

        except Exception as e:
            self.logger.error(f"Ошибка при поиске окна: {e}")
            return None

    def _find_windows_for_subset(self, subset: Set[str], required_duration: float,
                                 start_date: date, end_date: date, earliest_start_time: time,
                                 latest_end_time: time, min_gap_hours: float,
                                 include_holidays: bool, include_weekends: bool) -> List[Window]:
        """
        Находит окна строго заданной продолжительности для подмножества участников.

        Args:
            subset: Множество участников.
            required_duration: Точная продолжительность окна в часах.
            start_date: Начальная дата поиска.
            end_date: Конечная дата поиска.
            earliest_start_time: Начало рабочего времени (время).
            latest_end_time: Конец рабочего времени (время).
            min_gap_hours: Минимальный промежуток между занятиями (часы).
            include_holidays: Включать праздничные дни.
            include_weekends: Включать выходные дни.

        Returns:
            List[Window]: Список найденных окон.
        """
        windows = []
        adjusted_tree = self._build_adjusted_tree(subset, min_gap_hours)
        current_date = start_date

        while current_date <= end_date:
            if (not include_holidays and current_date in self.holidays) or \
               (not include_weekends and current_date.weekday() in self.weekend_days):
                current_date += timedelta(days=1)
                continue

            day_start = datetime.combine(current_date, earliest_start_time)
            day_end = datetime.combine(current_date, latest_end_time)

            t = day_start
            while t <= day_end:
                window_end = t + timedelta(hours=required_duration)
                if window_end < day_end:
                    if not adjusted_tree.overlap(t, window_end):
                        window = Window(
                            start=t,
                            end=window_end,
                            duration_hours=required_duration,
                            window_type=WindowType.COMMON_WINDOW,
                            description=f"Общее окно для участников: {', '.join(subset)}",
                            participants=list(subset)
                        )
                        windows.append(window)
                t += timedelta(minutes=min_gap_hours if min_gap_hours else 15)

            current_date += timedelta(days=1)

        return windows

    def _score_window(self, window: Window, time: datetime, participants: List[str],
                      maximize_participants: bool, minimize_start_time: bool,
                      minimize_total_idle: bool, minimize_max_gap: bool,
                      earliest_start_time: time, latest_end_time: time,
                      weight_participants: float = 1.0, weight_start_time: float = 1.0,
                      weight_total_idle: float = 1.0, weight_max_gap: float = 1.0) -> float:
        """
        Оценивает окно на основе заданных критериев с нормализацией и весами.

        Args:
            window: Окно для оценки.
            time: Время отсчета.
            participants: Список всех возможных участников.
            maximize_participants: Учитывать количество участников.
            minimize_start_time: Учитывать время начала.
            minimize_total_idle: Учитывать суммарное время простоя.
            minimize_max_gap: Учитывать максимальный промежуток.
            earliest_start_time: Начало рабочего дня (время).
            latest_end_time: Конец рабочего дня (время).
            weight_participants: Вес критерия количества участников.
            weight_start_time: Вес критерия времени начала.
            weight_total_idle: Вес критерия суммарного простоя.
            weight_max_gap: Вес критерия максимального промежутка.

        Returns:
            float: Оценка окна (чем выше, тем лучше).
        """
        score = 0.0
        max_possible_participants = len(participants)
        max_start_delay_hours = 24.0  # Максимальная задержка (1 день)
        # Вычисление длительности рабочего дня в часах
        work_day_duration = (
                                    datetime.combine(time.date(), latest_end_time) -
                                    datetime.combine(time.date(), earliest_start_time)
                            ).total_seconds() / 3600
        max_possible_gap = work_day_duration  # Максимальный промежуток в рабочем дне
        max_idle_per_participant = work_day_duration * 2  # Максимальный простой на участника

        if maximize_participants and max_possible_participants > 0:
            participants_score = len(window.participants) / max_possible_participants
            score += participants_score * weight_participants

        if minimize_start_time:
            start_delay = (window.start - time).total_seconds() / 3600
            start_time_score = 1.0 - min(start_delay / max_start_delay_hours, 1.0)
            score += start_time_score * weight_start_time

        if minimize_total_idle:
            total_idle = sum(
                (window.start - self._get_last_slot_end_before(p, window.start,
                                                               earliest_start_time)).total_seconds() / 3600 +
                (self._get_next_slot_start_after(p, window.end, latest_end_time) - window.end).total_seconds() / 3600
                for p in window.participants
            )
            total_idle_score = 1.0 - min(total_idle / (max_idle_per_participant * len(window.participants)), 1.0)
            score += total_idle_score * weight_total_idle

        if minimize_max_gap:
            max_gap = max(
                max(
                    (window.start - self._get_last_slot_end_before(p, window.start,
                                                                   earliest_start_time)).total_seconds() / 3600,
                    (self._get_next_slot_start_after(p, window.end,
                                                     latest_end_time) - window.end).total_seconds() / 3600
                )
                for p in window.participants
            )
            max_gap_score = 1.0 - min(max_gap / max_possible_gap, 1.0)
            score += max_gap_score * weight_max_gap

        return score

    def _get_last_slot_end_before(self, participant: str, before_time: datetime, earliest_start_time: time) -> datetime:
        """
        Находит время окончания последнего слота перед указанным временем в тот же день.

        Args:
            participant: Название доски участника.
            before_time: Время, до которого искать слот.
            earliest_start_time: Начало рабочего дня (время).

        Returns:
            datetime: Время окончания последнего слота или начало рабочего дня.
        """
        day = before_time.date()
        slots = self._time_slots_cache.get(participant, [])
        past_slots = [slot for slot in slots if slot.end <= before_time and slot.end.date() == day]
        if past_slots:
            return max(slot.end for slot in past_slots)
        else:
            return datetime.combine(day, earliest_start_time)

    def _get_next_slot_start_after(self, participant: str, after_time: datetime, latest_end_time: time) -> datetime:
        """
        Находит время начала ближайшего слота после указанного времени в тот же день.

        Args:
            participant: Название доски участника.
            after_time: Время, после которого искать слот.
            latest_end_time: Конец рабочего дня (время).

        Returns:
            datetime: Время начала ближайшего слота или конец рабочего дня.
        """
        day = after_time.date()
        slots = self._time_slots_cache.get(participant, [])
        future_slots = [slot for slot in slots if slot.start >= after_time and slot.start.date() == day]
        if future_slots:
            return min(slot.start for slot in future_slots)
        else:
            return datetime.combine(day, latest_end_time)

    def create_analysis_board(self) -> bool:
        """
        Создаёт доску 'Анализ расписания' в проекте с расписанием.

        Returns:
            bool: True, если доска создана или уже существует.
        """
        try:
            self.logger.info("Создание доски анализа")
            self.integrator.init_analyze()
            if self.integrator.analyze_board:
                self.logger.info(f"Доска анализа '{self.integrator.analyze_board.title}' готова")
                return True
            self.logger.error("Не удалось создать доску анализа")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при создании доски анализа: {e}")
            return False

    def create_window_task(self, window: Window) -> bool:
        """
        Создаёт задачу для найденного окна в колонке 'Найденные окна'.

        Args:
            window: Найденное окно.

        Returns:
            bool: True, если задача создана успешно.
        """
        try:
            column_id = self._get_windows_column_id()
            if not column_id:
                return False

            task_data = window.to_task_data()
            task_data["column_id"] = column_id

            create_response = self.integrator._api_call_with_retry(self.integrator.client.tasks.create, **task_data)
            task_id = create_response.get('id')
            if not task_id:
                self.logger.error("Не получен ID созданной задачи для окна")
                return False

            # Получаем полные данные задачи для кэша
            task_data = self.integrator._api_call_with_retry(self.integrator.client.tasks.get, id=task_id)
            self.integrator._tasks_cache[task_id] = task_data
            self.logger.info(f"Создана задача для окна: {window.start} - {window.end}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка при создании задачи для окна: {e}")
            return False

    def analyze_schedule(self, algorithms: Optional[List[Dict[str, Any]]] = None, board_names: Optional[List[str]] = None) -> List[Window]:
        """
        Выполняет анализ расписания с использованием указанных алгоритмов.

        Args:
            algorithms: Список конфигураций алгоритмов.
            board_names: Список названий досок для анализа.

        Returns:
            List[Window]: Список найденных окон.
        """
        try:
            self.logger.info("Начало анализа расписания")
            if not self.create_analysis_board():
                return []

            board_names = board_names or [board.title for board in self.integrator.schedule_boards]
            found_windows = []

            # Загружаем слоты для всех досок
            for board_name in board_names:
                self.integrator.copy_tasks_to_analysis_board(board_name)
                self.load_time_slots(board_name)

            # Выполняем алгоритмы
            for algo_config in algorithms:
                algo_type = algo_config.get("type")
                try:
                    window = None
                    if algo_type == "split_window":
                        window = self.find_split_window(
                            start_date=algo_config.get("start_date"),
                            end_date=algo_config.get("end_date"),
                            total_duration=algo_config.get("total_duration", 4.0),
                            min_segment_duration=algo_config.get("min_segment_duration", 0.5),
                            max_segments=algo_config.get("max_segments", 5),
                            participants=algo_config.get("participants", board_names),
                            earliest_start_time=algo_config.get("earliest_start_time", time(hour=7, minute=0)),
                            latest_end_time=algo_config.get("latest_end_time", time(hour=23, minute=0)),
                            min_gap_hours=algo_config.get("min_gap_hours", 0.0),
                            maximize_participants=algo_config.get("maximize_participants", True),
                            minimize_start_time=algo_config.get("minimize_start_time", True),
                            minimize_total_idle=algo_config.get("minimize_total_idle", True),
                            minimize_max_gap=algo_config.get("minimize_max_gap", True),
                            include_holidays=algo_config.get("include_holidays", False),
                            include_weekends=algo_config.get("include_weekends", False),
                            weight_participants=algo_config.get("weight_participants", 1.0),
                            weight_start_time=algo_config.get("weight_start_time", 1.0),
                            weight_total_idle=algo_config.get("weight_total_idle", 1.0),
                            weight_max_gap=algo_config.get("weight_max_gap", 1.0)
                        )
                    elif algo_type == "common_window":
                        window = self.find_common_window(
                            start_date=algo_config.get("start_date"),
                            end_date=algo_config.get("end_date"),
                            required_duration=algo_config.get("required_duration", 1.0),
                            participants=algo_config.get("participants", board_names),
                            earliest_start_time=algo_config.get("earliest_start_time", time(hour=7, minute=0)),
                            latest_end_time=algo_config.get("latest_end_time", time(hour=23, minute=0)),
                            min_gap_hours=algo_config.get("min_gap_hours", 0.0),
                            maximize_participants=algo_config.get("maximize_participants", True),
                            minimize_start_time=algo_config.get("minimize_start_time", True),
                            minimize_total_idle=algo_config.get("minimize_total_idle", True),
                            minimize_max_gap=algo_config.get("minimize_max_gap", True),
                            include_holidays=algo_config.get("include_holidays", False),
                            include_weekends=algo_config.get("include_weekends", False),
                            weight_participants=algo_config.get("weight_participants", 1.0),
                            weight_start_time=algo_config.get("weight_start_time", 1.0),
                            weight_total_idle=algo_config.get("weight_total_idle", 1.0),
                            weight_max_gap=algo_config.get("weight_max_gap", 1.0)
                        )
                    else:
                        self.logger.warning(f"Неизвестный тип алгоритма: {algo_type}")
                        continue

                    if window:
                        found_windows.append(window)
                        self.create_window_task(window)

                except Exception as e:
                    self.logger.error(f"Ошибка при выполнении алгоритма '{algo_type}': {e}")

            self.logger.info(f"Анализ завершён. Найдено окон: {len(found_windows)}")
            return found_windows

        except Exception as e:
            self.logger.error(f"Ошибка при анализе расписания: {e}")
            return []