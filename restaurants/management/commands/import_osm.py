import json
import urllib.parse
import urllib.request

from django.core.management.base import BaseCommand
from restaurants.models import Restaurant

OVERPASS_URL = 'https://overpass-api.de/api/interpreter'


class Command(BaseCommand):
    help = 'Import restaurants from OpenStreetMap around a point'

    def add_arguments(self, parser):
        parser.add_argument('--lat', type=float, default=10.2333)
        parser.add_argument('--lng', type=float, default=76.2000)
        parser.add_argument('--radius', type=int, default=15000, help='metres')
        parser.add_argument('--city', type=str, default='Kodungallur')

    def handle(self, *args, **opts):
        query = f"""
        [out:json][timeout:60];
        nwr["amenity"="restaurant"](around:{opts['radius']},{opts['lat']},{opts['lng']});
        out center tags;
        """
        data = urllib.parse.urlencode({'data': query}).encode()
        req = urllib.request.Request(
            OVERPASS_URL, data=data,
            headers={'User-Agent': 'DineWise-student-project/1.0'}
        )
        with urllib.request.urlopen(req, timeout=90) as resp:
            elements = json.load(resp)['elements']

        created = skipped = 0
        for el in elements:
            tags = el.get('tags', {})
            name = tags.get('name')
            if not name:
                skipped += 1
                continue

            center = el.get('center', {})
            lat = el.get('lat', center.get('lat'))
            lon = el.get('lon', center.get('lon'))
            city = tags.get('addr:city') or tags.get('addr:suburb') or opts['city']

            if Restaurant.objects.filter(name=name[:200], city=city[:200]).exists():
                skipped += 1
                continue

            diet = tags.get('diet:vegetarian')
            food_type = (Restaurant.VEG if diet == 'only'
                         else Restaurant.NON_VEG if diet == 'no'
                         else Restaurant.BOTH)

            address_parts = [tags.get('addr:housenumber'), tags.get('addr:street'),
                             tags.get('addr:suburb')]
            address = ', '.join(p for p in address_parts if p) or f'{name}, {city}'
            cuisine = (tags.get('cuisine', '').replace(';', ', ').replace('_', ' ').title()
                       or 'Not specified')

            Restaurant.objects.create(
                name=name[:200],
                address=address[:200],
                city=city[:200],
                cuisine=cuisine[:200],
                food_type=food_type,
                has_parking=False,
                description=tags.get('description', ''),
                latitude=lat,
                longitude=lon,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created}, skipped {skipped}'))