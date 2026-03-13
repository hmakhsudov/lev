# Docker local run

This project can be started on another PC with Docker only.

## What is included

- `backend` service: Django API served by Gunicorn
- `frontend` service: built Vue app served by Nginx
- `sqlite_data` volume: persists the SQLite database
- `django_static` volume: shares Django static files with Nginx

The frontend proxies `/api` and `/admin/` to Django, so you open only one URL in the browser.

## First run

1. Copy `.env.example` to `.env` ПРОСТО СОЗДАЙ .env файл рядом с env example
2. Fill in any keys you need, especially:
   - `DJANGO_SECRET_KEY`
   - `OPENAI_API_KEY`
   - `YANDEX_GEOCODER_API_KEY`
   - `VITE_YANDEX_MAPS_API_KEY` 
3. Start the stack:

```bash
docker compose up --build
```

Then open:

- Frontend: `http://localhost:8080`
- Backend API: `http://localhost:8000/api/`
- Django admin: `http://localhost:8080/admin/`
- Frontend admin page: `http://localhost:8080/admin`

## Useful commands

Create a Django superuser:

```bash
docker compose exec backend python manage.py createsuperuser
```

Stop the stack:

```bash
docker compose down
```

Stop and remove containers but keep data:

```bash
docker compose down
```

Stop and remove containers and volumes:

```bash
docker compose down -v
```

## Notes

- Migrations and `collectstatic` run automatically when the backend container starts.
- The default database is SQLite inside the `sqlite_data` Docker volume.
- `GUNICORN_WORKERS=1` is intentional because SQLite is safest with a single worker for local use.
- The frontend contains chat websocket client code, but this backend currently exposes only HTTP endpoints. Messaging still falls back to HTTP where implemented.
