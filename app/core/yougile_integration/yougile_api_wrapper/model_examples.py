"""
Примеры использования моделей данных YouGile API.

Этот файл содержит примеры создания и использования всех моделей данных,
доступных в модуле-обертке для YouGile API.
"""

from yougile_integration.yougile_api_wrapper.yougile_api.models import (
    Task, Board, Column, Company, Department, Employee, File,
    GroupChat, Project, ProjectRole, ChatMessage, SprintSticker,
    SprintStickerState, StringSticker, StringStickerState, Webhook
)


def task_examples():
    """Примеры использования модели Task."""
    print("\n=== Примеры использования модели Task ===")
    
    # Создание задачи с минимальными обязательными полями
    task = Task(title="Новая задача")
    print(f"Задача с минимальными полями: {task.model_dump()}")

    # Создание задачи со всеми полями
    task_full = Task(
        id="task-123",
        title="Полная задача",
        column_id="column-456",
        description="Описание задачи",
        archived=False,
        completed=False,
        subtasks=["subtask-1", "subtask-2"],
        assigned=["user-1", "user-2"],
        deadline={"date": "2023-12-31"},
        timeTracking={"spent": 120, "estimate": 240},
        checklists=[{"title": "Чеклист", "items": [{"text": "Пункт 1", "checked": False}]}],
        stickers={"sprint": {"id": "sprint-1", "state": "state-1"}},
        color="task-blue",
        idTaskCommon="common-123",
        idTaskProject="project-123",
        stopwatch={"active": False},
        timer={"active": False},
        deleted=False,
        board_id="board-789",
        project_id="project-789"
    )
    print(f"Задача со всеми полями: {task_full.model_dump(by_alias=True)}")

    # Обновление полей задачи
    task.description = "Новое описание"
    task.completed = True
    print(f"Обновленная задача: {task.model_dump()}")

    # Преобразование словаря в модель
    task_dict = {
        "id": "task-456",
        "title": "Задача из словаря",
        "columnId": "column-789",
        "description": "Описание из словаря"
    }
    task_from_dict = Task.model_validate(task_dict)
    print(f"Задача из словаря: {task_from_dict.model_dump()}")

    # Доступ к полям через атрибуты
    print(f"ID задачи: {task_from_dict.id}")
    print(f"Название задачи: {task_from_dict.title}")
    print(f"ID колонки: {task_from_dict.column_id}")


def board_examples():
    """Примеры использования модели Board."""
    print("\n=== Примеры использования модели Board ===")

    # Создание доски с минимальными обязательными полями
    board = Board(title="Новая доска", projectId="project-123")
    print(f"Доска с минимальными полями: {board.model_dump()}")

    # Создание доски со всеми полями
    board_full = Board(
        id="board-123",
        title="Полная доска",
        projectId="project-456",
        stickers={"sprint": ["sprint-1", "sprint-2"]},
        deleted=False
    )
    print(f"Доска со всеми полями: {board_full.model_dump(by_alias=True)}")

    # Обновление полей доски
    board.title = "Обновленная доска"
    print(f"Обновленная доска: {board.model_dump()}")

    # Преобразование словаря в модель
    board_dict = {
        "id": "board-456",
        "title": "Доска из словаря",
        "projectId": "project-789"
    }
    board_from_dict = Board.model_validate(board_dict)
    print(f"Доска из словаря: {board_from_dict.model_dump()}")

    # Доступ к полям через атрибуты
    print(f"ID доски: {board_from_dict.id}")
    print(f"Название доски: {board_from_dict.title}")
    print(f"ID проекта: {board_from_dict.project_id}")


