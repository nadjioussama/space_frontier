"""Raw APOD JSON -> APODEntry. Also downloads the image to /media/ for local serving.

Production replaces local storage with S3 + content-addressed variants (PLAN §6.5).
"""
from __future__ import annotations

import hashlib
import logging
from datetime import date as date_cls
from pathlib import Path

import requests
from django.conf import settings

from ..models import APODEntry

logger = logging.getLogger(__name__)


class APODTransformer:
    def __init__(self, raw: dict) -> None:
        self.raw = raw

    def _download(self, url: str) -> str:
        """Save the image under MEDIA_ROOT/apod/<hash>.<ext>; return the relative URL path."""
        h = hashlib.sha256(url.encode()).hexdigest()[:16]
        ext = url.rsplit(".", 1)[-1].split("?")[0].lower() or "jpg"
        if ext not in {"jpg", "jpeg", "png", "webp", "gif"}:
            ext = "jpg"
        dest_dir = Path(settings.MEDIA_ROOT) / "apod"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{h}.{ext}"
        if not dest.exists():
            try:
                r = requests.get(url, timeout=30, stream=True)
                r.raise_for_status()
                with dest.open("wb") as f:
                    for chunk in r.iter_content(1024 * 64):
                        f.write(chunk)
            except Exception as exc:  # noqa: BLE001 — we prefer a missing proxy over a failed ingest
                logger.warning("APOD image download failed (%s); using upstream URL", exc)
                return url
        return f"{settings.MEDIA_URL}apod/{dest.name}"

    def to_model(self) -> APODEntry:
        iso = self.raw["date"]
        image_url = self.raw.get("url", "")
        proxied = ""
        if self.raw.get("media_type") == "image" and image_url:
            proxied = self._download(image_url)

        entry, _ = APODEntry.objects.update_or_create(
            date=date_cls.fromisoformat(iso),
            defaults=dict(
                source_api="apod",
                source_id=iso,
                raw_url=image_url,
                title=self.raw.get("title", ""),
                explanation=self.raw.get("explanation", ""),
                media_type=self.raw.get("media_type", "image"),
                image_url=image_url,
                hd_image_url=self.raw.get("hdurl", "") or "",
                proxied_url=proxied,
                copyright=self.raw.get("copyright", "") or "",
            ),
        )
        return entry
