"""Quiz generator for Exoplanet missions. PLAN §2.2.6."""
from __future__ import annotations

from apps.nasa_ingest.models import Exoplanet
from ..models import Mission, Quiz


def generate(mission: Mission, exo: Exoplanet, n: int = 3) -> list[Quiz]:
    Quiz.objects.filter(mission=mission, auto_generated=True).delete()
    created = []

    # Q1: Habitability
    if exo.equilibrium_temp_k:
        temp_c = exo.equilibrium_temp_k - 273
        created.append(Quiz.objects.create(
            mission=mission, auto_generated=True, difficulty=3,
            question=f"Planet {exo.name} has an equilibrium temperature of {exo.equilibrium_temp_k:.0f} K. Is that in the range where liquid water could exist?",
            correct_answer="Yes" if 200 <= exo.equilibrium_temp_k <= 320 else "No",
            distractors=[
                "No" if 200 <= exo.equilibrium_temp_k <= 320 else "Yes",
                "Only underground",
                "Only as steam",
            ],
            explanation=f"{exo.equilibrium_temp_k:.0f} K is about {temp_c:.0f} C. Liquid water needs roughly 200-320 K.",
        ))

    # Q2: Size comparison
    if exo.radius_earth:
        if exo.radius_earth < 1.5:
            category = "rocky (Earth-like)"
        elif exo.radius_earth < 4:
            category = "sub-Neptune"
        else:
            category = "gas giant"
        created.append(Quiz.objects.create(
            mission=mission, auto_generated=True, difficulty=2,
            question=f"{exo.name} has a radius of {exo.radius_earth:.1f} Earth radii. What type of planet is it likely to be?",
            correct_answer=category,
            distractors=[c for c in ["rocky (Earth-like)", "sub-Neptune", "gas giant"] if c != category],
            explanation=f"At {exo.radius_earth:.1f}x Earth's radius, this planet is classified as {category}.",
        ))

    # Q3: Discovery
    if exo.discovery_year:
        created.append(Quiz.objects.create(
            mission=mission, auto_generated=True, difficulty=2,
            question=f"In what year was exoplanet {exo.name} discovered?",
            correct_answer=str(exo.discovery_year),
            distractors=[str(exo.discovery_year + d) for d in [-2, 1, 3]],
            explanation=f"{exo.name} was confirmed in {exo.discovery_year}, orbiting the star {exo.host_star}.",
        ))

    # Q4: General fallback
    if len(created) < n:
        created.append(Quiz.objects.create(
            mission=mission, auto_generated=True, difficulty=1,
            question="How do scientists most commonly discover exoplanets?",
            correct_answer="The transit method — watching for dips in starlight",
            distractors=[
                "Taking direct photographs",
                "Listening for radio signals",
                "Sending space probes to visit",
            ],
            explanation="The transit method detects tiny dips in a star's brightness as a planet passes in front of it. NASA's Kepler and TESS missions used this technique.",
        ))

    return created[:n]
