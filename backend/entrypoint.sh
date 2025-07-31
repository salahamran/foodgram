#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."

until nc -z "$DB_HOST" "$DB_PORT"; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL started"

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

cp -r /app/collected_static/. /staticfiles/
cp -r /app/collected_static/. /backend_static/static/

exec "$@"
