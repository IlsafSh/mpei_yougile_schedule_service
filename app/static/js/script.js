// Глобальные переменные
let currentTab = 'parse';
let currentMethod = 'common';
let lastParseResult = null;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeMethodTabs();
    initializeForms();
    initializeWeightSliders();
});

// Инициализация основных вкладок
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');

            // Удаляем активный класс у всех кнопок и контента
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Добавляем активный класс к выбранной вкладке
            this.classList.add('active');
            document.getElementById(tabId + '-tab').classList.add('active');

            currentTab = tabId;
        });
    });
}

// Инициализация вкладок методов анализа
function initializeMethodTabs() {
    const methodTabs = document.querySelectorAll('.method-tab');
    const methodContents = document.querySelectorAll('.method-content');

    methodTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const methodId = this.getAttribute('data-method');

            // Удаляем активный класс у всех вкладок и контента
            methodTabs.forEach(t => t.classList.remove('active'));
            methodContents.forEach(content => content.classList.remove('active'));

            // Добавляем активный класс к выбранной вкладке
            this.classList.add('active');
            document.getElementById(methodId + '-method').classList.add('active');

            currentMethod = methodId;
        });
    });
}

// Инициализация слайдеров весов
function initializeWeightSliders() {
    const weightSliders = document.querySelectorAll('input[type="range"]');

    weightSliders.forEach(slider => {
        const valueSpan = document.getElementById(slider.id + '-value');

        slider.addEventListener('input', function() {
            if (valueSpan) {
                valueSpan.textContent = this.value;
            }
        });
    });
}

// Инициализация форм
function initializeForms() {
    // Форма парсинга
    const parseForm = document.getElementById('parse-form');
    if (parseForm) {
        parseForm.addEventListener('submit', handleParseSubmit);
    }

    // Форма YouGile
    const yougileForm = document.getElementById('yougile-form');
    if (yougileForm) {
        yougileForm.addEventListener('submit', handleYougileSubmit);
    }

    // Форма поиска общего окна
    const commonForm = document.getElementById('common-form');
    if (commonForm) {
        commonForm.addEventListener('submit', handleCommonWindowSubmit);
    }

    // Форма поиска сплит окна
    const splitForm = document.getElementById('split-form');
    if (splitForm) {
        splitForm.addEventListener('submit', handleSplitWindowSubmit);
    }
}

// Обработка отправки формы парсинга
async function handleParseSubmit(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const data = {
        name: formData.get('name'),
        schedule_type: formData.get('schedule_type'),
        cleanup_files: formData.has('cleanup_files'),
        max_weeks: parseInt(formData.get('max_weeks')),
        save_to_file: formData.has('save_to_file'),
        filename: null
    };

    try {
        showLoading(true);
        const response = await fetch('/api/v1/schedule/parse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok && result.success) {
            lastParseResult = result.data.schedule;
            showResult('success', 'Парсинг завершен успешно!', result);

            // Автоматически заполняем поле данных в форме YouGile
            const yougileScheduleData = document.getElementById('yougile-schedule-data');
            const yougileScheduleName = document.getElementById('yougile-schedule-name');

            if (yougileScheduleData && lastParseResult) {
                yougileScheduleData.value = JSON.stringify(lastParseResult, null, 2);
            }

            if (yougileScheduleName && data.name) {
                yougileScheduleName.value = data.name;
            }
        } else {
            showResult('error', 'Ошибка парсинга', result);
        }
    } catch (error) {
        showResult('error', 'Ошибка сети', { message: error.message });
    } finally {
        showLoading(false);
    }
}

// Обработка отправки формы YouGile
async function handleYougileSubmit(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    let scheduleData;

    try {
        scheduleData = JSON.parse(formData.get('schedule_data'));
    } catch (error) {
        showResult('error', 'Ошибка парсинга JSON', { message: 'Неверный формат JSON данных расписания' });
        return;
    }

    const data = {
        login: formData.get('login'),
        password: formData.get('password'),
        schedule_data: scheduleData,
        schedule_name: formData.get('schedule_name'),
        project_title: formData.get('project_title')
    };

    try {
        showLoading(true);
        const response = await fetch('/api/v1/yougile/integrate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok && result.success) {
            showResult('success', 'Интеграция с YouGile завершена успешно!', result);
        } else {
            showResult('error', 'Ошибка интеграции с YouGile', result);
        }
    } catch (error) {
        showResult('error', 'Ошибка сети', { message: error.message });
    } finally {
        showLoading(false);
    }
}

