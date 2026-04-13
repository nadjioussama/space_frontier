"""Seed the Knowledge Constellation skill tree with initial data. PLAN §3.4."""
from django.core.management.base import BaseCommand
from apps.progress.models import Constellation, SkillStar


CONSTELLATIONS = [
    {
        "slug": "solar-system",
        "name": "Solar System",
        "topic": "astronomy",
        "description": "Planets, moons, and our cosmic neighborhood.",
        "icon": "sun",
        "stars": [
            {"slug": "inner-planets", "name": "Inner Planets", "x": 20, "y": 50,
             "mission_types": ["apod_daily"], "description": "Mercury, Venus, Earth, and Mars."},
            {"slug": "outer-planets", "name": "Outer Planets", "x": 50, "y": 30,
             "mission_types": ["apod_daily"], "description": "Jupiter, Saturn, Uranus, Neptune.",
             "prereqs": ["inner-planets"]},
            {"slug": "dwarf-planets", "name": "Dwarf Planets", "x": 80, "y": 50,
             "mission_types": ["apod_daily"], "description": "Pluto, Eris, Ceres, and more.",
             "prereqs": ["outer-planets"]},
            {"slug": "solar-wind", "name": "Solar Wind", "x": 50, "y": 70,
             "mission_types": ["apod_daily"], "description": "The Sun's constant stream of particles."},
        ],
    },
    {
        "slug": "mars-exploration",
        "name": "Mars Exploration",
        "topic": "geology",
        "description": "Rovers, terrain, and the search for water.",
        "icon": "rover",
        "stars": [
            {"slug": "mars-rovers", "name": "Mars Rovers", "x": 30, "y": 40,
             "mission_types": ["mars_rover"], "description": "Curiosity, Perseverance, Opportunity."},
            {"slug": "mars-geology", "name": "Martian Geology", "x": 60, "y": 30,
             "mission_types": ["mars_rover"], "description": "Rocks, craters, and volcanos.",
             "prereqs": ["mars-rovers"]},
            {"slug": "mars-water", "name": "Water on Mars", "x": 70, "y": 60,
             "mission_types": ["mars_rover"], "description": "Evidence of ancient water.",
             "prereqs": ["mars-geology"]},
            {"slug": "mars-atmosphere", "name": "Mars Atmosphere", "x": 40, "y": 70,
             "mission_types": ["mars_rover"], "description": "Thin CO2 atmosphere, dust storms."},
        ],
    },
    {
        "slug": "planetary-defense",
        "name": "Planetary Defense",
        "topic": "planetary_defense",
        "description": "Tracking asteroids and protecting Earth.",
        "icon": "shield",
        "stars": [
            {"slug": "what-is-neo", "name": "Near-Earth Objects", "x": 25, "y": 45,
             "mission_types": ["neo_defense"], "description": "Asteroids and comets near Earth's orbit."},
            {"slug": "tracking-neos", "name": "Tracking NEOs", "x": 55, "y": 30,
             "mission_types": ["neo_defense"], "description": "How scientists detect and track threats.",
             "prereqs": ["what-is-neo"]},
            {"slug": "deflection", "name": "Deflection Methods", "x": 75, "y": 55,
             "mission_types": ["neo_defense", "cross_api"], "description": "DART mission and kinetic impactors.",
             "prereqs": ["tracking-neos"]},
        ],
    },
    {
        "slug": "earth-observation",
        "name": "Earth Observation",
        "topic": "earth_science",
        "description": "Watching our home from space.",
        "icon": "earth",
        "stars": [
            {"slug": "epic-camera", "name": "EPIC Camera", "x": 30, "y": 40,
             "mission_types": ["epic_observer"], "description": "Earth Polychromatic Imaging Camera at L1."},
            {"slug": "lagrange-points", "name": "Lagrange Points", "x": 60, "y": 30,
             "mission_types": ["epic_observer"], "description": "Gravitational balance points in space.",
             "prereqs": ["epic-camera"]},
            {"slug": "earth-atmosphere", "name": "Earth's Atmosphere", "x": 70, "y": 60,
             "mission_types": ["epic_observer"], "description": "Layers of air that protect life.",
             "prereqs": ["epic-camera"]},
        ],
    },
    {
        "slug": "exoplanet-science",
        "name": "Exoplanet Science",
        "topic": "exoplanets",
        "description": "Thousands of worlds beyond our Sun.",
        "icon": "planet",
        "stars": [
            {"slug": "transit-method", "name": "Transit Method", "x": 25, "y": 45,
             "mission_types": ["exoplanet_explorer"], "description": "Detecting dips in starlight."},
            {"slug": "habitable-zone", "name": "Habitable Zone", "x": 55, "y": 30,
             "mission_types": ["exoplanet_explorer"], "description": "The Goldilocks zone for liquid water.",
             "prereqs": ["transit-method"]},
            {"slug": "planet-types", "name": "Planet Types", "x": 75, "y": 55,
             "mission_types": ["exoplanet_explorer"], "description": "Rocky, sub-Neptune, gas giant.",
             "prereqs": ["transit-method"]},
            {"slug": "biosignatures", "name": "Biosignatures", "x": 50, "y": 75,
             "mission_types": ["exoplanet_explorer", "cross_api"],
             "description": "Chemical signs of possible life.",
             "prereqs": ["habitable-zone", "planet-types"]},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed Knowledge Constellation skill tree with initial data."

    def handle(self, *args, **options):
        all_stars = {}  # slug -> SkillStar instance
        for i, cdata in enumerate(CONSTELLATIONS):
            constellation, created = Constellation.objects.update_or_create(
                slug=cdata["slug"],
                defaults={
                    "name": cdata["name"],
                    "topic": cdata["topic"],
                    "description": cdata["description"],
                    "icon": cdata["icon"],
                    "display_order": i,
                },
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} constellation: {constellation.name}")

            for sdata in cdata["stars"]:
                star, created = SkillStar.objects.update_or_create(
                    slug=sdata["slug"],
                    defaults={
                        "constellation": constellation,
                        "name": sdata["name"],
                        "description": sdata.get("description", ""),
                        "mission_types": sdata.get("mission_types", []),
                        "xp_value": 25,
                        "display_x": sdata["x"],
                        "display_y": sdata["y"],
                    },
                )
                all_stars[sdata["slug"]] = star

        # Wire up prerequisites (second pass, after all stars exist)
        for cdata in CONSTELLATIONS:
            for sdata in cdata["stars"]:
                if "prereqs" in sdata:
                    star = all_stars[sdata["slug"]]
                    prereq_stars = [all_stars[p] for p in sdata["prereqs"] if p in all_stars]
                    star.prerequisites.set(prereq_stars)

        total = SkillStar.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Done. {total} stars across {len(CONSTELLATIONS)} constellations."))
