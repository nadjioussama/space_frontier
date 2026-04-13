"""NeoWs transformer. Converts raw feed into NEOObject + NEOApproach. PLAN §2.2.3."""
from __future__ import annotations

import logging
import math
from datetime import datetime

from ..models import NEOApproach, NEOObject

logger = logging.getLogger(__name__)

# Size comparison thresholds (meters)
_SIZE_LABELS = [
    (1, "basketball"),
    (5, "car"),
    (15, "school bus"),
    (50, "house"),
    (100, "football field"),
    (500, "cruise ship"),
    (1000, "skyscraper"),
    (5000, "small town"),
]


def _size_comparison(diameter_m: float) -> str:
    label = "pebble"
    for threshold, name in _SIZE_LABELS:
        if diameter_m >= threshold:
            label = name
    return label


def _threat_score(diameter_m: float, velocity_kmh: float, miss_km: float) -> int:
    """Compute a 0-100 threat score for gameplay. Not real science — tuned for fun."""
    if miss_km <= 0 or diameter_m <= 0:
        return 0
    # Bigger, faster, closer = higher score
    size_factor = min(math.log10(max(diameter_m, 1)) / 4, 1.0)       # 0-1
    speed_factor = min(velocity_kmh / 150000, 1.0)                    # 0-1
    closeness = max(1 - (miss_km / 7_500_000), 0)                    # 0-1 (7.5M km = ~50 lunar dist)
    raw = (size_factor * 0.3 + speed_factor * 0.2 + closeness * 0.5) * 100
    return min(int(raw), 100)


class NeoWsTransformer:
    def __init__(self, feed: dict) -> None:
        self.feed = feed

    def to_models(self) -> list[NEOObject]:
        results = []
        near_earth = self.feed.get("near_earth_objects", {})
        for date_str, neos in near_earth.items():
            for raw in neos:
                try:
                    obj = self._upsert_neo(raw)
                    self._upsert_approaches(obj, raw.get("close_approach_data", []))
                    results.append(obj)
                except Exception as exc:
                    logger.warning("Failed to ingest NEO %s: %s", raw.get("id"), exc)
        return results

    def _upsert_neo(self, raw: dict) -> NEOObject:
        diam = raw.get("estimated_diameter", {}).get("meters", {})
        obj, _ = NEOObject.objects.update_or_create(
            neo_id=str(raw["id"]),
            defaults=dict(
                source_api="neows",
                source_id=str(raw["id"]),
                raw_url=raw.get("nasa_jpl_url", ""),
                name=raw.get("name", f"NEO-{raw['id']}"),
                diameter_min_m=diam.get("estimated_diameter_min", 0),
                diameter_max_m=diam.get("estimated_diameter_max", 0),
                is_hazardous=raw.get("is_potentially_hazardous_asteroid", False),
            ),
        )
        return obj

    def _upsert_approaches(self, obj: NEOObject, approaches: list[dict]) -> None:
        avg_diam = (obj.diameter_min_m + obj.diameter_max_m) / 2
        for a in approaches:
            vel = float(a.get("relative_velocity", {}).get("kilometers_per_hour", 0))
            miss = float(a.get("miss_distance", {}).get("kilometers", 0))
            approach_dt = datetime.fromisoformat(
                a.get("close_approach_date_full", a.get("close_approach_date", "2000-01-01"))
                .replace(" ", "T")
            )
            NEOApproach.objects.update_or_create(
                neo=obj,
                approach_date=approach_dt,
                defaults=dict(
                    velocity_kmh=vel,
                    miss_distance_km=miss,
                    threat_score=_threat_score(avg_diam, vel, miss),
                    size_comparison=_size_comparison(avg_diam),
                ),
            )
