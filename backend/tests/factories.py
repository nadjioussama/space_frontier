"""Lightweight model factories shared across the test suite.

Kept dependency-free (no factory_boy) to match the project's minimal
requirements set.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

from apps.games.models import Mission, Planet
from apps.nasa_ingest.models import (
    APODEntry, EPICImage, Exoplanet, MarsPhoto, NEOApproach, NEOObject,
)
from apps.users.models import ParentAccount, Player


# --------------------------------------------------------------------------- #
# NASA content
# --------------------------------------------------------------------------- #

def make_apod(d: date | None = None, **over) -> APODEntry:
    d = d or date(2026, 4, 13)
    defaults = dict(
        source_api="apod", source_id=d.isoformat(), date=d,
        title="Test Nebula",
        explanation="A beautiful cloud of gas and dust photographed by Hubble.",
        media_type="image",
        image_url="https://example.com/test.jpg",
        proxied_url="/media/apod/test.jpg",
        is_published=True,
    )
    defaults.update(over)
    return APODEntry.objects.create(**defaults)


def make_mars_photo(nasa_id: int = 1, **over) -> MarsPhoto:
    defaults = dict(
        source_api="mars_rover", source_id=str(nasa_id),
        rover="perseverance", camera="navcam", sol=1000,
        earth_date=date(2026, 4, 1),
        image_url="https://example.com/mars.jpg",
        proxied_url="/media/mars/x.jpg",
        nasa_photo_id=nasa_id,
    )
    defaults.update(over)
    return MarsPhoto.objects.create(**defaults)


def make_neo(neo_id: str = "1", hazardous: bool = False, diameter: float = 30.0,
             with_approach: bool = True, **over) -> NEOObject:
    defaults = dict(
        source_api="neows", source_id=neo_id, neo_id=neo_id,
        name=f"({neo_id}) Test Rock",
        diameter_min_m=diameter * 0.8, diameter_max_m=diameter * 1.2,
        is_hazardous=hazardous,
    )
    defaults.update(over)
    obj = NEOObject.objects.create(**defaults)
    if with_approach:
        NEOApproach.objects.create(
            neo=obj,
            approach_date=datetime(2026, 4, 14, tzinfo=timezone.utc),
            velocity_kmh=50000.0, miss_distance_km=1_000_000.0,
            threat_score=42, size_comparison="school bus",
        )
    return obj


def make_epic(identifier: str = "epic_1", **over) -> EPICImage:
    defaults = dict(
        source_api="epic", source_id=identifier, identifier=identifier,
        image_name="epic_test", caption="Earth full disc",
        image_url="https://example.com/epic.png",
        proxied_url="/media/epic/x.png",
        date_taken=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc),
        centroid_lat=10.0, centroid_lon=-45.0,
    )
    defaults.update(over)
    return EPICImage.objects.create(**defaults)


def make_exoplanet(name: str = "Kepler-442 b", **over) -> Exoplanet:
    defaults = dict(
        source_api="exoplanet_archive", source_id=name, name=name,
        host_star="Kepler-442", mass_earth=2.3, radius_earth=1.34,
        orbital_period_days=112.3, equilibrium_temp_k=233.0,
        distance_ly=1206.0, discovery_year=2015,
        habitability_score=80,
    )
    defaults.update(over)
    return Exoplanet.objects.create(**defaults)


# --------------------------------------------------------------------------- #
# Game world
# --------------------------------------------------------------------------- #

def make_planet(slug: str = "earth", **over) -> Planet:
    defaults = dict(slug=slug, name=slug.title(), description="", is_unlocked=True)
    defaults.update(over)
    obj, _ = Planet.objects.get_or_create(slug=slug, defaults=defaults)
    return obj


def make_mission(slug: str = "test-mission", **over) -> Mission:
    defaults = dict(
        slug=slug, title="Test Mission",
        planet=over.pop("planet", None) or make_planet(),
        mission_type="apod_daily", xp_reward=50, difficulty=3,
        is_published=True,
    )
    defaults.update(over)
    return Mission.objects.create(**defaults)


# --------------------------------------------------------------------------- #
# Users
# --------------------------------------------------------------------------- #

def make_player(username: str = "kid1", **over) -> Player:
    defaults = dict(age_group="9-11", is_under_13=True)
    defaults.update(over)
    return Player.objects.create_user(username=username, password="pw", **defaults)


def make_parent(email: str = "parent@example.com", verified: bool = True) -> ParentAccount:
    p = ParentAccount.objects.create(email=email, full_name="Pat Parent")
    if verified:
        p.verification_status = "verified"
        p.save(update_fields=["verification_status"])
    return p
