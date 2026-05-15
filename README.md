# Lev Estate

Платформа недвижимости на Django + DRF и Vue 3. Проект запускается локально через Docker Compose: backend, frontend, миграции, API, WebSocket-чаты и загрузка медиа работают внутри общей docker-сборки.

## Что внутри

- Backend: Django, DRF, SimpleJWT, Channels/WebSocket, ADS-API sync, OpenRouter assistant.
- Frontend: Vue 3, Vite, Pinia, Vue Router, SCSS, Yandex Maps.
- Основные функции: каталог объектов, фильтры, AI-ассистент, избранное, личный кабинет, панель агента, админ-панель, диалоги с агентами.

## Быстрый запуск на Windows через Docker

Этот раздел рассчитан на запуск проекта на другом компьютере с Windows. Нужно, чтобы были установлены и запущены:

- Docker Desktop
- PostgreSQL
- Git или скачанный архив проекта

Python и Node.js вручную запускать не нужно: backend и frontend стартуют через Docker.

### 1. Откройте проект

Откройте PowerShell в папке проекта, где лежит `docker-compose.yml`.

Если проект скачан через git:

```powershell
git clone <URL_РЕПОЗИТОРИЯ>
cd lev
```

Если проект скачан архивом, распакуйте его и откройте PowerShell в распакованной папке.

### 2. Создайте `.env`



Скопируйте файл env.example в .env


Откройте `.env` 

Для Docker-запуска нужен именно корневой `.env` рядом с `docker-compose.yml`

### 3. Создайте базу PostgreSQL

создайте базу через pgAdmin если ее нет:

1. Откройте pgAdmin.
2. Подключитесь к серверу PostgreSQL.
3. Правой кнопкой по `Databases`.
4. `Create` → `Database`.
5. Имя базы: `lev`.

### 4. Проверьте `.env`

В `.env` должна быть строка подключения к PostgreSQL. Если пароль PostgreSQL `1234`, оставьте так:

```env
DATABASE_URL=postgresql://postgres:1234@host.docker.internal:5432/lev
```

Если пароль другой, замените `1234` на свой пароль:

```env
DATABASE_URL=postgresql://postgres:ВАШ_ПАРОЛЬ@host.docker.internal:5432/lev
```

Остальные важные строки для локального запуска:

```env
DJANGO_SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=*
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

BACKEND_PORT=8000
FRONTEND_PORT=5173
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
```

Ключи OpenRouter, Yandex и ADS-API можно заполнить сразу или позже:

```env
OPENROUTER_TOKEN=
OPENROUTER_API=https://openrouter.ai/api/v1/chat/completions
OPENROUTER_TIMEOUT_SECONDS=30
OPENROUTER_MODEL=openai/gpt-4o-mini

VITE_YANDEX_MAPS_API_KEY=
YANDEX_GEOCODER_API_KEY=

ADS_API_USER=
ADS_API_TOKEN=
ADS_API_BASE_URL=https://ads-api.ru/main/api
ADS_API_CATEGORY_FLATS=1
```

### 5. Запустите проект

Убедитесь, что Docker Desktop запущен. Затем в PowerShell:

```powershell
docker compose up --build
```

Первый запуск может занять несколько минут. Backend сам установит зависимости и применит миграции.

Откройте:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api/`
- Django admin: `http://localhost:8000/admin/`

### 6. Если нужно остановить проект

В окне, где запущен Docker Compose, нажмите `Ctrl+C`.

Или

docker compose down

## Аккаунты

После миграций создаётся дефолтный администратор:

```text
email: admin@admin.admin
password: Admin1234
```

Публичная регистрация создаёт обычного пользователя. Аккаунты агентов создаются администратором в админ-панели сайта.

## Полезные Docker-команды

Запуск в foreground:

```powershell
docker compose up --build
```

Запуск в фоне:

```powershell
docker compose up -d --build
```

Остановить контейнеры:

```powershell
docker compose down
```

Полный сброс контейнеров и Docker volumes:

```powershell
docker compose down -v --remove-orphans
```

Пересобрать backend без cache:

```powershell
docker compose build --no-cache backend
docker compose up
```

