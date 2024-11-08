# release.sh
#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Running initial setup..."
python manage.py initd

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

exec "$@"
