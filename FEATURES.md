# Полный обзор функционала Lev Estate

Этот документ описывает все ключевые возможности платформы Lev Estate — AI‑ассистированной системы подбора недвижимости, состоящей из Django/DRF бэкенда и фронтенда на Vue 3.

## 1. Архитектура
- **Бэкенд**: Django + Django REST Framework, SQLite по умолчанию (через `DATABASE_URL` легко переключается на PostgreSQL). JWT‑аутентификация на базе SimpleJWT, поддержка CORS и конфигурации через `.env`.
- **Фронтенд**: Vue 3 (script setup) + Vite + SCSS. Используются Pinia (состояние), vue-router, axios, Swiper, FloatingVue, Iconify, Motion.
- **Интеграции**: OpenRouter API (парсинг естественного запроса в фильтры) и Yandex Geocoder API (координаты и карта).
- **Структура**:
  - `backend/` — проект `django_project` и приложения `accounts`, `real_estate`, `assistant`, `core`.
  - `frontend/` — SPA с маршрутами для поиска, карточек, ассистента, панели агента и auth.

## 2. Бэкенд
### 2.1 Приложение `accounts`
- Пользовательская модель с ролями `user`, `agent`, `admin` (email — логин).
- Эндпоинты (`/api/auth/`):
  - `register/` — регистрация.
  - `login/` — JWT (access/refresh).
  - `token/refresh/` — обновление токена.
  - `me/` — текущий пользователь (JWT).
  - `agents/` — список агентов.

### 2.2 Приложение `real_estate`
- Модели: `Property` (основная информация, координаты, изображения) и `PropertyImage`.
- CRUD‑вьюсет `PropertyViewSet` (`/api/properties/`).
  - **GET** `/` — список с фильтрами `min_price`, `max_price`, `rooms`, `district`, `property_type`, `area_min`, `area_max`, `order_by=price|-price`.
  - **GET** `/<id>/` — детальная карточка (включая галерею).
  - **POST/PUT/PATCH/DELETE** — только агенты и админы.
  - **POST** `/sync/` — заглушка интеграции с CIAN (создаёт/обновляет объекты).
  - **POST** `/geocode/` — геокодирование всех объектов через Yandex API.
- Сервисы: `CIANClient` (mock), `YandexGeocoder` (получение широты/долготы и сохранение).

### 2.3 Приложение `assistant`
- Эндпоинт `/api/assistant/parse-query/` принимает `{ "query": "..." }`.
- Вызов OpenRouter Chat Completions с системной подсказкой → строгий JSON с полями `rooms`, `price_max`, `district`, `city`, `property_type`.
- Ошибки OpenRouter преобразуются в HTTP 503 с описанием.

### 2.4 Приложение `core`
- `/api/core/health/` — healthcheck (AllowAny). Используется мониторингом и фронтендом.

### 2.5 Конфигурация и безопасность
- `settings.py`: чтение `.env`, подключение `dj_database_url`, CORS, статические файлы, SimpleJWT.
- `.env.example` определяет ключи: `DJANGO_SECRET_KEY`, `DEBUG`, `DATABASE_URL`, `OPENROUTER_TOKEN`, `OPENROUTER_API`, `OPENROUTER_TIMEOUT_SECONDS`, `YANDEX_GEOCODER_API_KEY`, `CORS_ALLOWED_ORIGINS`.

## 3. Фронтенд
### 3.1 Главная (`/`)
- **Hero-секция**: описание сервиса, статистика, кнопки.
- **AI‑инпут**: компонент `AssistantInput` (textarea + подсказки), отправляет запрос на `/assistant/parse-query/` и обновляет фильтры.
- **Панель фильтров**: `FilterForm` с городом, районом, типом, комнатами, ценой, площадью.
- **Листинг объектов**: `ListingCard` с галереей (Swiper), бейджами, иконками метрик, действиями (переход/фокус на карте).
- **Карта**: `ListingsMap` на Yandex Maps, кастомные маркеры с ценой, подсказки при ховере.
- Состояния: skeleton‑карты, пустые состояния, переключение списка/сеток, адаптивность.

