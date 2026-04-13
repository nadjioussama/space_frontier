"""Synchronous ingest for neows — convenience wrapper for dev/testing."""
from django.core.management.base import BaseCommand
from apps.nasa_ingest.tasks import ingest_neows


class Command(BaseCommand):
    help = "Synchronously ingest neows data from NASA."

    def handle(self, *args, **options):
        result = ingest_neows()
        self.stdout.write(self.style.SUCCESS(f"ingest_neows -> {result}"))
