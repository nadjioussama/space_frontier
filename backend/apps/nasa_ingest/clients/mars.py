"""Mars Rover Photos API client. PLAN §2.2.2, §5.3."""
from django.conf import settings
from .base import NASAClient


class MarsRoverClient(NASAClient):
    ENDPOINT = "/mars-photos/api/v1/rovers"

    def fetch_latest(self, rover: str = "perseverance", camera: str | None = None) -> list[dict]:
        """Fetch the most recent sol's photos for a rover."""
        params = {}
        if camera:
            params["camera"] = camera
        data = self.get(
            f"{settings.NASA_API_BASE}{self.ENDPOINT}/{rover}/latest_photos",
            params,
        )
        return data.get("latest_photos", [])

    def fetch_sol(self, rover: str, sol: int, camera: str | None = None) -> list[dict]:
        params = {"sol": sol}
        if camera:
            params["camera"] = camera
        data = self.get(
            f"{settings.NASA_API_BASE}{self.ENDPOINT}/{rover}/photos",
            params,
        )
        return data.get("photos", [])
