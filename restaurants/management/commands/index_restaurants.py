import time

from django.core.management.base import BaseCommand

from restaurants import search


class Command(BaseCommand):
    help = 'Index all restaurants into OpenSearch (retries until the domain is ready)'

    def handle(self, *args, **opts):
        if not search.get_client():
            self.stdout.write('[search-index] OPENSEARCH_ENDPOINT not set, skipping')
            return
        for attempt in range(20):
            try:
                n = search.index_all()
                self.stdout.write(f'[search-index] indexed {n} restaurants')
                return
            except Exception as exc:
                self.stdout.write(f'[search-index] retry {attempt}: {exc}')
                time.sleep(30)