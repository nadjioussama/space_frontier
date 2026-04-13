"""Quiz generator for EPIC Earth observation missions. PLAN §2.2.5."""
from __future__ import annotations

import random

from apps.nasa_ingest.models import EPICImage
from ..models import Mission, Quiz


def generate(mission: Mission, images: list[EPICImage], n: int = 3) -> list[Quiz]:
    Quiz.objects.filter(mission=mission, auto_generated=True).delete()
    created = []

    # Q1: Where EPIC lives
    created.append(Quiz.objects.create(
        mission=mission, auto_generated=True, difficulty=3,
        question="Where is the DSCOVR satellite (which carries the EPIC camera) located?",
        correct_answer="Lagrange Point 1 (L1), about 1.5 million km from Earth",
        distractors=[
            "In low Earth orbit, 400 km up",
            "On the surface of the Moon",
            "Orbiting Mars",
        ],
        explanation="DSCOVR sits at the L1 Lagrange point — a gravitational balance point between Earth and the Sun, about 1.5 million km away.",
    ))

    # Q2: Why full disc
    created.append(Quiz.objects.create(
        mission=mission, auto_generated=True, difficulty=2,
        question="Why does the EPIC camera always see the full disc of Earth?",
        correct_answer="It is between Earth and the Sun, always seeing the sunlit side",
        distractors=[
            "It uses a very wide-angle lens",
            "It is very far from Earth",
            "Earth is always fully lit",
        ],
        explanation="EPIC is positioned at L1, between Earth and the Sun. It always faces Earth's sunlit side, so it sees a full, illuminated disc.",
    ))

    if images:
        img = images[0]
        # Q3: Date identification
        wrong_dates = []
        for delta in [1, -2, 5]:
            from datetime import timedelta
            d = img.date_taken + timedelta(days=delta)
            wrong_dates.append(d.strftime("%Y-%m-%d"))
        created.append(Quiz.objects.create(
            mission=mission, auto_generated=True, difficulty=2,
            question=f"When was this Earth image captured by EPIC?",
            correct_answer=img.date_taken.strftime("%Y-%m-%d"),
            distractors=wrong_dates[:3],
            explanation=f"This image was taken on {img.date_taken.strftime('%B %d, %Y')}.",
        ))

    return created[:n]
