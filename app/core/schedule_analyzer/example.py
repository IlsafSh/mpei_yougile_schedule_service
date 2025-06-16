"""
------------------------------------------------------------
ScheduleAnalyzer - Обновленный пример использования
------------------------------------------------------------
Примеры использования алгоритмов анализа расписания
------------------------------------------------------------
"""

from analyzer import ScheduleAnalyzer
from yougile_integration.yougile_integrator import ScheduleIntegrator
from yougile_integration.yougile_api_wrapper import YouGileClient
from datetime import datetime, timedelta, date, time


def main():

    # Данные учетной записи YouGile
    login = "parov.duvel@mail.ru"
    password = "pavel123"

    client = YouGileClient(login=login, password=password)
    client.set_token(
        client.auth.get_keys(
            login, password, client.auth.get_companies(login, password)['content'][0].get('id')
        )[0].get('key')
    )

    integrator = ScheduleIntegrator(client)

    analyzer = ScheduleAnalyzer(integrator)

    # Входные параметры для анализа алгоритма поиска общего окна
    type = "common_window"
    start_date = date(2025, 6, 9)
    end_date = date(2025, 6, 10)
    required_duration = 1.0
    min_gap_hours = 0.05
    earliest_start_time = time(hour=9, minute=0)
    latest_end_time = time(hour=20, minute=0)
    include_holidays = False
    include_weekends = False
    maximize_participants = True
    weight_participants = 1.0
    minimize_start_time = True
    weight_start_time = 1.0
    minimize_total_idle = True
    weight_total_idle = 1.0
    minimize_max_gap = True
    weight_max_gap = 1.0
    board_names = ['А-08-24-short']
    participants = board_names[:2]      # Задается от одного до нескольких расписаний/досок в проекте YouGile

    algorithms = [{
            "type": type,
            "start_date": start_date,
            "end_date": end_date,
            "required_duration": required_duration,
            "participants": participants,
            "earliest_start_time": earliest_start_time,
            "latest_end_time": latest_end_time,
            "min_gap_hours": min_gap_hours,
            "include_holidays": include_holidays,
            "include_weekends": include_weekends,
            "maximize_participants": maximize_participants,
            "minimize_start_time": minimize_start_time,
            "minimize_total_idle": minimize_total_idle,
            "minimize_max_gap": minimize_max_gap,
            "weight_participants": weight_participants,
            "weight_start_time": weight_start_time,
            "weight_total_idle": weight_total_idle,
            "weight_max_gap": weight_max_gap
    }]

    analyzer.analyze_schedule(algorithms, board_names=board_names)

if __name__ == "__main__":
    main()