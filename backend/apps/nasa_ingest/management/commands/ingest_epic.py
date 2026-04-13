"""Synchronous ingest for epic — convenience wrapper for dev/testing."""
from django.core.management.base import BaseCommand
from apps.nasa_ingest.tasks import ingest_epic


class Command(BaseCommand):
    help = "Synchronously ingest epic data from NASA."

    def handle(self, *args, **options):
        result = ingest_epic()
        self.stdout.write(self.style.SUCCESS(f"ingest_epic -> {result}"))
