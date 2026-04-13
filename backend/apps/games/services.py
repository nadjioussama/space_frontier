"""Business-logic entry points used by ingest tasks and views.

Keeps views + tasks thin: they orchestrate; services do the work.
Each `generate_*_mission(s)` follows the same contract:
  1. Ensure the destination Planet exists
  2. Create or update the Mission row
  3. Generate game artifacts (quiz, jigsaw)
  4. Return the mission(s) created
"""
from __future__ import annotations

import logging

from apps.nasa_ingest.models import (
    APODEntry, EPICImage, Exoplanet, MarsPhoto, NEOObject,
)
from .generators import jigsaw as jigsaw_gen
from .generators import quiz as quiz_gen
from .generators import neo_quiz, mars_quiz, epic_quiz, exoplanet_quiz
from .models import Mission, Planet

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Planet factories (lazy-create)
# --------------------------------------------------------------------------- #

def _get_planet(slug: str, name: str, description: str, unlocked: bool = True) -> Planet:
    planet, _ = Planet.objects.get_or_create(
        slug=slug,
        defaults=dict(name=name, description=description, is_unlocked=unlocked),
    )
    return planet


def _earth() -> Planet:
    return _get_planet("earth", "Earth",
                       "Your home planet. The daily NASA Picture and Earth observation missions live here.")


def _mars() -> Planet:
    return _get_planet("mars", "Mars",
                       "The Red Planet. Drive the rover, explore the terrain, classify rocks.")


def _asteroid_belt() -> Planet:
    return _get_planet("asteroid-belt", "Asteroid Belt",
                       "Planetary Defense HQ. Track near-Earth objects, assess threats.")


def _exoplanets() -> Planet:
    return _get_planet("exoplanets", "Exoplanets",
                       "Thousands of alien worlds. Rate their habitability, find the Goldilocks zone.")


# --------------------------------------------------------------------------- #
# APOD mission (Phase 1)
# --------------------------------------------------------------------------- #

def generate_apod_mission(entry: APODEntry) -> Mission:
    slug = f"apod-{entry.date.isoformat()}"
    mission, _ = Mission.objects.update_or_create(
        slug=slug,
        defaults=dict(
            title=f"Mission: {entry.title}"[:255],
            planet=_earth(),
            mission_type="apod_daily",
            apod=entry,
            xp_reward=50,
            difficulty=3,
            is_published=True,
        ),
    )
    image_for_puzzle = entry.proxied_url or entry.image_url
    if entry.media_type == "image" and image_for_puzzle:
        jigsaw_gen.generate(mission, image_for_puzzle, piece_count=12)
    quiz_gen.generate(mission, entry, n=3)
    return mission


# --------------------------------------------------------------------------- #
# Mars Rover missions (Phase 4)
# --------------------------------------------------------------------------- #

def generate_mars_missions(photos: list[MarsPhoto]) -> list[Mission]:
    if not photos:
        return []
    planet = _mars()
    missions = []
    # Group by sol — one mission per sol batch
    sols: dict[int, list[MarsPhoto]] = {}
    for p in photos:
        sols.setdefault(p.sol, []).append(p)

    for sol, batch in list(sols.items())[:3]:  # cap at 3 missions per ingest
        rover = batch[0].rover
        slug = f"mars-{rover}-sol-{sol}"
        representative = batch[0]
        mission, _ = Mission.objects.update_or_create(
            slug=slug,
            defaults=dict(
                title=f"Mars {rover.title()} — Sol {sol}",
                planet=planet,
                mission_type="mars_rover",
                xp_reward=60,
                difficulty=4,
                is_published=True,
            ),
        )
        img = representative.proxied_url or representative.image_url
        if img:
            jigsaw_gen.generate(mission, img, piece_count=12)
        mars_quiz.generate(mission, batch, n=3)
        missions.append(mission)
    return missions


# --------------------------------------------------------------------------- #
# NEO / Planetary Defense missions (Phase 4)
# --------------------------------------------------------------------------- #

def generate_neo_missions(neos: list[NEOObject]) -> list[Mission]:
    if not neos:
        return []
    planet = _asteroid_belt()
    missions = []
    # One mission per day covering all approaching NEOs
    from datetime import date
    slug = f"neo-{date.today().isoformat()}"
    mission, _ = Mission.objects.update_or_create(
        slug=slug,
        defaults=dict(
            title=f"Planetary Defense — {date.today().strftime('%b %d')}",
            planet=planet,
            mission_type="neo_defense",
            xp_reward=70,
            difficulty=5,
            is_published=True,
        ),
    )
    neo_quiz.generate(mission, neos, n=4)
    missions.append(mission)
    return missions


