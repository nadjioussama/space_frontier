"""APOD client. Trivial wrapper — the base class does all the work."""
from django.conf import settings
from .base import NASAClient


class APODClient(NASAClient):
    ENDPOINT = "/planetary/apod"

    def fetch_today(self) -> dict:
        return self.get(f"{settings.NASA_API_BASE}{self.ENDPOINT}")

    def fetch_date(self, iso_date: str) -> dict:
        return self.get(f"{settings.NASA_API_BASE}{self.ENDPOINT}", {"date": iso_date})
