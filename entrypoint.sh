# release.sh
#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating initial data..."
python manage.py initd

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

gunicorn --bind :8000 --workers 2 --worker-class uvicorn.workers.UvicornWorker ecommerce_store.asgi
exec "$@"
