# release.sh
#!/bin/bash

# Run Django migrations
python manage.py migrate --noinput

# Run the initial data creation
python manage.py initd

# Create static files
python manage.py collectstatic --noinput --clear