Логи backend:

```powershell
docker compose logs -f backend
```

Логи frontend:

```powershell
docker compose logs -f frontend
```

Выполнить Django-команду:

```powershell
docker compose exec backend python manage.py <command>
```

Применить миграции вручную:

```powershell
docker compose exec backend python manage.py migrate
```

Создать superuser вручную:

```powershell
docker compose exec backend python manage.py createsuperuser
```

## Парсинг объектов из ADS-API

Объекты из ADS-API импортируются в локальную БД командой `sync_ads_listings`. Сайт показывает объекты из нашей базы, поэтому после парсинга они появляются на главной странице, в поиске, на карте и в админке.

Перед импортом заполните в `.env`:

```env
ADS_API_USER=your_ads_api_login
ADS_API_TOKEN=your_ads_api_token
ADS_API_BASE_URL=https://ads-api.ru/main/api
ADS_API_CATEGORY_FLATS=1
```

Базовый импорт:

```powershell
docker compose exec backend python manage.py sync_ads_listings
```

Импорт по городу:

```powershell
docker compose exec backend python manage.py sync_ads_listings --city="Санкт-Петербург"
```

Импорт с фильтром по цене:

```powershell
docker compose exec backend python manage.py sync_ads_listings --city="Москва" --price-min=8000000 --price-max=20000000
```

Ограничить количество:

```powershell
docker compose exec backend python manage.py sync_ads_listings --city="Санкт-Петербург" --limit=50
```

Инкрементальная загрузка с ADS id:

```powershell
docker compose exec backend python manage.py sync_ads_listings --startid=670000000 --limit=50
```

Команда выводит итог:

```text
ADS sync finished: created=10, updated=5, total=50, skipped=0
```

Если ADS-API возвращает `401`, проверьте `ADS_API_USER` и `ADS_API_TOKEN`. Если `402`, срок доступа/token истёк или доступ не оплачен на стороне ADS-API.

## AI-ассистент

AI-ассистент использует OpenRouter. Заполните:

```env
OPENROUTER_TOKEN=sk-or-...
OPENROUTER_API=https://openrouter.ai/api/v1/chat/completions
OPENROUTER_TIMEOUT_SECONDS=30
```

Опционально можно задать модель:

```env
OPENROUTER_MODEL=openai/gpt-4o-mini
```

Endpoint ассистента: `POST /api/assistant/parse-query/`.

## Карты и геокодер

Для карт на фронтенде нужен:

```env
VITE_YANDEX_MAPS_API_KEY=...
```

Для backend-геокодирования:

```env
YANDEX_GEOCODER_API_KEY=...
```

Массовое геокодирование:

```powershell
docker compose exec backend python manage.py shell
```

Или используйте endpoint `/api/properties/geocode/`, если он вызывается из панели администратора/агента.

## Основные API

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `GET/PATCH /api/auth/me/`
- `GET /api/properties/`
- `POST /api/properties/`
- `PATCH /api/properties/<id>/`
- `DELETE /api/properties/<id>/`
- `GET /api/favorites/`
- `POST /api/favorites/`
- `GET /api/chat/conversations/`
- `POST /api/chat/conversations/`
- `WS /ws/chat/<conversation_id>/?token=<access_token>`

## Типовые проблемы

Если после добавления новой Python-библиотеки Docker пишет `ModuleNotFoundError`, пересоберите backend:

```powershell
docker compose build --no-cache backend
docker compose up
```

Если база в SQLite испорчена или хочется начать с чистой:

```powershell
docker compose down -v
docker compose up --build
```

Если используется PostgreSQL, `docker compose down -v` не удаляет вашу PostgreSQL-базу на хосте. Для полного сброса PostgreSQL пересоздайте базу вручную:

```powershell
dropdb lev
createdb -U postgres lev
docker compose up --build
```

Если frontend не видит backend, проверьте:

```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
```

Если WebSocket не подключается, убедитесь, что backend запущен через текущую Django/Channels конфигурацию и URL имеет вид:

```text
ws://localhost:8000/ws/chat/<conversation_id>/?token=<access_token>
```
