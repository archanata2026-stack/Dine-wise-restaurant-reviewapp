#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py createsuperuser --noinput || true

has_restaurants() {
  python manage.py shell -c "import sys; from restaurants.models import Restaurant; sys.exit(0 if Restaurant.objects.exists() else 1)" >/dev/null 2>&1
}

if ! has_restaurants; then
  python manage.py loaddata restaurants.json || echo "loaddata failed - will try OpenStreetMap import"
fi

if ! has_restaurants; then
  (python manage.py import_osm --city Kodungallur || echo "OSM import failed") &
fi

exec gunicorn restaurant_review.wsgi:application --bind 0.0.0.0:8000 --workers 2