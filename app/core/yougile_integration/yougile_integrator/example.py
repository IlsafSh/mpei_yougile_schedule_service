from integrator import ScheduleIntegrator
from yougile_integration.yougile_api_wrapper.yougile_api import YouGileClient


def main():

    login = "parov.duvel@mail.ru"
    password = "pavel123"

    client = YouGileClient(login=login, password=password)
    client.set_token(
        client.auth.get_keys(
            login, password, client.auth.get_companies(login, password)['content'][0].get('id')
        )[0].get('key')
    )

    # parser = MPEIRuzParser(
    #     headless=True,  # Запуск парсинга в видимом/невидимом режиме
    #     cleanup_files=False,  # Очистить/Сохранять вспомогательные файлы
    #     max_weeks=15
    # )
    # schedule_data = parser.parse(
    #     name="Аэ-21-21",
    #     schedule_type="group",
    #     save_to_file=False
    # )

    schedule_data = [
        {
            "day": "Пн, 16 июня",
            "week": 18,
            "lessons": [
                {
                    "time": "11:10-12:45",
                    "subject": "Информатика",
                    "type": "Зачет с оценкой (по билетам)",
                    "room": "З-307 (Корпус З)",
                    "teacher": "доц. Аляева Ю.В."
                }
            ]
        },
        {
            "day": "Вт, 17 июня",
            "week": 18,
            "lessons": [
                {
                    "time": "11:10-12:45",
                    "subject": "Математический анализ",
                    "type": "Консультация",
                    "room": "М-200 (Корпус М)",
                    "teacher": "доц. Симушев А.А."
                }
            ]
        },
        {
            "day": "Ср, 18 июня",
            "week": 18,
            "lessons": [
                {
                    "time": "09:20-10:55",
                    "subject": "Математический анализ",
                    "type": "Экзамен",
                    "room": "М-200 (Корпус М)",
                    "teacher": "доц. Симушев А.А."
                }
            ]
        },
        {
            "day": "Вт, 24 июня",
            "week": 19,
            "lessons": [
                {
                    "time": "11:10-12:45",
                    "subject": "Физика",
                    "type": "Консультация",
                    "room": "К-601 (Корпус КИЖ)",
                    "teacher": "ст.преп. Корецкая И.В."
                }
            ]
        },
        {
            "day": "Чт, 26 июня",
            "week": 19,
            "lessons": [
                {
                    "time": "09:20-10:55",
                    "subject": "Физика",
                    "type": "Экзамен",
                    "room": "З-106 (Корпус З)",
                    "teacher": "ст.преп. Корецкая И.В."
                }
            ]
        },
        {
            "day": "Вт, 01 июля",
            "week": 20,
            "lessons": [
                {
                    "time": "11:10-12:45",
                    "subject": "Программирование",
                    "type": "Консультация",
                    "room": "М-709 (Корпус М)",
                    "teacher": "ст.преп. Гречкина П.В."
                }
            ]
        },
        {
            "day": "Ср, 02 июля",
            "week": 20,
            "lessons": [
                {
                    "time": "09:20-10:55",
                    "subject": "Программирование",
                    "type": "Экзамен",
                    "room": "М-805 (Корпус М)",
                    "teacher": "ст.преп. Гречкина П.В."
                }
            ]
        }
    ]


    integrator = ScheduleIntegrator(client)
    integrator.integrate_schedule(schedule_data, "А-07-24-short", project_title="IT")

    integrator.init_analyze("Анализ расписания")

if __name__ == "__main__":
    main()