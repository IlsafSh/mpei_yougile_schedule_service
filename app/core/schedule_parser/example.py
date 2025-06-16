"""
------------------------------------------------------------
MPEIRuzParser - Обновленный пример использования
------------------------------------------------------------
Пример использования класса для парсинга расписания
------------------------------------------------------------
"""

from schedule_parser.ScheduleParser import MPEIRuzParser
import logging
import sys
import json


def main():
    ## Пример парсинга расписания для учебной группы
    # Создание экземпляра парсера
    parser = MPEIRuzParser(
        headless=True,  # Запуск парсинга в видимом/невидимом режиме
        cleanup_files=False,  # Очистить/Сохранять вспомогательные файлы
        max_weeks=21
    )

    try:
        # Парсинг расписания для группы
        schedule = parser.parse(
            name="ЭР-05-24",
            schedule_type="group",
            save_to_file=True,
            filename="data/json_schedules/schedule_group_ER-05-24.json"
        )

        # Обработка результатов
        if schedule:
            print(f"Успешно получено расписание. Количество дней: {len(schedule)}")
        else:
            print("Не удалось получить расписание")
    finally:
        # Закрываем браузер
        parser.close()

if __name__ == "__main__":
    main()