def column_examples():
    """Примеры использования модели Column."""
    print("\n=== Примеры использования модели Column ===")

    # Создание колонки с минимальными обязательными полями
    column = Column(title="Новая колонка", boardId="board-123")
    print(f"Колонка с минимальными полями: {column.model_dump()}")

    # Создание колонки со всеми полями
    column_full = Column(
        id="column-123",
        title="Полная колонка",
        boardId="board-456",
        color=1,
        deleted=False
    )
    print(f"Колонка со всеми полями: {column_full.model_dump(by_alias=True)}")

    # Обновление полей колонки
    column.title = "Обновленная колонка"
    column.color = 2
    print(f"Обновленная колонка: {column.model_dump()}")

    # Преобразование словаря в модель
    column_dict = {
        "id": "column-456",
        "title": "Колонка из словаря",
        "boardId": "board-789",
        "color": 3
    }
    column_from_dict = Column.model_validate(column_dict)
    print(f"Колонка из словаря: {column_from_dict.model_dump()}")

    # Доступ к полям через атрибуты
    print(f"ID колонки: {column_from_dict.id}")
    print(f"Название колонки: {column_from_dict.title}")
    print(f"ID доски: {column_from_dict.board_id}")
    print(f"Цвет колонки: {column_from_dict.color}")


def company_examples():
    """Примеры использования модели Company."""
    print("\n=== Примеры использования модели Company ===")

    # Создание компании с минимальными обязательными полями
    company = Company(title="Новая компания")
    print(f"Компания с минимальными полями: {company.model_dump()}")

    # Создание компании со всеми полями
    company_full = Company(
        id="company-123",
        title="Полная компания",
        deleted=False,
        timestamp=1625097600000,
        apiData={"key": "value"}
    )
    print(f"Компания со всеми полями: {company_full.model_dump(by_alias=True)}")

    # Обновление полей компании
    company.title = "Обновленная компания"
    print(f"Обновленная компания: {company.model_dump()}")

    # Преобразование словаря в модель
    company_dict = {
        "id": "company-456",
        "title": "Компания из словаря",
        "timestamp": 1625097600000,
        "apiData": {"custom": "data"}
    }
    company_from_dict = Company.model_validate(company_dict)
    print(f"Компания из словаря: {company_from_dict.model_dump()}")

    # Доступ к полям через атрибуты
    print(f"ID компании: {company_from_dict.id}")
    print(f"Название компании: {company_from_dict.title}")
    print(f"Временная метка: {company_from_dict.timestamp}")
    print(f"API данные: {company_from_dict.api_data}")


def department_examples():
    """Примеры использования модели Department."""
    print("\n=== Примеры использования модели Department ===")

    # Создание отдела с минимальными обязательными полями
    department = Department()
    print(f"Отдел с минимальными полями: {department.model_dump()}")

    # Создание отдела со всеми полями
    department_full = Department(
        id="department-123",
        title="Полный отдел",
        parentId="department-parent",
        users={"user-1": {"role": "admin"}, "user-2": {"role": "member"}},
        deleted=False
    )
    print(f"Отдел со всеми полями: {department_full.model_dump(by_alias=True)}")

    # Обновление полей отдела
    department.title = "Обновленный отдел"
    department.users = {"user-3": {"role": "admin"}}
    print(f"Обновленный отдел: {department.model_dump()}")

    # Преобразование словаря в модель
    department_dict = {
        "id": "department-456",
        "title": "Отдел из словаря",
        "parentId": "department-parent-2",
        "users": {"user-4": {"role": "member"}}
    }
    department_from_dict = Department.model_validate(department_dict)
    print(f"Отдел из словаря: {department_from_dict.model_dump()}")

    # Доступ к полям через атрибуты
    print(f"ID отдела: {department_from_dict.id}")
    print(f"Название отдела: {department_from_dict.title}")
    print(f"ID родительского отдела: {department_from_dict.parent_id}")
    print(f"Пользователи отдела: {department_from_dict.users}")


def employee_examples():
    """Примеры использования модели Employee."""
    print("\n=== Примеры использования модели Employee ===")

    # Создание сотрудника с минимальными обязательными полями
    employee = Employee(email="employee@example.com")
    print(f"Сотрудник с минимальными полями: {employee.model_dump()}")

    # Создание сотрудника со всеми полями
    employee_full = Employee(
        id="employee-123",
        email="full.employee@example.com",
        isAdmin=True
    )
    print(f"Сотрудник со всеми полями: {employee_full.model_dump(by_alias=True)}")

    # Обновление полей сотрудника
    employee.is_admin = False
    print(f"Обновленный сотрудник: {employee.model_dump()}")

    # Преобразование словаря в модель
    employee_dict = {
        "id": "employee-456",
        "email": "dict.employee@example.com",
        "isAdmin": True
    }
    employee_from_dict = Employee.model_validate(employee_dict)
    print(f"Сотрудник из словаря: {employee_from_dict.model_dump()}")

    # Доступ к полям через атрибуты
    print(f"ID сотрудника: {employee_from_dict.id}")
    print(f"Email сотрудника: {employee_from_dict.email}")
    print(f"Администратор: {employee_from_dict.is_admin}")


