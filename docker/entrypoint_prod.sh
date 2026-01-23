#!/bin/sh
set -e

echo "Waiting for database..."

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER"; do
  sleep 1
done

echo "Database is ready"

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120