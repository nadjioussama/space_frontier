"""Run the APOD ingest synchronously — handy for first-boot and smoke tests."""
from django.core.management.base import BaseCommand
from apps.nasa_ingest.tasks import ingest_apod


class Command(BaseCommand):
    help = "Synchronously fetch today's APOD, persist, and generate mission."

    def handle(self, *args, **options) -> None:
        result = ingest_apod()
        self.stdout.write(self.style.SUCCESS(f"ingest_apod -> {result}"))