### 3.2 Карточка объекта (`/property/:id`)
- Галерея (Swiper) + пагинация/навигация.
- Блок цены, вычисленный `pricePerMeter`, метрики (комнаты, площадь, этаж, тип).
- Описание, карта объекта, sticky-sidebar:
  - Карточка агента (контакты).
  - Слайдер «Похожие объекты» (подбор по району/комнатам).

### 3.3 Страница ассистента (`/assistant`)
- Панель с историей запросов и советами AI.
- Ввод произвольного описания → отображение распознанных фильтров в карточках.

### 3.4 Панель агента (`/admin`)
- Заголовок с действиями «Синхронизация CIAN» и «Геокодировать» (POST `/properties/sync/`, `/properties/geocode/`).
- Форма создания объекта: название, цена, площадь, комнаты, этажность, адрес, тип, описание, список изображений.
- Список объектов агента (тот же `ListingCard`).

### 3.5 Аутентификация (`/login`, `/register`)
- Страницы с современными формами, подсказками и ссылками.
- Регистрация поддерживает выбор роли (`user`/`agent`).
- JWT токен сохраняется в `localStorage`, Pinia `auth` стор оборачивает login/register/logout/me.

## 4. Компоненты и UX
- **UI Kit**: `BaseButton`, `BaseField`, `BaseChip`, `SkeletonBlock`, `MetricPill` — базовая типографика/иконки/шадоу.
- **Анимации**: VueUse Motion (fade/slide), плавные hover эффекты, Swiper transitions.
- **Иконки**: Iconify (навигация, фильтры, метрики, статусы).
- **Состояния**: Skeleton loaders, пустые состояния с иллюстрациями, всплывающие подсказки (FloatingVue).
- **Адаптив**: гриды перестраиваются для планшетов/мобил, sticky элементы отключаются на узких экранах.

## 5. Интеграции и окружение
- `.env.example` (корень) — ключи для бэкенда и фронтенда: `VITE_API_URL`, `VITE_WS_URL`, `VITE_YANDEX_MAPS_API_KEY`.
- Все сетевые вызовы frontend выполняет через `axios` инстанс `services/api.js` (авто‑добавление JWT в заголовок `Authorization`).
- Карта загружается динамически (добавление <script> + Promise), маркеры создаются из JSON‑ответа бэкенда.

## 6. Как пользователь взаимодействует
1. **Гость**: открывает `/`, вводит текстовый запрос, получает фильтры + подбор, просматривает объекты, строит маршрут по карте.
2. **Авторизованный пользователь**: получает доступ к сохранению JWT, видит персонализированный `me/` ответ.
3. **Агент/Админ**: после входа посещает `/admin`, создаёт/редактирует объекты, запускает синхронизацию CIAN и массовое геокодирование, контролирует галереи.
4. **Все роли**: могут просматривать детальные страницы, делиться ссылками и использовать карту.

## 7. Расширение
- **CI/CD**: проект уже готов к Docker/CI настройкам (env, requirements, build scripts).
- **PostgreSQL**: смена `DATABASE_URL` и `pip install psycopg[binary]` (при необходимости) позволит мигрировать в прод.
- **OpenRouter**: можно заменить модель через `OPENROUTER_MODEL` или добавить fallback (обработчик ошибок уже предусмотрен).
- **Карты**: Yandex Map API key хранится в Vite env, можно добавить кластеры, маршруты, поиск по карте.

## 8. Краткий чек-лист запуска
1. `cp .env.example .env` → заполнить ключи.
2. **Backend**: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py runserver`.
3. **Frontend**: `cd frontend && npm install && npm run dev`.
4. В `.env`/`frontend/.env` указать OpenRouter/Yandex ключи для полноценных AI и геокодер функций.

Так реализован полный функционал Lev Estate — современного веб‑приложения для AI‑подбора недвижимости с картой, фильтрами, админ‑панелью и богатым UI.
