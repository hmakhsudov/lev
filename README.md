# Lev — AI Real-Estate Platform

Полноценная платформа для поиска недвижимости с AI-помощником. Бэкенд на Django + DRF, фронтенд на Vue 3 (Vite, script setup, SCSS).

## Структура

```
├── backend/        # Django проект (accounts, real_estate, assistant, core)
├── frontend/       # Vite + Vue 3 приложение
├── .env.example    # Переменные окружения для бэкенда
└── README.md
```

## Подготовка окружения

1. Скопируйте `.env.example` в `.env` и заполните ключи:
   ```dotenv
   DJANGO_SECRET_KEY=your-secret
   DEBUG=True
   DATABASE_URL=sqlite:///db.sqlite3
   OPENAI_API_KEY=sk-...
   YANDEX_GEOCODER_API_KEY=...
   ADS_API_USER=...
   ADS_API_TOKEN=...
   ADS_API_BASE_URL=https://ads-api.ru/main/api
   ADS_API_CATEGORY_FLATS=1
   CORS_ALLOWED_ORIGINS=http://localhost:5173
   ```
2. Для фронтенда создайте `frontend/.env` на основе `frontend/.env.example`:
   ```dotenv
   VITE_API_URL=http://localhost:8000/api
   VITE_OPENAI_KEY=sk-...
   VITE_YANDEX_MAPS_API_KEY=...
   ```

## Запуск бэкенда

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # по желанию
python manage.py runserver
```

Основные эндпоинты (`/api/...`):
- `auth/register/`, `auth/login/`, `auth/me/`, `auth/agents/`
- `properties/` с фильтрами (`min_price`, `max_price`, `rooms`, `district`, `property_type`, `area_min`, `area_max`, `order_by=price|-price`)
- `properties/sync/` и `properties/sync-external/` + `properties/geocode/` (для агентов/админов)
- `assistant/parse-query/` — прокси к OpenAI, возвращает структурированные фильтры
- `core/health/`

### Синхронизация с ADS-API

- Бэкенд хранит объявления локально в таблице `real_estate_property`. Любой поиск/фильтры на фронтенде работают только по нашей БД.
- Для импорта используйте один из вариантов:
  - **Management-команда**: `python manage.py sync_ads_listings --city="Санкт-Петербург" --price-max=15000000 --limit=200`
  - **REST эндпоинт** (только агент/админ): `POST /api/properties/sync-external/` с JSON-параметрами `city`, `price_min`, `price_max`, `limit`.
- Синк использует `startid`, чтобы подтягивать только новые объявления, и перезаписывает фотографии/основную информацию по `external_id + source`.
- Переменные `ADS_API_USER`, `ADS_API_TOKEN`, `ADS_API_CATEGORY_FLATS` должны быть выданы ADS-API (https://ads-api.ru).

## Запуск фронтенда

```bash
cd frontend
npm install
npm run dev
```

UI доступен на `http://localhost:5173`. Все подписи интерфейса на русском, карта использует ключ `VITE_YANDEX_MAPS_API_KEY`.

## Работа с AI и геокодером

- **OpenAI**: ключ используется на бэкенде (преобразование запроса в фильтры) и может быть повторно использован на фронтенде при необходимости интеграций.
- **Yandex Geocoder**: бэкенд обновляет координаты объектов (эндпоинт `/api/properties/geocode/`). Фронтенд использует `VITE_YANDEX_MAPS_API_KEY` для отображения карты и маркеров.

## Следующие шаги

- Настроить PostgreSQL, обновив `DATABASE_URL` (например, `postgresql://user:pass@localhost:5432/lev`).
- Подключить реальный API CIAN и обработку изображений.
- Добавить e2e-тесты и production-конфигурацию (Docker, CI/CD).
