# Local Docker Run

This Docker setup is intentionally simple and local-first:

- `backend` runs Django with `runserver`
- `frontend` runs Vite dev server

That avoids Nginx and Gunicorn issues and is the safest option for running the full project on another PC locally.

## Start

1. Copy `.env.example` to `.env`
2. Run:

```bash
docker compose up --build
```

Open:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api/`

## Full reset

If Docker cached old broken containers or images:

```bash
docker compose down -v --remove-orphans --rmi local
docker compose up --build
```

## Notes

- Backend auto-runs migrations on startup.
- SQLite is stored in the `sqlite_data` volume.
- Frontend source is mounted into the container for predictable local startup.
- Node modules are stored in the `frontend_node_modules` volume.
