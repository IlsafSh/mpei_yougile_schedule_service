# MPEI Schedule Service

Веб-сервис для сбора, анализа и интеграции учебного расписания БАРС НИУ МЭИ с системой управления проектами YouGile.

## Описание

MPEI Schedule Service представляет собой полнофункциональный веб-сервис, разработанный на основе FastAPI, который обеспечивает автоматизированный сбор расписания с сайта БАРС НИУ МЭИ, его анализ и интеграцию с платформой YouGile для управления проектами.

### Основные возможности

- **Парсинг расписания**: Автоматический сбор данных расписания для групп, преподавателей и аудиторий
- **Анализ расписания**: Поиск свободных временных окон с различными параметрами
- **Интеграция с YouGile**: Создание проектов и задач на основе данных расписания
- **Веб-интерфейс**: Удобный пользовательский интерфейс для управления всеми функциями
- **REST API**: Полноценное API для интеграции с другими системами

## Архитектура

Сервис построен на современной архитектуре с использованием следующих технологий:

- **FastAPI**: Высокопроизводительный веб-фреймворк для создания API
- **Pydantic**: Валидация данных и сериализация
- **Selenium**: Автоматизация браузера для парсинга веб-страниц
- **HTML/CSS/JavaScript**: Современный адаптивный пользовательский интерфейс
- **YouGile API**: Интеграция с системой управления проектами

### Структура проекта

```
fastapi_mpei_service/
├── app/
│   ├── core/                    # Основные модули из прототипа
│   │   ├── schedule_parser/     # Парсинг расписания
│   │   ├── schedule_analyzer/   # Анализ расписания
│   │   └── yougile_integration/ # Интеграция с YouGile
│   ├── models/                  # Pydantic модели
│   ├── routers/                 # API роутеры
│   ├── services/                # Бизнес-логика
│   ├── static/                  # Статические файлы (CSS, JS)
│   ├── templates/               # HTML шаблоны
│   ├── config.py               # Конфигурация
│   ├── main.py                 # Главный файл приложения
│   └── data/                    # Данные и логи
├── requirements.txt            # Зависимости
└── test_api.py                # Тесты
```

## Установка и запуск

### Требования

- Python 3.11+
- Google Chrome или Chromium (для Selenium)
- Доступ к интернету

### Установка

1. Клонируйте репозиторий или распакуйте архив:
```bash
cd fastapi_mpei_service
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Запустите сервер:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Доступ к сервису

- **Веб-интерфейс**: http://localhost:8000
- **API документация**: http://localhost:8000/docs
- **Альтернативная документация**: http://localhost:8000/redoc

## Использование

### Веб-интерфейс

Веб-интерфейс предоставляет три основные вкладки:

1. **Парсинг расписания**: Сбор данных расписания с сайта БАРС НИУ МЭИ
2. **Интеграция с YouGile**: Создание проектов и задач в YouGile
3. **Анализ расписания**: Поиск свободных временных окон

### API Endpoints

#### Парсинг расписания
- `POST /api/v1/schedule/parse` - Парсинг расписания

#### Интеграция с YouGile
- `POST /api/v1/yougile/integrate` - Интеграция расписания с YouGile

#### Анализ расписания
- `POST /api/v1/schedule/analyze/common-window` - Общее планирование окна в расписании
- `POST /api/v1/schedule/analyze/split-window` - Планирование сплит-окна в расписании

#### Служебные
- `GET /api/v1/health` - Проверка состояния сервиса

## Конфигурация

Сервис поддерживает конфигурацию через переменные окружения:

- `DEBUG`: Режим отладки (по умолчанию: False)
- `HOST`: Хост для запуска (по умолчанию: 0.0.0.0)
- `PORT`: Порт для запуска (по умолчанию: 8000)

## Развертывание

### Локальное развертывание

Для локального развертывания достаточно выполнить команды из раздела "Установка и запуск".

### Продакшн развертывание

Для продакшн развертывания рекомендуется:

1. Использовать WSGI сервер (например, Gunicorn)
2. Настроить обратный прокси (Nginx)
3. Использовать Docker для контейнеризации
4. Настроить мониторинг и логирование

## Безопасность

- Все пароли и токены должны передаваться через HTTPS
- Рекомендуется использовать переменные окружения для конфиденциальных данных
- Регулярно обновляйте зависимости для устранения уязвимостей

## Поддержка и разработка

### Известные ограничения

- Парсинг зависит от структуры сайта БАРС НИУ МЭИ
- Требуется установленный браузер Chrome/Chromium
- Интеграция с YouGile требует действующих учетных данных

## Лицензия

Проект разработан для образовательных и исследовательских целей.

## Контакты

Для вопросов и предложений по улучшению сервиса обращайтесь к разработчикам проекта.

