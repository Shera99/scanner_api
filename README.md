# Scanner API

Бэкенд для мобильного приложения сканера билетов. Работает с общей базой Sxodim/ShowGo.

## Стек

- Python 3.14, FastAPI, SQLAlchemy 2.0 (async), asyncpg
- PostgreSQL (удалённая БД через SSL)
- JWT-авторизация (PyJWT + bcrypt)

## Быстрый старт

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Скопировать `.env.example` → `.env` и заполнить доступы к БД.

```bash
python run.py
```

Сервер поднимется на `http://localhost:5001`. Swagger — `/docs`.

## Переменные окружения

| Переменная | Описание |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Подключение к PostgreSQL |
| `DB_PGBOUNCER` | `true`, если перед БД стоит pgbouncer в transaction-режиме (KZ). Отключает кэши prepared statements и включает уникальные имена для них. Для прямого подключения к Postgres — `false` (по умолчанию) |
| `DB_POOL_SIZE` | Размер пула соединений (по умолчанию `10`) |
| `DB_MAX_OVERFLOW` | Сколько соединений можно открыть сверх пула (по умолчанию `10`). Потолок от сервиса = `DB_POOL_SIZE + DB_MAX_OVERFLOW`; сверять с `max_client_conn` у pgbouncer либо с `max_connections` у Postgres |
| `SECRET_KEY` | Ключ для подписи JWT |
| `ACCESS_TOKEN_EXPIRE_DAYS` | Срок жизни токена (дни) |
| `DEFAULT_COUNTRY_CODE` | Код страны по умолчанию (`uz`) |
| `TIME_ZONE_DIFFERENCE` | Разница с UTC в часах |

## Структура

```
src/
├── core/              # конфиг, enums, exceptions, утилиты
├── application/
│   ├── repositories/  # абстрактные репозитории (интерфейсы)
│   ├── schemas/       # pydantic-схемы (request/response/dto)
│   └── services/      # бизнес-логика (auth, scan/check, events, tickets, statistics)
├── infrastructure/
│   ├── database/      # модели, конкретные репозитории, сессия
│   ├── dependencies/  # DI для FastAPI (auth, scan сервисы)
│   ├── middleware/     # auth middleware, request logging
│   └── security/      # JWT encode/decode
└── presentation/
    └── v1/            # роуты (auth, scan/*)
```

## API

`POST /api/v1/auth/` — логин, возвращает JWT с `permission_id`

Все остальные эндпоинты требуют `Authorization: Bearer <token>`:

- `GET /api/v1/event/list` — список сессий на сегодня
- `POST /api/v1/check` — сканирование билета (вход/выход)
- `GET /api/v1/ticket/list/{session_id}` — список билетов сессии
- `GET /api/v1/ticket/search/{session_id}/{ticket_number}` — поиск по номеру
- `GET /api/v1/ticket/search/by_mail/{session_id}/{email}` — поиск по email
- `GET /api/v1/statistics/{session_id}` — статистика продаж/сканирований

## Логи

Пишутся в `logs/YYYY/MM/DD.log` — каждый запрос с заголовками, телом, статусом и временем ответа.