def file_examples():
    """Примеры использования модели File."""
    print("\n=== Примеры использования модели File ===")

    # Создание файла с минимальными обязательными полями
    file = File(url="https://example.com/files/file.txt")
    print(f"Файл с минимальными полями: {file.model_dump()}")

    # Создание файла со всеми полями
    file_full = File(
        url="https://example.com/files/full-file.txt",
        name="full-file.txt",
        size=1024,
        mime_type="text/plain"
    )
    print(f"Файл со всеми полями: {file_full.model_dump()}")

    # Обновление полей файла
    file.name = "updated-file.txt"
    file.size = 2048
    print(f"Обновленный файл: {file.model_dump()}")

    # Преобразование словаря в модель
    file_dict = {
        "url": "https://example.com/files/dict-file.txt",
        "name": "dict-file.txt",
        "size": 4096,
        "mime_type": "application/pdf"
    }
    file_from_dict = File.model_validate(file_dict)
    print(f"Файл из словаря: {file_from_dict.model_dump()}")

    # Доступ к полям через атрибуты
    print(f"URL файла: {file_from_dict.url}")
    print(f"Имя файла: {file_from_dict.name}")
    print(f"Размер файла: {file_from_dict.size}")
    print(f"MIME-тип файла: {file_from_dict.mime_type}")


def group_chat_examples():
    """Примеры использования модели GroupChat."""
    print("\n=== Примеры использования модели GroupChat ===")

    # Создание группового чата с минимальными обязательными полями
    group_chat = GroupChat(title="Новый чат", users={"user-1": {"role": "admin"}})
    print(f"Групповой чат с минимальными полями: {group_chat.model_dump()}")

    # Создание группового чата со всеми полями
    group_chat_full = GroupChat(
        id="chat-123",
        title="Полный чат",
        users={"user-1": {"role": "admin"}, "user-2": {"role": "member"}},
        deleted=False
    )
    print(f"Групповой чат со всеми полями: {group_chat_full.model_dump()}")

    # Обновление полей группового чата
    group_chat.title = "Обновленный чат"
    group_chat.users["user-3"] = {"role": "member"}
    print(f"Обновленный групповой чат: {group_chat.model_dump()}")

    # Преобразование словаря в модель
    group_chat_dict = {
        "id": "chat-456",
        "title": "Чат из словаря",
        "users": {"user-4": {"role": "admin"}, "user-5": {"role": "member"}}
    }
    group_chat_from_dict = GroupChat.model_validate(group_chat_dict)
    print(f"Групповой чат из словаря: {group_chat_from_dict.model_dump()}")

    # Доступ к полям через атрибуты
    print(f"ID группового чата: {group_chat_from_dict.id}")
    print(f"Название группового чата: {group_chat_from_dict.title}")
    print(f"Пользователи группового чата: {group_chat_from_dict.users}")


def project_examples():
    """Примеры использования модели Project."""
    print("\n=== Примеры использования модели Project ===")

    # Создание проекта с минимальными обязательными полями
    project = Project(id="project-123", title="Новый проект")
    print(f"Проект с минимальными полями: {project.model_dump()}")

    # Создание проекта со всеми полями
    project_full = Project(
        id="project-456",
        title="Полный проект",
        users={"user-1": "admin", "user-2": "member"},
        deleted=False
    )
    print(f"Проект со всеми полями: {project_full.model_dump()}")

    # Обновление полей проекта
    project.title = "Обновленный проект"
    project.users = {"user-3": "admin"}
    print(f"Обновленный проект: {project.model_dump()}")

    # Преобразование словаря в модель
    project_dict = {
        "id": "project-789",
        "title": "Проект из словаря",
        "users": {"user-4": "admin", "user-5": "member"}
    }
    project_from_dict = Project.model_validate(project_dict)
    print(f"Проект из словаря: {project_from_dict.model_dump()}")

    # Доступ к полям через атрибуты
    print(f"ID проекта: {project_from_dict.id}")
    print(f"Название проекта: {project_from_dict.title}")
    print(f"Пользователи проекта: {project_from_dict.users}")


