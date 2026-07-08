# DriveCore — ИИ-ассистент для платформенной занятости

[![Django](https://img.shields.io/badge/Django-5.2.15-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.17.1-red.svg)](https://www.django-rest-framework.org/)
[![Ollama](https://img.shields.io/badge/Ollama-LLM-orange.svg)](https://ollama.ai/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## О проекте

**DriveCore** — это интеллектуальный ИИ-ассистент для водителей такси и курьеров, работающих на платформах занятости (Яндекс Про, Uber, Bolt и др.). Проект помогает водителям разбираться с налогами, документами, выплатами и правилами работы.

### Цели проекта

- Создание ИИ-ассистента для водителей платформенной занятости
- Реализация RAG (Retrieval-Augmented Generation) для точных ответов на основе базы знаний
- Интеграция с Telegram для доступности на мобильных устройствах
- Мониторинг проблем и оповещение о всплесках жалоб
- Автоматический парсинг новостей по теме платформенной занятости

---

## Основные возможности

### Для водителей

| Функция | Описание |
|---------|----------|
| **Чат с ИИ** | Задавайте вопросы о налогах, документах, выплатах на русском языке |
| **Понимание смысла** | Векторный поиск понимает разные формулировки одного вопроса |
| **Налоговый калькулятор** | Рассчитайте налоги для самозанятого, ИП или наёмного работника |
| **WebSocket чат** | Общение в реальном времени без перезагрузки страницы |
| **Telegram бот** | Доступ к ассистенту через Telegram (@drive_core_bot) |

### Для команды

| Функция | Описание |
|---------|----------|
| **Дашборд** | Отслеживание доходов, налогов и активности пользователей |
| **Мониторинг проблем** | Автоматическое обнаружение всплесков жалоб по городам |
| **Новости ПЗ** | Ежедневный дайджест новостей платформенной занятости |
| **Django Admin** | Управление пользователями, чатами, налоговыми расчётами |

### Интеграции

| Сервис | Назначение |
|--------|------------|
| **Ollama** | Локальная LLM (Llama 3.2) для генерации ответов |
| **Telegram Bot** | Доступ к ассистенту через мессенджер |
| **RSS ленты** | Автоматический парсинг новостей (ТАСС, РБК) |
| **Sentence-Transformers** | Векторные эмбеддинги для семантического поиска |

---

![Демонстрация](media/demo.mp4)

## Логика работы ИИ-агента

### Входные и выходные данные

| Тип данных | Источник | Формат | Назначение |
|------------|----------|--------|------------|
| **Вопрос пользователя** | Веб-форма / Telegram | Текст | Запрос к ИИ-ассистенту |
| **Данные пользователя** | База данных Django | JSON | Контекст (статус, доход, регион) |
| **Новостные RSS ленты** | ТАСС, РБК | XML/RSS | Источник новостей по ПЗ |
| **Жалобы из чатов** | История чатов | Текст | Мониторинг проблем |

### Инструменты и ИИ-сервисы

| Сервис | Назначение |
|--------|------------|
| **Ollama (Llama 3.2)** | Генерация ответов на естественном языке |
| **Sentence-Transformers** | Векторные эмбеддинги для семантического поиска |
| **RAG Pipeline** | Поиск релевантных документов в базе знаний |
| **Celery** | Фоновые задачи (парсинг новостей, мониторинг) |
| **Django Channels** | WebSocket для реального времени |

### Польза для команды

| Польза | Описание |
|--------|----------|
| **Снижение нагрузки на поддержку** | Автоматические ответы на частые вопросы |
| **Ускорение работы** | Мгновенный доступ к информации через чат |
| **Мониторинг проблем** | Раннее обнаружение всплесков жалоб |
| **Аналитика** | Дашборд с ключевыми метриками |
| **Автоматизация** | Парсинг новостей и ежедневные дайджесты |


---

## Автоматические задачи

### Парсер новостей по платформенной занятости

Система автоматически парсит новости из RSS-лент (ТАСС, РБК) и отбирает материалы по теме платформенной занятости.

**Как это работает:**

1. Каждый день в 9:00 Celery запускает задачу `parse_news`
2. Система парсит RSS-ленты ТАСС и РБК
3. Из всех новостей отбираются только те, которые содержат ключевые слова:
   - `такси`, `самозанятый`, `ИП`, `платформенная занятость`, `гиг-экономика`
   - `водитель`, `курьер`, `яндекс такси`, `uber`, `bolt`, `grab`
4. Отобранные новости сохраняются в базу данных с категорией `platform_employment`
5. В 9:05 формируется дайджест и отправляется в Telegram-чат команды

**Пример дайджеста:**
```
Ежедневный дайджест 06.07.2026

Новости (1):
• ТАСС: украинские ТЦК вербуют таксистов
  https://tass.ru/armiya-i-opk/27891063
```

### Мониторинг проблем

Система анализирует жалобы водителей из чатов и оповещает команду о всплесках проблем.

**Как это работает:**

1. Каждые 2 часа Celery запускает задачу `monitor_problems`
2. Система сканирует историю чатов за последние 2 часа
3. Поиск жалоб по ключевым словам:
   - `проблема`, `ошибка`, `не работает`, `сбой`, `баг`
   - `жалоба`, `недоволен`, `плохо`, `ужасно`
   - `деньги`, `выплата`, `не получил`, `задержка`
4. Жалобы группируются по городам
5. Если в одном городе зафиксировано 3+ жалоб - отправляется оповещение

---

## Диаграмма потоков данных

```mermaid
flowchart TB
    subgraph INPUT["Входные данные"]
        Q[Вопрос пользователя]
        U[Данные пользователя]
        N[Новостные RSS ленты]
        C[Жалобы из чатов]
    end

    subgraph PROCESS["Обработка"]
        direction TB
        
        subgraph ROUTE["Маршрутизация"]
            CI[Классификация интента]
            DECISION{Тип запроса}
        end

        subgraph CHAT["Обработка чата"]
            KB[Поиск в базе знаний]
            VEC[Векторный поиск]
            RAG[Формирование контекста]
            LLM[Генерация ответа Ollama]
        end

        subgraph TAX["Налоговый расчет"]
            TC[Расчет налога]
            TL[Проверка лимита]
        end

        subgraph NEWS["Новости"]
            RSS[Парсинг RSS]
            FILTER[Фильтр по ключевым словам]
            SAVE[Сохранение в БД]
        end

        subgraph MONITOR["Мониторинг"]
            SCAN[Сканирование чатов]
            GROUP[Группировка по городам]
            ALERT[Оповещение о всплесках]
        end
    end

    subgraph STORAGE["Хранилища"]
        DB[(SQLite БД)]
        VDB[(Векторная БД)]
        CACHE[(Кэш)]
    end

    subgraph OUTPUT["Выходные данные"]
        ANS[Ответ пользователю]
        STAT[Статистика]
        DIGEST[Дайджест новостей]
        ALERTS[Оповещения о проблемах]
    end

    Q --> CI
    U --> CI
    CI --> DECISION

    DECISION -->|Вопрос о налогах| TAX
    DECISION -->|Вопрос о документах/выплатах| KB
    DECISION -->|Общий вопрос| LLM

    KB --> VEC
    VEC --> VDB
    VDB --> RAG
    RAG --> LLM
    LLM --> ANS

    TAX --> TC
    TC --> TL
    TL --> STAT
    STAT --> ANS

    N --> RSS
    RSS --> FILTER
    FILTER --> SAVE
    SAVE --> DB
    DB --> DIGEST

    C --> SCAN
    SCAN --> GROUP
    GROUP --> ALERT
    ALERT --> ALERTS

    ANS --> CACHE
    STAT --> CACHE
    DIGEST --> CACHE

    DB --> DIGEST
    DB --> STAT
    DB --> ALERTS
```

---

## Диаграммs последовательностей проекта DriveCore

### Диаграмма последовательности для чат-бота

```mermaid
sequenceDiagram
    participant User as Пользователь
    participant Web as Веб-интерфейс
    participant API as REST API
    participant AI as OllamaService
    participant KB as KnowledgeBase
    participant VDB as Векторная БД
    participant DB as Основная БД
    participant Cache as Кэш

    User->>Web: Вводит вопрос
    Web->>Web: Проверка авторизации
    Web->>API: POST /chat/ask/
    API->>Cache: Проверка кэша
    
    alt Ответ в кэше
        Cache-->>API: Возвращает кэшированный ответ
        API-->>Web: Ответ (from_cache: true)
        Web-->>User: Отображает ответ
    else Кэш пуст
        API->>AI: classify_intent(question)
        AI-->>API: intent (tax/documents/general)
        
        alt Вопрос о налогах
            API->>API: calculate_tax()
        else Вопрос о документах/выплатах
            API->>KB: search_knowledge_base(question)
            KB->>VDB: vector_search(query)
            VDB-->>KB: Результаты поиска
            KB-->>API: Документы
        end
        
        API->>AI: generate_response(question, context)
        AI->>LLM: Запрос к Ollama
        LLM-->>AI: Сгенерированный ответ
        AI-->>API: Ответ
        
        API->>DB: Сохранение истории
        DB-->>API: Запись сохранена
        
        API->>Cache: Сохранение в кэш
        Cache-->>API: Кэшировано
        
        API-->>Web: Ответ (from_cache: false)
        Web-->>User: Отображает ответ
    end
```

### Диаграмма последовательности для WebSocket чата

```mermaid
sequenceDiagram
    participant User as Пользователь
    participant WS as WebSocket
    participant Consumer as ChatConsumer
    participant AI as OllamaService
    participant KB as KnowledgeBase
    participant DB as Основная БД

    User->>WS: Подключение /ws/chat/{id}/
    WS->>Consumer: connect()
    Consumer->>DB: Проверка пользователя
    DB-->>Consumer: Пользователь найден
    Consumer-->>WS: accept()
    Consumer-->>User: Приветственное сообщение
    
    User->>WS: Отправка вопроса
    WS->>Consumer: receive(question)
    Consumer->>User: typing: true
    
    Consumer->>AI: classify_intent(question)
    AI-->>Consumer: intent
    
    Consumer->>KB: search_knowledge_base(question)
    KB-->>Consumer: Документы
    
    Consumer->>AI: generate_response(question, context)
    AI-->>Consumer: Ответ
    
    Consumer->>DB: save_chat_history()
    DB-->>Consumer: Сохранено
    
    Consumer->>User: typing: false
    Consumer-->>User: Ответ
    
    alt Ошибка
        Consumer-->>User: error
    end
    
    User->>WS: Закрытие соединения
    WS->>Consumer: disconnect()
    Consumer->>DB: Очистка сессии
```

### Диаграмма последовательности налогового калькулятора

```mermaid
sequenceDiagram
    participant User as Пользователь
    participant Web as Веб-интерфейс
    participant API as REST API
    participant Tax as TaxService
    participant Cache as Кэш
    participant DB as Основная БД

    User->>Web: Вводит доход и статус
    Web->>API: POST /taxes/calculate/
    
    API->>Cache: Проверка кэша
    alt Ответ в кэше
        Cache-->>API: Кэшированный результат
        API-->>Web: Результат (from_cache: true)
        Web-->>User: Отображает расчет
    else Кэш пуст
        API->>Tax: calculate(income, status, region)
        Tax->>Tax: Расчет по ставке
        Tax->>Tax: Проверка лимита
        Tax-->>API: TaxCalculationResult
        
        API->>DB: Сохранение расчета
        DB-->>API: Расчет сохранен
        
        API->>Cache: Сохранение в кэш
        Cache-->>API: Кэшировано
        
        API-->>Web: Результат (from_cache: false)
        Web-->>User: Отображает расчет
    end
```

### Диаграмма последовательности для новостей

```mermaid
sequenceDiagram
    participant Beat as Celery Beat
    participant Task as Celery Worker
    participant Parser as NewsParser
    participant RSS as RSS ленты
    participant DB as Основная БД
    participant Cache as Кэш
    participant TG as Telegram API

    Beat->>Task: Запуск задачи parse_news()
    
    Task->>Parser: parse_sources()
    
    loop Для каждого источника
        Parser->>RSS: GET /rss/
        RSS-->>Parser: XML лента
        Parser->>Parser: Парсинг новостей
        Parser->>Parser: Фильтр по ключевым словам ПЗ
    end
    
    Parser-->>Task: Список новостей
    
    loop Для каждой новости
        Task->>DB: Проверка существования
        DB-->>Task: Результат проверки
        alt Новость отсутствует
            Task->>DB: Сохранение новости
            DB-->>Task: Сохранено
        end
    end
    
    Task->>Cache: Очистка кэша новостей
    
    alt Дайджест
        Task->>DB: Получение новостей за день
        DB-->>Task: Список новостей
        Task->>TG: Отправка дайджеста
        TG-->>Task: Отправлено
    end
    
    Task-->>Beat: Задача выполнена
```

---

## Технологический стек

### Backend

| Технология | Версия | Назначение |
|------------|--------|------------|
| **Python** | 3.11 | Язык программирования |
| **Django** | 5.2.15 | Веб-фреймворк |
| **Django REST Framework** | 3.17.1 | REST API |
| **SQLite** | - | База данных |
| **Daphne** | 4.1.0 | ASGI сервер для WebSocket |
| **Channels** | 4.0.0 | WebSocket поддержка |
| **Celery** | 5.6.3 | Фоновые задачи |
| **JWT** | - | Аутентификация |

### AI и векторный поиск

| Технология | Назначение |
|------------|------------|
| **Ollama** | Локальная LLM (Llama 3.2) |
| **Sentence-Transformers** | Генерация векторных эмбеддингов |
| **RAG** | Retrieval-Augmented Generation |
| **Semantic Search** | Поиск по смыслу (векторный) |

### Frontend

| Технология | Назначение |
|------------|------------|
| **HTML5/CSS3** | Разметка и стилизация |
| **JavaScript (ES6+)** | Интерактивность и WebSocket |
| **Chart.js** | Графики на дашборде |

### Инструменты

| Инструмент | Назначение |
|------------|------------|
| **Docker** | Контейнеризация |
| **Docker Compose** | Оркестрация сервисов |
| **pytest** | Тестирование |
| **coverage.py** | Анализ покрытия кода |

---

## Архитектура проекта

### Диаграмма архитектуры

```mermaid
graph TB
    subgraph USERS["Пользователи"]
        U1["Водитель"]
        U2["Команда"]
        U3["Госорганы"]
    end

    subgraph CHANNELS["Каналы доступа"]
        WEB["Веб-приложение (HTML/CSS/JS)"]
        TG["Telegram-бот (@drive_core_bot)"]
    end

    subgraph BACKEND["Backend - Django 5.2 + DRF"]
        subgraph API_LAYER["API Layer"]
            REST["REST API"]
            WS["WebSocket (Daphne)"]
            ADMIN["Django Admin"]
        end

        subgraph MIDDLEWARE["Middleware"]
            AUTH["JWT Authentication"]
            PERM["Permissions (Driver/Team/Gov)"]
            CACHE["Django Cache"]
        end

        subgraph APPS["Django Apps"]
            USERS_APP["Users App"]
            CHAT_APP["Chat App"]
            TAX_APP["Tax App"]
            NEWS_APP["News App"]
            ANALYTICS_APP["Analytics App"]
        end

        subgraph AI_ENGINE["AI Engine"]
            OLLAMA["Ollama (Llama 3.2)"]
            RAG["RAG Pipeline"]
            EMB["Embeddings (sentence-transformers)"]
        end

        subgraph SERVICES["Services"]
            CHAT_SERVICE["ChatService"]
            TAX_SERVICE["TaxService"]
            KB_SERVICE["KnowledgeBase"]
        end

        subgraph ORM["Django ORM"]
            MODELS["Models: User, ChatHistory, TaxCalculation, NewsArticle"]
        end
    end

    subgraph DATA["Хранилища (SQLite)"]
        MAIN_DB[("Основная БД<br/>(users, chat_history,<br/>tax_calculations, news_articles)")]
        VECTOR_DB[("Векторная БД<br/>(documents, vectors)")]
        CACHE_DB[("Кэш<br/>(cache_table)")]
    end

    subgraph TASKS["Фоновые задачи (Celery)"]
        PARSER["Парсер новостей"]
        MONITOR["Мониторинг жалоб"]
        DIGEST["Дайджест"]
    end

    subgraph EXTERNAL["Внешние API"]
        TELEGRAM_API["Telegram API"]
        OLLAMA_API["Ollama API"]
        RSS["RSS ленты (ТАСС, РБК)"]
    end

    U1 --> WEB
    U1 --> TG
    U2 --> WEB
    U2 --> ADMIN
    U3 --> WEB

    WEB --> REST
    WEB --> WS
    TG --> REST

    REST --> AUTH
    REST --> PERM
    REST --> CACHE

    AUTH --> USERS_APP
    PERM --> USERS_APP
    CACHE --> CHAT_APP

    CHAT_APP --> CHAT_SERVICE
    CHAT_APP --> KB_SERVICE
    TAX_APP --> TAX_SERVICE

    CHAT_SERVICE --> OLLAMA
    CHAT_SERVICE --> RAG
    KB_SERVICE --> VECTOR_DB

    USERS_APP --> MODELS
    CHAT_APP --> MODELS
    TAX_APP --> MODELS
    NEWS_APP --> MODELS
    ANALYTICS_APP --> MODELS

    MODELS --> MAIN_DB
    MODELS --> CACHE_DB

    OLLAMA --> OLLAMA_API
    NEWS_APP --> RSS
    TG --> TELEGRAM_API

    PARSER --> NEWS_APP
    MONITOR --> CHAT_APP
    DIGEST --> NEWS_APP
    DIGEST --> TELEGRAM_API

    ADMIN --> MODELS
```

### Структура проекта

```
drivecore-django/
├── analytics/                         # Приложение аналитики и дашбордов
├── celery/                            # Конфигурация Celery
├── chat/                              # Приложение чата с ИИ
├── config/                            # Настройки проекта
├── core/                              # Ядро системы (AI, векторный поиск)
├── db.sqlite3                         # Основная база данных
├── docker-compose.yml                 # Docker Compose
├── Dockerfile                         # Docker образ
├── docs/                              # Документация
├── entrypoint.sh                      # Точка входа для Docker
├── frontend/                          # Фронтенд (HTML, CSS, JS)
├── htmlcov/                           # Отчёты о покрытии тестами
├── knowledge_base/                    # База знаний (документы)
├── logs/                              # Логи
├── manage.py                          # Управляющий скрипт Django
├── media/                             # Загруженные файлы
├── news/                              # Приложение новостей
├── ollama_data/                       # Данные Ollama (модели)
├── pytest.ini                         # Настройка pytest
├── README.md                          # Документация проекта
├── requirements.txt                   # Зависимости проекта
├── scripts/                           # Вспомогательные скрипты
├── staticfiles/                       # Собранная статика
├── taxes/                             # Приложение налогового калькулятора
├── telegram_bot/                      # Telegram бот
├── tests/                             # Тесты
├── users/                             # Приложение пользователей
├── vector_db.sqlite3                  # Векторная база данных
└── venv/                              # Виртуальное окружение
```

---

# Схема базы данных (ER-диаграмма)

```mermaid
erDiagram
LogEntry {
  integer id pk
  text action_time 
  integer user_id 
  integer content_type_id 
  text object_id 
  varchar object_repr 
  smallint_unsigned action_flag 
  text change_message 
}
Permission {
  integer id pk
  varchar name 
  integer content_type_id 
  varchar codename 
}
Group {
  integer id pk
  varchar name 
}
ContentType {
  integer id pk
  varchar app_label 
  varchar model 
}
Session {
  varchar session_key pk
  text session_data 
  text expire_date 
}
SolarSchedule {
  integer id pk
  varchar event 
  decimal latitude 
  decimal longitude 
}
IntervalSchedule {
  integer id pk
  integer every 
  varchar period 
}
ClockedSchedule {
  integer id pk
  text clocked_time 
}
CrontabSchedule {
  integer id pk
  varchar minute 
  varchar hour 
  varchar day_of_month 
  varchar month_of_year 
  varchar day_of_week 
  varchar timezone 
}
PeriodicTasks {
  smallint ident pk
  text last_update 
}
PeriodicTask {
  integer id pk
  varchar name 
  varchar task 
  integer interval_id 
  integer crontab_id 
  integer solar_id 
  integer clocked_id 
  text args 
  text kwargs 
  varchar queue 
  varchar exchange 
  varchar routing_key 
  text headers 
  integer_unsigned priority 
  text expires 
  integer_unsigned expire_seconds 
  bool one_off 
  text start_time 
  bool enabled 
  text last_run_at 
  integer_unsigned total_run_count 
  text date_changed 
  text description 
}
TaskResult {
  integer id pk
  varchar task_id 
  varchar periodic_task_name 
  varchar task_name 
  text task_args 
  text task_kwargs 
  varchar status 
  varchar worker 
  varchar content_type 
  varchar content_encoding 
  text result 
  text date_created 
  text date_started 
  text date_done 
  text traceback 
  text meta 
}
ChordCounter {
  integer id pk
  varchar group_id 
  text sub_tasks 
  integer_unsigned count 
}
GroupResult {
  integer id pk
  varchar group_id 
  text date_created 
  text date_done 
  varchar content_type 
  varchar content_encoding 
  text result 
}
User {
  integer id pk
  varchar password 
  text last_login 
  bool is_superuser 
  varchar username 
  varchar first_name 
  varchar last_name 
  varchar email 
  bool is_staff 
  bool is_active 
  text date_joined 
  varchar role 
  varchar status 
  varchar region 
  varchar telegram_id 
  varchar phone 
  decimal total_income 
  decimal tax_paid 
  decimal tax_rate 
  bool documents_verified 
  bool has_patent 
  varchar patent_region 
  text created_at 
  text updated_at 
  text last_active 
}
ChatHistory {
  integer id pk
  integer user_id 
  text question 
  text answer 
  varchar intent 
  real confidence 
  integer tokens_used 
  real response_time 
  bool is_helpful 
  text context 
  text meta 
  text created_at 
}
IntentLog {
  integer id pk
  text text 
  varchar predicted_intent 
  real confidence 
  bool is_correct 
  text created_at 
}
TaxCalculation {
  integer id pk
  integer user_id 
  decimal income 
  decimal tax_amount 
  decimal tax_rate 
  varchar status 
  varchar region 
  text created_at 
}
Document {
  integer id pk
  integer user_id 
  varchar title 
  varchar doc_type 
  text content 
  varchar file_path 
  text created_at 
}
NewsArticle {
  integer id pk
  varchar title 
  text summary 
  text full_text 
  varchar url 
  varchar source 
  varchar category 
  text published_at 
  text created_at 
}
Dashboard {
  integer id pk
  varchar name 
  text data 
  text created_at 
  text updated_at 
}
ChatHistory }|--|| User: ""
Document }|--|| User: ""
TaxCalculation }|--|| User: ""
Group }|--|{ User: ""
Group }|--|{ Permission: ""
LogEntry }|--|| User: ""
LogEntry }|--|| ContentType: ""
User }|--|{ Permission: ""
Permission }|--|| ContentType: ""
PeriodicTask }|--|| IntervalSchedule: ""
PeriodicTask }|--|| CrontabSchedule: ""
PeriodicTask }|--|| SolarSchedule: ""
PeriodicTask }|--|| ClockedSchedule: ""
```

## Описание таблиц

### Основные таблицы приложения

#### 1. `User` — Пользователи
Хранит информацию о всех пользователях системы: водителях, сотрудниках команды и представителях госорганов.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer PK | Уникальный идентификатор |
| `username` | varchar | Логин пользователя |
| `password` | varchar | Хеш пароля |
| `email` | varchar | Email пользователя |
| `role` | varchar | Роль: `driver` (водитель), `team` (команда), `gov` (госорганы) |
| `status` | varchar | Статус: `self_employed` (самозанятый), `ie` (ИП), `employee` (наёмный) |
| `region` | varchar | Регион работы |
| `telegram_id` | varchar | ID в Telegram для связи с ботом |
| `total_income` | decimal | Общий доход |
| `tax_paid` | decimal | Уплачено налогов |
| `tax_rate` | decimal | Текущая налоговая ставка |
| `documents_verified` | bool | Проверены ли документы |

#### 2. `ChatHistory` — История чатов
Хранит все диалоги пользователей с ИИ-ассистентом.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer PK | Уникальный идентификатор |
| `user_id` | integer FK | Ссылка на пользователя |
| `question` | text | Вопрос пользователя |
| `answer` | text | Ответ ИИ-ассистента |
| `intent` | varchar | Классификация вопроса: `tax`, `documents`, `payments`, `general` |
| `confidence` | real | Уверенность классификации (0-1) |
| `tokens_used` | integer | Количество токенов, использованных для генерации |
| `response_time` | real | Время генерации ответа (в секундах) |
| `is_helpful` | bool | Полезен ли ответ для пользователя |
| `context` | text (JSON) | Контекст пользователя на момент вопроса (статус, регион, доход) |

#### 3. `TaxCalculation` — Налоговые расчёты
Хранит историю налоговых расчётов для каждого пользователя.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer PK | Уникальный идентификатор |
| `user_id` | integer FK | Ссылка на пользователя |
| `income` | decimal | Доход для расчёта |
| `tax_amount` | decimal | Рассчитанная сумма налога |
| `tax_rate` | decimal | Применённая налоговая ставка |
| `status` | varchar | Статус пользователя на момент расчёта |
| `region` | varchar | Регион пользователя |

#### 4. `NewsArticle` — Новости
Хранит новости, собранные из RSS-лент.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer PK | Уникальный идентификатор |
| `title` | varchar | Заголовок новости |
| `summary` | text | Краткое содержание |
| `full_text` | text | Полный текст новости |
| `url` | varchar | Ссылка на источник |
| `source` | varchar | Источник новости (ТАСС, РБК) |
| `category` | varchar | Категория: `platform_employment` (ПЗ), `general` (общие) |
| `published_at` | text | Дата публикации |

#### 5. `Document` — Документы
Хранит сгенерированные документы (отчёты, справки).

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer PK | Уникальный идентификатор |
| `user_id` | integer FK | Ссылка на пользователя |
| `title` | varchar | Название документа |
| `doc_type` | varchar | Тип: `report`, `certificate`, `contract`, `invoice` |
| `content` | text (JSON) | Содержание документа |
| `file_path` | varchar | Путь к файлу на диске |

---

### Системные таблицы Django

#### 6. `LogEntry` — Логи действий
Журнал действий в админ-панели Django.

#### 7. `Group` — Группы пользователей
Группы для управления правами доступа.

#### 8. `Permission` — Разрешения
Права доступа для пользователей и групп.

#### 9. `ContentType` — Типы контента
Метаданные о моделях Django (используется для разрешений).

#### 10. `Session` — Сессии
Хранит активные сессии пользователей.

---

### Таблицы Celery (фоновые задачи)

#### 11. `PeriodicTask` — Периодические задачи
Настройки периодических задач для Celery Beat.

#### 12. `IntervalSchedule` — Интервалы
Расписания для периодических задач (каждые N минут/часов/дней).

#### 13. `CrontabSchedule` — Cron-расписания
Расписания в формате cron.

#### 14. `TaskResult` — Результаты задач
Результаты выполнения фоновых задач.

#### 15. `GroupResult` — Результаты групп задач
Результаты выполнения групп задач.

---

## Связи между таблицами

```
User → ChatHistory: Один пользователь может иметь много чатов (1:N)
User → TaxCalculation: Один пользователь может иметь много налоговых расчётов (1:N)
User → Document: Один пользователь может иметь много документов (1:N)
User ↔ Group: Пользователи могут состоять в нескольких группах (N:N)
User ↔ Permission: Пользователи могут иметь несколько разрешений (N:N)
Group ↔ Permission: Группы могут иметь несколько разрешений (N:N)
```

---

## Дополнительные таблицы (модули)

### `IntentLog` — Логи классификации интентов
Используется для анализа точности классификации вопросов.

### `Dashboard` — Дашборды
Хранит настройки и данные для дашбордов.

---

## Запуск проекта

### Предварительные требования

- Python 3.11 или выше
- Docker Desktop (для Docker-запуска)
- 4 ГБ свободной оперативной памяти
- Порт 8000 свободен

### Вариант 1: Локальный запуск

#### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/yourusername/drivecore-django.git
cd drivecore-django
```

#### Шаг 2: Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

#### Шаг 4: Создание переменных окружения

Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=django-insecure-key-for-dev
DEBUG=True
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
TELEGRAM_BOT_TOKEN=ваш_токен_бота
```

#### Шаг 5: Установка и запуск Ollama

```bash
# Установка Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Запуск Ollama
ollama serve

# Скачать модель
ollama pull llama3.2:3b
```

#### Шаг 6: Настройка базы данных

```bash
# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Обновление базы знаний
python scripts/update_knowledge_base.py

# Индексация векторов
python scripts/index_knowledge_base.py
```

#### Шаг 7: Запуск проекта

```bash
# Запуск Daphne (WebSocket + HTTP)
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

#### Шаг 8: Запуск Celery (фоновые задачи)

```bash
# В отдельном терминале
celery -A config worker --loglevel=info
```

#### Шаг 9: Запуск Telegram бота (опционально)

```bash
# В отдельном терминале
python telegram_bot/bot.py
```

### Вариант 2: Запуск через Docker

#### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/yourusername/drivecore-django.git
cd drivecore-django
```

#### Шаг 2: Создание переменных окружения

Создайте файл `.env`:

```env
SECRET_KEY=django-insecure-key-for-docker
DEBUG=False
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3.2:3b
TELEGRAM_BOT_TOKEN=ваш_токен_бота
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

#### Шаг 3: Сборка и запуск

```bash
# Сборка образов
docker-compose build

# Запуск всех сервисов
docker-compose up -d

# Запуск с Telegram ботом
docker-compose --profile telegram up -d
```

#### Шаг 4: Доступ к приложению

| URL | Назначение |
|-----|------------|
| http://localhost:8000/ | Главная страница |
| http://localhost:8000/admin/ | Панель администратора |
| http://localhost:8000/swagger/ | API документация |  

#### Шаг 5: Управление Docker

```bash
# Просмотр статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f web

# Остановка
docker-compose down

# Остановка с удалением томов
docker-compose down -v
```

---

## Тестирование

### Запуск тестов

```bash
# Запуск всех тестов с покрытием
python -m pytest tests/ -v --cov=. --cov-report=term

# Запуск конкретного файла
python -m pytest tests/test_models.py -v

# Отчёт о покрытии в HTML
python -m pytest tests/ --cov=. --cov-report=html
```

### Покрытие тестами

| Компонент | Покрытие |
|-----------|----------|
| Модели (models) | ~90% |
| Сериализаторы (serializers) | ~75% |
| Сервисы (services) | ~85% |
| API Views | ~70% |
| Celery задачи (tasks) | ~70% |
| Утилиты (utils/decorators) | ~50% |
| **Общее покрытие** | **~70%** |

---

## API Документация

После запуска доступна Swagger документация:

- http://localhost:8000/swagger/

### Основные эндпоинты

| Метод | URL | Назначение |
|-------|-----|------------|
| POST | `/api/v1/auth/login/` | Вход в систему |
| POST | `/api/v1/auth/refresh/` | Обновление JWT |
| POST | `/api/v1/chat/ask/` | Задать вопрос ИИ |
| GET | `/api/v1/chat/` | История чатов |
| POST | `/api/v1/taxes/calculate/` | Расчёт налогов |
| GET | `/api/v1/taxes/rates/` | Налоговые ставки |
| GET | `/api/v1/analytics/stats/` | Статистика |
| GET | `/api/v1/analytics/problems/` | Мониторинг проблем |
| GET | `/api/v1/news/latest/` | Последние новости |
| GET | `/api/v1/users/me/` | Текущий пользователь |

### WebSocket

| URL | Назначение |
|-----|------------|
| `ws://localhost:8000/ws/chat/{user_id}/` | Чат в реальном времени |

---

## Telegram Бот

### Ссылка на бота

[@drive_core_bot](https://t.me/drive_core_bot)

### Команды

| Команда | Описание |
|---------|----------|
| `/start` | Начать работу (регистрация) |
| `/help` | Помощь |
| `/status` | Статус пользователя |
| `/tax` | Налоговый калькулятор |

### Пример диалога

```
Пользователь: /start
Бот: Привет! Выберите свою роль...

Пользователь: Я водитель
Бот: Роль выбрана. Теперь укажи свой статус...

Пользователь: Самозанятый
Бот: Статус сохранён! Задайте вопрос...

Пользователь: Сколько налогов платит самозанятый?
Бот: Самозанятые платят 4% с физлиц и 6% с юрлиц...
```

---

## Лицензия

MIT License