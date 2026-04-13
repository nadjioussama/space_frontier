"""NeoWs (Near Earth Object Web Service) client. PLAN §2.2.3, §5.3."""
from datetime import date, timedelta
from django.conf import settings
from .base import NASAClient


class NeoWsClient(NASAClient):
    ENDPOINT = "/neo/rest/v1/feed"

    def fetch_week(self, start: date | None = None) -> dict:
        """Fetch NEOs for a 7-day window (API limit). Returns the full feed dict."""
        start = start or date.today()
        end = start + timedelta(days=7)
        return self.get(f"{settings.NASA_API_BASE}{self.ENDPOINT}", {
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        })

    def fetch_today(self) -> dict:
        today = date.today()
        return self.get(f"{settings.NASA_API_BASE}{self.ENDPOINT}", {
            "start_date": today.isoformat(),
            "end_date": today.isoformat(),
        })
