"""Synchronous ingest for mars — convenience wrapper for dev/testing."""
from django.core.management.base import BaseCommand
from apps.nasa_ingest.tasks import ingest_mars


class Command(BaseCommand):
    help = "Synchronously ingest mars data from NASA."

    def handle(self, *args, **options):
        result = ingest_mars()
        self.stdout.write(self.style.SUCCESS(f"ingest_mars -> {result}"))
