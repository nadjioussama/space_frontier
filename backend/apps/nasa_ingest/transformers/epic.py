"""EPIC transformer. PLAN §2.2.5."""
from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from pathlib import Path

import requests
from django.conf import settings

from ..clients.epic import EPICClient
from ..models import EPICImage

logger = logging.getLogger(__name__)


class EPICTransformer:
    def __init__(self, images: list[dict]) -> None:
        self.images = images
        self._client = EPICClient()

    def _proxy_image(self, url: str) -> str:
        h = hashlib.sha256(url.encode()).hexdigest()[:16]
        dest_dir = Path(settings.MEDIA_ROOT) / "epic"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{h}.png"
        if not dest.exists():
            try:
                r = requests.get(url, timeout=60, stream=True)
                r.raise_for_status()
                with dest.open("wb") as f:
                    for chunk in r.iter_content(1024 * 64):
                        f.write(chunk)
            except Exception as exc:
                logger.warning("EPIC image download failed: %s", exc)
                return url
        return f"{settings.MEDIA_URL}epic/{dest.name}"

    def to_models(self, limit: int = 12) -> list[EPICImage]:
        results = []
        for raw in self.images[:limit]:
            identifier = raw.get("identifier", "")
            image_name = raw.get("image", "")
            date_str = raw.get("date", "")[:10]
            dt = datetime.fromisoformat(raw.get("date", "2000-01-01T00:00:00"))
            full_url = self._client.image_url(image_name, date_str)

            coords = raw.get("centroid_coordinates", {})
            entry, _ = EPICImage.objects.update_or_create(
                identifier=identifier,
                defaults=dict(
                    source_api="epic",
                    source_id=identifier,
                    raw_url=full_url,
                    caption=raw.get("caption", ""),
                    image_name=image_name,
                    image_url=full_url,
                    proxied_url=self._proxy_image(full_url),
                    date_taken=dt,
                    centroid_lat=coords.get("lat"),
                    centroid_lon=coords.get("lon"),
                ),
            )
            results.append(entry)
        return results
