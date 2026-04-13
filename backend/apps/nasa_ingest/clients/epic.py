"""EPIC (Earth Polychromatic Imaging Camera) client. PLAN §2.2.5, §5.3."""
from django.conf import settings
from .base import NASAClient


class EPICClient(NASAClient):
    BASE = "https://epic.gsfc.nasa.gov/api"
    ARCHIVE = "https://epic.gsfc.nasa.gov/archive"

    def fetch_recent(self, collection: str = "natural") -> list[dict]:
        """Fetch the most recent set of Earth images."""
        return self.get(f"{self.BASE}/{collection}")

    def image_url(self, image_name: str, date_str: str, collection: str = "natural") -> str:
        """Build the full image URL from metadata. Date format: YYYY-MM-DD."""
        y, m, d = date_str.split("-")
        return f"{self.ARCHIVE}/{collection}/{y}/{m}/{d}/png/{image_name}.png"