def project_role_examples():
    """Примеры использования модели ProjectRole."""
    print("\n=== Примеры использования модели ProjectRole ===")

    # Создание роли проекта с минимальными обязательными полями
    permissions = {
        "editTitle": True,
        "delete": False,
        "boards": {
            "editTitle": True,
            "delete": False
        }
    }
    project_role = ProjectRole(name="Новая роль", permissions=permissions)
    print(f"Роль проекта с минимальными полями: {project_role.model_dump()}")

    # Создание роли проекта со всеми полями
    project_role_full = ProjectRole(
        id="role-123",
        name="Полная роль",
        description="Описание роли",
        permissions=permissions
    )
    print(f"Роль проекта со всеми полями: {project_role_full.model_dump()}")

    # Обновление полей роли проекта
    project_role.name = "Обновленная роль"
    project_role.description = "Новое описание"
    print(f"Обновленная роль проекта: {project_role.model_dump()}")

    # Преобразование словаря в модель
    project_role_dict = {
        "id": "role-456",
        "name": "Роль из словаря",
        "description": "Описание из словаря",
        "permissions": permissions
    }
    project_role_from_dict = ProjectRole.model_validate(project_role_dict)
    print(f"Роль проекта из словаря: {project_role_from_dict.model_dump()}")

    # Доступ к полям через атрибуты
    print(f"ID роли проекта: {project_role_from_dict.id}")
    print(f"Название роли проекта: {project_role_from_dict.name}")
    print(f"Описание роли проекта: {project_role_from_dict.description}")


def chat_message_examples():
    """Примеры использования модели ChatMessage."""
    print("\n=== Примеры использования модели ChatMessage ===")

    # Создание сообщения чата с минимальными обязательными полями
    chat_message = ChatMessage(text="Привет!", textHtml="<p>Привет!</p>", label="user-1")
    print(f"Сообщение чата с минимальными полями: {chat_message.model_dump()}")

    # Создание сообщения чата со всеми полями
    chat_message_full = ChatMessage(
        id="message-123",
        text="Полное сообщение",
        textHtml="<p>Полное сообщение</p>",
        label="user-2",
        deleted=False,
        react="👍"
    )
    print(f"Сообщение чата со всеми полями: {chat_message_full.model_dump(by_alias=True)}")

    # Обновление полей сообщения чата
    chat_message.text = "Обновленное сообщение"
    chat_message.text_html = "<p>Обновленное сообщение</p>"
    print(f"Обновленное сообщение чата: {chat_message.model_dump()}")

    # Преобразование словаря в модель
    chat_message_dict = {
        "id": "message-456",
        "text": "Сообщение из словаря",
        "textHtml": "<p>Сообщение из словаря</p>",
        "label": "user-3",
        "react": "❤️"
    }
    chat_message_from_dict = ChatMessage.model_validate(chat_message_dict)
    print(f"Сообщение чата из словаря: {chat_message_from_dict.model_dump()}")

    # Доступ к полям через атрибуты
    print(f"ID сообщения чата: {chat_message_from_dict.id}")
    print(f"Текст сообщения чата: {chat_message_from_dict.text}")
    print(f"HTML-текст сообщения чата: {chat_message_from_dict.text_html}")
    print(f"Метка сообщения чата: {chat_message_from_dict.label}")