// Обработка отправки формы поиска общего окна
async function handleCommonWindowSubmit(event) {
    event.preventDefault();

    const formData = new FormData(event.target);

    // Парсим участников из строки
    const participantsStr = formData.get('participants');
    const participants = participantsStr.split(',').map(p => p.trim()).filter(p => p.length > 0);

    if (participants.length === 0) {
        showResult('error', 'Ошибка валидации', { message: 'Необходимо указать хотя бы одного участника' });
        return;
    }

    const data = {
        login: formData.get('login'),
        password: formData.get('password'),
        project_title: formData.get('project_title'),
        search_parameters: {
            start_date: formData.get('start_date'),
            end_date: formData.get('end_date'),
            required_duration: parseFloat(formData.get('required_duration')),
            participants: participants,
            earliest_start_time: formData.get('earliest_start_time'),
            latest_end_time: formData.get('latest_end_time'),
            min_gap_hours: parseFloat(formData.get('min_gap_hours')),
            maximize_participants: formData.has('maximize_participants'),
            minimize_start_time: formData.has('minimize_start_time'),
            minimize_total_idle: formData.has('minimize_total_idle'),
            minimize_max_gap: formData.has('minimize_max_gap'),
            include_holidays: formData.has('include_holidays'),
            include_weekends: formData.has('include_weekends'),
            weight_participants: parseFloat(formData.get('weight_participants')),
            weight_start_time: parseFloat(formData.get('weight_start_time')),
            weight_total_idle: parseFloat(formData.get('weight_total_idle')),
            weight_max_gap: parseFloat(formData.get('weight_max_gap'))
        }
    };

    try {
        showLoading(true);
        const response = await fetch('/api/v1/schedule/analyze/common-window', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok && result.success) {
            showResult('success', 'Поиск общего окна завершен!', result);
        } else {
            showResult('error', 'Ошибка поиска общего окна', result);
        }
    } catch (error) {
        showResult('error', 'Ошибка сети', { message: error.message });
    } finally {
        showLoading(false);
    }
}

// Обработка отправки формы поиска сплит окна
async function handleSplitWindowSubmit(event) {
    event.preventDefault();

    const formData = new FormData(event.target);

    // Парсим участников из строки
    const participantsStr = formData.get('participants');
    const participants = participantsStr.split(',').map(p => p.trim()).filter(p => p.length > 0);

    if (participants.length === 0) {
        showResult('error', 'Ошибка валидации', { message: 'Необходимо указать хотя бы одного участника' });
        return;
    }

    const data = {
        login: formData.get('login'),
        password: formData.get('password'),
        project_title: formData.get('project_title'),
        search_parameters: {
            start_date: formData.get('start_date'),
            end_date: formData.get('end_date'),
            total_duration: parseFloat(formData.get('total_duration')),
            min_segment_duration: parseFloat(formData.get('min_segment_duration')),
            max_segments: parseInt(formData.get('max_segments')),
            participants: participants,
            earliest_start_time: formData.get('earliest_start_time'),
            latest_end_time: formData.get('latest_end_time'),
            min_gap_hours: parseFloat(formData.get('min_gap_hours')),
            include_holidays: formData.has('include_holidays'),
            include_weekends: formData.has('include_weekends')
        }
    };

    try {
        showLoading(true);
        const response = await fetch('/api/v1/schedule/analyze/split-window', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok && result.success) {
            showResult('success', 'Поиск сплит окна завершен!', result);
        } else {
            showResult('error', 'Ошибка поиска сплит окна', result);
        }
    } catch (error) {
        showResult('error', 'Ошибка сети', { message: error.message });
    } finally {
        showLoading(false);
    }
}

// Показать/скрыть индикатор загрузки
function showLoading(show) {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = show ? 'flex' : 'none';
    }
}

// Показать результат
function showResult(type, message, data) {
    const resultsContent = document.getElementById('results-content');
    if (!resultsContent) return;

    const resultClass = type === 'success' ? 'result-success' : 'result-error';

    let html = `
        <div class="${resultClass}">
            <h4><i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i> ${message}</h4>
            <p>${data.message || ''}</p>
    `;

    if (data.data) {
        html += `
            <div class="result-data">
                <h5>Данные результата:</h5>
                <pre>${JSON.stringify(data.data, null, 2)}</pre>
            </div>
        `;
    }

    html += '</div>';

    resultsContent.innerHTML = html;

    // Прокрутка к результатам
    document.getElementById('results').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Утилиты для работы с формами
function fillScheduleDataFromParse() {
    if (lastParseResult) {
        const yougileScheduleData = document.getElementById('yougile-schedule-data');
        if (yougileScheduleData) {
            yougileScheduleData.value = JSON.stringify(lastParseResult, null, 2);
        }
    }
}

