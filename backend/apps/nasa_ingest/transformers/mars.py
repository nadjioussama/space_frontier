"""Mars Rover Photos transformer. PLAN §2.2.2."""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path

import requests
from django.conf import settings

from ..models import MarsPhoto

logger = logging.getLogger(__name__)


class MarsPhotoTransformer:
    def __init__(self, photos: list[dict]) -> None:
        self.photos = photos

    def _proxy_image(self, url: str) -> str:
        h = hashlib.sha256(url.encode()).hexdigest()[:16]
        dest_dir = Path(settings.MEDIA_ROOT) / "mars"
        dest_dir.mkdir(parents=True, exist_ok=True)
        ext = url.rsplit(".", 1)[-1].split("?")[0].lower() or "jpg"
        dest = dest_dir / f"{h}.{ext}"
        if not dest.exists():
            try:
                r = requests.get(url, timeout=30, stream=True)
                r.raise_for_status()
                with dest.open("wb") as f:
                    for chunk in r.iter_content(1024 * 64):
                        f.write(chunk)
            except Exception as exc:
                logger.warning("Mars image download failed: %s", exc)
                return url
        return f"{settings.MEDIA_URL}mars/{dest.name}"

    def to_models(self, limit: int = 20) -> list[MarsPhoto]:
        results = []
        for raw in self.photos[:limit]:
            rover_data = raw.get("rover", {})
            cam_data = raw.get("camera", {})
            img_url = raw.get("img_src", "")
            nasa_id = raw.get("id", 0)

            photo, created = MarsPhoto.objects.update_or_create(
                nasa_photo_id=nasa_id,
                defaults=dict(
                    source_api="mars_rover",
                    source_id=str(nasa_id),
                    raw_url=img_url,
                    rover=rover_data.get("name", "unknown").lower(),
                    camera=cam_data.get("short_name", "unknown").lower(),
                    sol=raw.get("sol", 0),
                    earth_date=raw.get("earth_date", "2000-01-01"),
                    image_url=img_url,
                    proxied_url=self._proxy_image(img_url) if img_url else "",
                ),
            )
            results.append(photo)
        return results
