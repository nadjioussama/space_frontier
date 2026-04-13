"""Quiz generator for NeoWs / Planetary Defense missions. PLAN §2.2.3."""
from __future__ import annotations

import random

from apps.nasa_ingest.models import NEOObject
from ..models import Mission, Quiz


def generate(mission: Mission, neos: list[NEOObject], n: int = 4) -> list[Quiz]:
    Quiz.objects.filter(mission=mission, auto_generated=True).delete()
    created = []

    if neos:
        # Q1: Count question
        hazardous = [n for n in neos if n.is_hazardous]
        created.append(Quiz.objects.create(
            mission=mission, auto_generated=True, difficulty=2,
            question=f"Of the {len(neos)} near-Earth objects detected today, how many are classified as potentially hazardous?",
            correct_answer=str(len(hazardous)),
            distractors=[str(len(hazardous) + d) for d in [1, -1, 3] if len(hazardous) + d >= 0][:3] or ["0", "1", "2"],
            explanation=f"NASA classifies {len(hazardous)} of today's {len(neos)} NEOs as potentially hazardous based on size and orbit.",
        ))

        # Q2: Size comparison
        neo = random.choice(neos)
        approaches = neo.approaches.order_by("approach_date").first()
        if approaches:
            created.append(Quiz.objects.create(
                mission=mission, auto_generated=True, difficulty=3,
                question=f"Asteroid {neo.name} is estimated to be {neo.diameter_min_m:.0f}-{neo.diameter_max_m:.0f} meters across. What is it roughly the size of?",
                correct_answer=approaches.size_comparison,
                distractors=[s for s in ["basketball", "school bus", "football field", "skyscraper", "car"]
                             if s != approaches.size_comparison][:3],
                explanation=f"At {(neo.diameter_min_m + neo.diameter_max_m) / 2:.0f}m average diameter, {neo.name} is about the size of a {approaches.size_comparison}.",
            ))

        # Q3: General NEO knowledge
        created.append(Quiz.objects.create(
            mission=mission, auto_generated=True, difficulty=2,
            question="What does 'NEO' stand for in space science?",
            correct_answer="Near-Earth Object",
            distractors=["New Earth Orbit", "Non-Essential Observation", "Nebula Explorer Operation"],
            explanation="NEO stands for Near-Earth Object — asteroids and comets that pass close to Earth's orbit.",
        ))

        # Q4: Threat assessment
        created.append(Quiz.objects.create(
            mission=mission, auto_generated=True, difficulty=4,
            question="What organization tracks potentially hazardous asteroids for NASA?",
            correct_answer="Center for Near Earth Object Studies (CNEOS)",
            distractors=["International Space Station crew", "SpaceX tracking team", "The Hubble Space Telescope"],
            explanation="CNEOS at JPL is NASA's center for computing orbits and assessing impact risks.",
        ))

    return created[:n]
