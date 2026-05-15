# Docker

Проект сейчас рассчитан на локальный запуск через Docker Compose. Отдельно запускать backend через venv и frontend через `npm run dev` не требуется.

## Сервисы

`docker-compose.yml` поднимает:

- `backend` — Django/DRF/Channels на `http://localhost:8000`
- `frontend` — Vite dev server на `http://localhost:5173`
- `sqlite_data` volume — используется только если включён SQLite fallback
- `frontend_node_modules` volume — зависимости frontend внутри контейнера

Backend command:

```bash
python -m pip install -r /app/requirements.txt &&
python manage.py migrate --noinput &&
python manage.py runserver 0.0.0.0:8000
```

Это сделано для dev-режима: контейнер сам подтягивает новые Python-зависимости и применяет миграции.

## Первый запуск на Windows

Откройте терминал в папке проекта.

1. Скопируйте env:

```powershell
cp .env.example .env
```

Если PowerShell не принимает `cp`, используйте:

```powershell
copy .env.example .env
```

2. Откройте `.env`:

```powershell
notepad .env
```

Для Docker используется корневой `.env` рядом с `docker-compose.yml`; `frontend/.env` отдельно не нужен.

3. Создайте PostgreSQL-базу:

```powershell
createdb -U postgres lev
```

Если `createdb` не найден, создайте базу `lev` через pgAdmin.

4. Проверьте `DATABASE_URL` в `.env`:

```env
DATABASE_URL=postgresql://postgres:1234@host.docker.internal:5432/lev
```

Если пароль PostgreSQL не `1234`, замените его в строке.

5. Запустите Docker Desktop и выполните:

```powershell
docker compose up --build
```

Адреса:

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000/api/`
- Admin: `http://localhost:8000/admin/`

## Основные команды

Запустить:

```powershell
docker compose up --build
```

Запустить в фоне:

```powershell
docker compose up -d --build
```

Остановить:

```powershell
docker compose down
```

Остановить и удалить volumes:

```powershell
docker compose down -v
```

Пересобрать всё:

```powershell
docker compose build --no-cache
docker compose up
```

Пересобрать только backend:

```powershell
docker compose build --no-cache backend
docker compose up backend
```

Пересобрать только frontend:

```powershell
docker compose build --no-cache frontend
docker compose up frontend
```

Посмотреть запущенные контейнеры:

```powershell
docker compose ps
```

Логи всех сервисов:

```powershell
docker compose logs -f
```

Логи backend:

```powershell
docker compose logs -f backend
```

Логи frontend:

```powershell
docker compose logs -f frontend
```

Зайти в shell backend-контейнера:

```powershell
docker compose exec backend sh
```

Зайти в shell frontend-контейнера:

```powershell
docker compose exec frontend sh
```

## Django-команды через Docker

Проверка проекта:

```powershell
docker compose exec backend python manage.py check
```

Миграции:

```powershell
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

Создать superuser:

```powershell
docker compose exec backend python manage.py createsuperuser
```

Django shell:

```powershell
docker compose exec backend python manage.py shell
```

Список URL/эндпоинтов смотрите в `README.md`.

## ADS-API sync

Заполните `.env`:

```env
ADS_API_USER=
ADS_API_TOKEN=
ADS_API_BASE_URL=https://ads-api.ru/main/api
ADS_API_CATEGORY_FLATS=1
```

Запустить импорт:

```powershell
docker compose exec backend python manage.py sync_ads_listings
```

С городом:

```powershell
docker compose exec backend python manage.py sync_ads_listings --city="Санкт-Петербург"
```

С ценой:

```powershell
docker compose exec backend python manage.py sync_ads_listings --price-min=5000000 --price-max=15000000
```

С лимитом:

```powershell
docker compose exec backend python manage.py sync_ads_listings --limit=50
```

С `startid`:

```powershell
docker compose exec backend python manage.py sync_ads_listings --startid=670000000 --limit=50
```

Параметры команды:

- `--city` — город
- `--price-min` — минимальная цена
- `--price-max` — максимальная цена
- `--startid` — ADS id, с которого начинать импорт
- `--limit` — лимит объявлений

Если ADS возвращает `401`, неверные `ADS_API_USER` или `ADS_API_TOKEN`.

Если ADS возвращает `402`, доступ/token истёк или не оплачен.

## Env для Docker

Основные переменные:

```env
DJANGO_SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=*
DATABASE_URL=postgresql://postgres:1234@host.docker.internal:5432/lev
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

OPENROUTER_TOKEN=
OPENROUTER_API=https://openrouter.ai/api/v1/chat/completions
OPENROUTER_TIMEOUT_SECONDS=30
OPENROUTER_MODEL=openai/gpt-4o-mini

YANDEX_GEOCODER_API_KEY=
ADS_API_USER=
ADS_API_TOKEN=
ADS_API_BASE_URL=https://ads-api.ru/main/api
ADS_API_CATEGORY_FLATS=1

BACKEND_PORT=8000
FRONTEND_PORT=5173
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
VITE_YANDEX_MAPS_API_KEY=
```

Это основной вариант для локального запуска на Windows/macOS: PostgreSQL работает на хосте, backend-контейнер подключается к нему через `host.docker.internal`.

Перед запуском создайте базу:

```powershell
createdb -U postgres lev
```

Если у вас другой пользователь, пароль, порт или имя базы, поменяйте `DATABASE_URL`, например:

```env
DATABASE_URL=postgresql://user:password@host.docker.internal:5432/dbname
```

SQLite можно использовать только как быстрый fallback:

```env
DATABASE_URL=sqlite:////app/data/db.sqlite3
```

## Полный reset

Если нужно снести контейнеры и Docker volumes:

```powershell
docker compose down -v --remove-orphans
docker compose build --no-cache
docker compose up
```

Если проект работает через PostgreSQL на хосте, volume reset не очищает PostgreSQL. Для полного сброса базы:

```powershell
dropdb lev
createdb -U postgres lev
docker compose up --build
```

## Частые проблемы

### `ModuleNotFoundError: No module named ...`

Контейнер собран из старого image. Решение:

```powershell
docker compose build --no-cache backend
docker compose up backend
```

### Frontend не видит API

Проверьте `.env`:

```env
VITE_API_URL=http://localhost:8000/api
```

После изменения env перезапустите frontend:

```powershell
docker compose restart frontend
```

### WebSocket 404

Проверьте:

```env
VITE_WS_URL=ws://localhost:8000
```

И перезапустите backend:

```powershell
docker compose restart backend
```

### Нужно посмотреть, что внутри backend-контейнера

```powershell
docker compose exec backend sh
python -m pip list
python manage.py check
```
