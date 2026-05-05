"""Exoplanet Archive transformer. PLAN §2.2.6."""
from __future__ import annotations

import logging

from ..models import Exoplanet

logger = logging.getLogger(__name__)


def _habitability_score(
    mass_earth: float | None,
    radius_earth: float | None,
    temp_k: float | None,
) -> int:
    """Simple habitability heuristic for gameplay. NOT real science.

    Criteria (each contributes 0-33 points):
    - Mass: 0.5-5 Earth masses preferred
    - Radius: 0.5-2 Earth radii preferred
    - Temperature: 200-320 K (liquid water possible)
    """
    score = 0
    if mass_earth is not None:
        if 0.5 <= mass_earth <= 5:
            score += 33
        elif 0.1 <= mass_earth <= 10:
            score += 15
    if radius_earth is not None:
        if 0.5 <= radius_earth <= 2:
            score += 33
        elif 0.3 <= radius_earth <= 3:
            score += 15
    if temp_k is not None:
        if 200 <= temp_k <= 320:
            score += 34
        elif 150 <= temp_k <= 400:
            score += 15
    return min(score, 100)


class ExoplanetTransformer:
    def __init__(self, records: list[dict]) -> None:
        self.records = records

    def to_models(self) -> list[Exoplanet]:
        results = []
        for raw in self.records:
            name = raw.get("pl_name")
            if not name:
                continue
            mass = raw.get("pl_bmasse")
            radius = raw.get("pl_rade")
            temp = raw.get("pl_eqt")
            dist_pc = raw.get("sy_dist")
            dist_ly = round(dist_pc * 3.26156, 2) if dist_pc else None

            entry, _ = Exoplanet.objects.update_or_create(
                name=name,
                defaults=dict(
                    source_api="exoplanet_archive",
                    source_id=name,
                    host_star=raw.get("hostname", ""),
                    mass_earth=mass,
                    radius_earth=radius,
                    orbital_period_days=raw.get("pl_orbper"),
                    equilibrium_temp_k=temp,
                    distance_ly=dist_ly,
                    discovery_year=raw.get("disc_year"),
                    habitability_score=_habitability_score(mass, radius, temp),
                ),
            )
            results.append(entry)
        return results
