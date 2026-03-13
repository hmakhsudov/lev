#!/bin/sh
set -e

mkdir -p /app/backend/data /app/backend/staticfiles

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-1}" \
  --timeout "${GUNICORN_TIMEOUT:-120}" \
  django_project.wsgi:application