# --------------------------------------------------------------------------- #
# EPIC Earth observation missions (Phase 4)
# --------------------------------------------------------------------------- #

def generate_epic_missions(images: list[EPICImage]) -> list[Mission]:
    if not images:
        return []
    planet = _earth()
    missions = []
    latest = images[0]
    slug = f"epic-{latest.date_taken.date().isoformat()}"
    mission, _ = Mission.objects.update_or_create(
        slug=slug,
        defaults=dict(
            title=f"Earth Observer — {latest.date_taken.strftime('%b %d')}",
            planet=planet,
            mission_type="epic_observer",
            xp_reward=50,
            difficulty=3,
            is_published=True,
        ),
    )
    img = latest.proxied_url or latest.image_url
    if img:
        jigsaw_gen.generate(mission, img, piece_count=12)
    epic_quiz.generate(mission, images, n=3)
    missions.append(mission)
    return missions


# --------------------------------------------------------------------------- #
# Exoplanet missions (Phase 4)
# --------------------------------------------------------------------------- #

def generate_exoplanet_missions(planets_list: list[Exoplanet]) -> list[Mission]:
    if not planets_list:
        return []
    planet = _exoplanets()
    missions = []
    # Top 5 most habitable from the latest batch
    top = sorted(planets_list, key=lambda x: x.habitability_score, reverse=True)[:5]
    for exo in top:
        slug = f"exo-{exo.name.lower().replace(' ', '-')}"[:50]
        mission, _ = Mission.objects.update_or_create(
            slug=slug,
            defaults=dict(
                title=f"Explore {exo.name}",
                planet=planet,
                mission_type="exoplanet_explorer",
                xp_reward=55,
                difficulty=4,
                is_published=True,
            ),
        )
        exoplanet_quiz.generate(mission, exo, n=3)
        missions.append(mission)
    return missions


# --------------------------------------------------------------------------- #
# Cross-API missions (Phase 5, PLAN §2.3)
# --------------------------------------------------------------------------- #

CROSS_API_TEMPLATES = [
    {
        "slug": "cross-is-there-life",
        "title": "Is There Life Out There?",
        "description": "Combine exoplanet habitability, Mars water evidence, and solar activity data.",
        "sources": ["exoplanet_explorer", "mars_rover", "apod_daily"],
        "xp_reward": 100,
        "difficulty": 6,
    },
    {
        "slug": "cross-defend-the-planet",
        "title": "Defend the Planet",
        "description": "Assess asteroid threats and protect Earth using NEO tracking data.",
        "sources": ["neo_defense", "epic_observer"],
        "xp_reward": 90,
        "difficulty": 5,
    },
    {
        "slug": "cross-day-in-space",
        "title": "A Day in Space",
        "description": "Morning APOD ritual, Earth observation, and Mars weather check.",
        "sources": ["apod_daily", "epic_observer", "mars_rover"],
        "xp_reward": 80,
        "difficulty": 3,
    },
    {
        "slug": "cross-scale-of-everything",
        "title": "Scale of Everything",
        "description": "Sort objects from rover wheels to galaxies — understand cosmic scale.",
        "sources": ["mars_rover", "neo_defense", "exoplanet_explorer", "apod_daily"],
        "xp_reward": 85,
        "difficulty": 4,
    },
]


def generate_cross_api_missions() -> list[Mission]:
    """Generate cross-API missions from templates. PLAN §2.3.

    These missions pull quiz content from multiple API sources. They live on
    the Earth planet node as special "combined" missions.
    """
    from .generators import cross_api_quiz
    planet = _earth()
    missions = []

    for tmpl in CROSS_API_TEMPLATES:
        mission, _ = Mission.objects.update_or_create(
            slug=tmpl["slug"],
            defaults=dict(
                title=tmpl["title"],
                planet=planet,
                mission_type="cross_api",
                xp_reward=tmpl["xp_reward"],
                difficulty=tmpl["difficulty"],
                is_published=True,
                is_cross_api=True,
                cross_api_sources=tmpl["sources"],
            ),
        )
        cross_api_quiz.generate(mission, tmpl["slug"])
        missions.append(mission)

    return missions