def sprint_sticker_examples():
    """Примеры использования модели SprintSticker."""
    print("\n=== Примеры использования модели SprintSticker ===")

    # Создание стикера спринта с минимальными обязательными полями
    sprint_sticker = SprintSticker(name="Новый спринт", states=[])
    print(f"Стикер спринта с минимальными полями: {sprint_sticker.model_dump()}")

    # Создание стикера спринта со всеми полями
    states = [
        {"id": "state-1", "name": "Состояние 1"},
        {"id": "state-2", "name": "Состояние 2"}
    ]
    sprint_sticker_full = SprintSticker(
        id="sticker-123",
        name="Полный спринт",
        states=states,
        deleted=False
    )
    print(f"Стикер спринта со всеми полями: {sprint_sticker_full.model_dump()}")

    # Обновление полей стикера спринта
    sprint_sticker.name = "Обновленный спринт"
    sprint_sticker.states = [{"id": "state-3", "name": "Состояние 3"}]
    print(f"Обновленный стикер спринта: {sprint_sticker.model_dump()}")

    # Преобразование словаря в модель
    sprint_sticker_dict = {
        "id": "sticker-456",
        "name": "Спринт из словаря",
        "states": [{"id": "state-4", "name": "Состояние 4"}]
    }
    sprint_sticker_from_dict = SprintSticker.model_validate(sprint_sticker_dict)
    print(f"Стикер спринта из словаря: {sprint_sticker_from_dict.model_dump()}")

    # Доступ к полям через атрибуты
    print(f"ID стикера спринта: {sprint_sticker_from_dict.id}")
    print(f"Название стикера спринта: {sprint_sticker_from_dict.name}")
    print(f"Состояния стикера спринта: {sprint_sticker_from_dict.states}")


def sprint_sticker_state_examples():
    """Примеры использования модели SprintStickerState."""
    print("\n=== Примеры использования модели SprintStickerState ===")

    # Создание состояния стикера спринта с минимальными обязательными полями
    sprint_sticker_state = SprintStickerState(name="Новое состояние")
    print(f"Состояние стикера спринта с минимальными полями: {sprint_sticker_state.model_dump()}")

    # Создание состояния стикера спринта со всеми полями
    sprint_sticker_state_full = SprintStickerState(
        id="state-123",
        name="Полное состояние",
        begin=1625097600000,
        end=1627776000000,
        deleted=False
    )
    print(f"Состояние стикера спринта со всеми полями: {sprint_sticker_state_full.model_dump()}")

    # Обновление полей состояния стикера спринта
    sprint_sticker_state.name = "Обновленное состояние"
    sprint_sticker_state.begin = 1625097600000
    print(f"Обновленное состояние стикера спринта: {sprint_sticker_state.model_dump()}")

    # Преобразование словаря в модель
    sprint_sticker_state_dict = {
        "id": "state-456",
        "name": "Состояние из словаря",
        "begin": 1625097600000,
        "end": 1627776000000
    }
    sprint_sticker_state_from_dict = SprintStickerState.model_validate(sprint_sticker_state_dict)
    print(f"Состояние стикера спринта из словаря: {sprint_sticker_state_from_dict.model_dump()}")

    # Доступ к полям через атрибуты
    print(f"ID состояния стикера спринта: {sprint_sticker_state_from_dict.id}")
    print(f"Название состояния стикера спринта: {sprint_sticker_state_from_dict.name}")
    print(f"Начало состояния стикера спринта: {sprint_sticker_state_from_dict.begin}")
    print(f"Конец состояния стикера спринта: {sprint_sticker_state_from_dict.end}")


def string_sticker_examples():
    """Примеры использования модели StringSticker."""
    print("\n=== Примеры использования модели StringSticker ===")

    # Создание строкового стикера с минимальными обязательными полями
    string_sticker = StringSticker(name="Новый стикер")
    print(f"Строковый ��тикер с минимальными полями: {string_sticker.model_dump()}")

    # Создание строкового стикера со всеми полями
    states = [
        {"id": "state-1", "name": "Состояние 1"},
        {"id": "state-2", "name": "Состояние 2"}
    ]
    string_sticker_full = StringSticker(
        id="sticker-123",
        name="Полный стикер",
        states=states,
        icon="icon-tag",
        deleted=False
    )
    print(f"Строковый стикер со всеми полями: {string_sticker_full.model_dump()}")

    # Обновление полей строкового стикера
    string_sticker.name = "Обновленный стикер"
    string_sticker.icon = "icon-flag"
    print(f"Обновленный строковый стикер: {string_sticker.model_dump()}")

    # Преобразование словаря в модель
    string_sticker_dict = {
        "id": "sticker-456",
        "name": "Стикер из словаря",
        "states": [{"id": "state-3", "name": "Состояние 3"}],
        "icon": "icon-star"
    }
    string_sticker_from_dict = StringSticker.model_validate(string_sticker_dict)
    print(f"Строковый стикер из словаря: {string_sticker_from_dict.model_dump()}")

    # Доступ к полям через атрибуты
    print(f"ID строкового стикера: {string_sticker_from_dict.id}")
    print(f"Название строкового стикера: {string_sticker_from_dict.name}")
    print(f"Состояния строкового стикера: {string_sticker_from_dict.states}")
    print(f"Иконка строкового стикера: {string_sticker_from_dict.icon}")


