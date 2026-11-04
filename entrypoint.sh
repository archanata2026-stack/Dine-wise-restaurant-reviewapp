#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py shell -c "import sys; from restaurants.models import Restaurant; sys.exit(0 if Restaurant.objects.exists() else 1)" || python manage.py loaddata restaurants.json
python manage.py createsuperuser --noinput || true
exec gunicorn restaurant_review.wsgi:application --bind 0.0.0.0:8000 --workers 2