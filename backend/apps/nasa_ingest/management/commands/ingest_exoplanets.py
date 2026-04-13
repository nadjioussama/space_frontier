"""Synchronous ingest for exoplanets — convenience wrapper for dev/testing."""
from django.core.management.base import BaseCommand
from apps.nasa_ingest.tasks import ingest_exoplanets


class Command(BaseCommand):
    help = "Synchronously ingest exoplanets data from NASA."

    def handle(self, *args, **options):
        result = ingest_exoplanets()
        self.stdout.write(self.style.SUCCESS(f"ingest_exoplanets -> {result}"))
