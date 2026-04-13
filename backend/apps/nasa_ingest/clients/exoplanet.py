"""NASA Exoplanet Archive client. PLAN §2.2.6, §5.3.

The Exoplanet Archive uses a TAP (Table Access Protocol) query interface,
not the api.nasa.gov gateway. It has its own rate limits and doesn't need
the NASA API key.
"""
from .base import NASAClient


class ExoplanetClient(NASAClient):
    BASE = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

    def fetch_confirmed(self, limit: int = 100) -> list[dict]:
        """Fetch confirmed exoplanets with key habitability fields."""
        query = (
            "SELECT pl_name, hostname, pl_bmasse, pl_rade, pl_orbper, "
            "pl_eqt, disc_year, sy_dist "
            "FROM pscomppars "
            "WHERE default_flag = 1 "
            f"ORDER BY disc_year DESC "
            f"LIMIT {limit}"
        )
        # TAP endpoint returns JSON when format=json
        import requests
        resp = requests.get(self.BASE, params={
            "query": query,
            "format": "json",
        }, timeout=self.TIMEOUT_SECONDS)
        resp.raise_for_status()
        return resp.json()