def string_sticker_state_examples():
    """Примеры использования модели StringStickerState."""
    print("\n=== Примеры использования модели StringStickerState ===")

    # Создание состояния строкового стикера с минимальными обязательными полями
    string_sticker_state = StringStickerState(name="Новое состояние")
    print(f"Состояние строкового стикера с минимальными полями: {string_sticker_state.model_dump()}")

    # Создание состояния строкового стикера со всеми полями
    string_sticker_state_full = StringStickerState(
        id="state-123",
        name="Полное состояние",
        color=1,
        deleted=False
    )
    print(f"Состояние строкового стикера со всеми полями: {string_sticker_state_full.model_dump()}")

    # Обновление полей состояния строкового стикера
    string_sticker_state.name = "Обновленное состояние"
    string_sticker_state.color = 2
    print(f"Обновленное состояние строкового стикера: {string_sticker_state.model_dump()}")

    # Преобразование словаря в модель
    string_sticker_state_dict = {
        "id": "state-456",
        "name": "Состояние из словаря",
        "color": 3
    }
    string_sticker_state_from_dict = StringStickerState.model_validate(string_sticker_state_dict)
    print(f"Состояние строкового стикера из словаря: {string_sticker_state_from_dict.model_dump()}")

    # Доступ к полям через атрибуты
    print(f"ID состояния строкового стикера: {string_sticker_state_from_dict.id}")
    print(f"Название состояния строкового стикера: {string_sticker_state_from_dict.name}")
    print(f"Цвет состояния строкового стикера: {string_sticker_state_from_dict.color}")


def webhook_examples():
    """Примеры использования модели Webhook."""
    print("\n=== Примеры использования модели Webhook ===")

    # Создание вебхука с минимальными обязательными полями
    webhook = Webhook(
        id="webhook-123",
        url="https://example.com/webhook",
        event="task.created",
        deleted=False,
        disabled=False
    )
    print(f"Вебхук с минимальными полями: {webhook.model_dump()}")

    # Обновление полей вебхука
    webhook.url = "https://example.com/updated-webhook"
    webhook.disabled = True
    print(f"Обновленный вебхук: {webhook.model_dump()}")

    # Преобразование словаря в модель
    webhook_dict = {
        "id": "webhook-456",
        "url": "https://example.com/dict-webhook",
        "event": "task.updated",
        "deleted": False,
        "disabled": False
    }
    webhook_from_dict = Webhook.model_validate(webhook_dict)
    print(f"Вебхук из словаря: {webhook_from_dict.model_dump()}")
    
    # Доступ к полям через атрибуты
    print(f"ID вебхука: {webhook_from_dict.id}")
    print(f"URL вебхука: {webhook_from_dict.url}")
    print(f"Событие вебхука: {webhook_from_dict.event}")
    print(f"Вебхук удален: {webhook_from_dict.deleted}")
    print(f"Вебхук отключен: {webhook_from_dict.disabled}")


def main():
    """Основная функция для запуска примеров."""
    # Запуск примеров использования моделей
    task_examples()
    board_examples()
    column_examples()
    company_examples()
    department_examples()
    employee_examples()
    file_examples()
    group_chat_examples()
    project_examples()
    project_role_examples()
    chat_message_examples()
    sprint_sticker_examples()
    sprint_sticker_state_examples()
    string_sticker_examples()
    string_sticker_state_examples()
    webhook_examples()


if __name__ == "__main__":
    main()

