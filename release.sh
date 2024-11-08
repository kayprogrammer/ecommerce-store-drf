# release.sh
#!/bin/sh

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating initial data..."
python manage.py initd

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear
