"""Quiz generator for Mars Rover missions. PLAN §2.2.2."""
from __future__ import annotations

import random

from apps.nasa_ingest.models import MarsPhoto
from ..models import Mission, Quiz

_CAMERAS = {
    "fhaz": "Front Hazard Avoidance Camera",
    "rhaz": "Rear Hazard Avoidance Camera",
    "mast": "Mast Camera",
    "navcam": "Navigation Camera",
    "chemcam": "Chemistry and Camera Complex",
    "mahli": "Mars Hand Lens Imager",
    "mcz": "Mastcam-Z",
}


def generate(mission: Mission, photos: list[MarsPhoto], n: int = 3) -> list[Quiz]:
    Quiz.objects.filter(mission=mission, auto_generated=True).delete()
    created = []

    if photos:
        p = photos[0]
        # Q1: Which rover?
        correct_rover = p.rover.title()
        distractors = [r for r in ["Curiosity", "Perseverance", "Opportunity", "Spirit"]
                       if r != correct_rover][:3]
        created.append(Quiz.objects.create(
            mission=mission, auto_generated=True, difficulty=2,
            question=f"Which Mars rover captured this photo on Sol {p.sol}?",
            correct_answer=correct_rover,
            distractors=distractors,
            explanation=f"{correct_rover} has been exploring Mars since its landing.",
        ))

        # Q2: Which camera?
        cam_full = _CAMERAS.get(p.camera, p.camera)
        other_cams = [v for k, v in _CAMERAS.items() if k != p.camera]
        random.shuffle(other_cams)
        created.append(Quiz.objects.create(
            mission=mission, auto_generated=True, difficulty=3,
            question=f"What camera type was used: '{p.camera.upper()}'?",
            correct_answer=cam_full,
            distractors=other_cams[:3],
            explanation=f"'{p.camera.upper()}' stands for {cam_full}.",
        ))

        # Q3: Sol timing
        created.append(Quiz.objects.create(
            mission=mission, auto_generated=True, difficulty=2,
            question="How long is one Martian day (sol) compared to Earth?",
            correct_answer="About 24 hours and 37 minutes",
            distractors=["Exactly 24 hours", "About 12 hours", "About 48 hours"],
            explanation="A Martian sol is 24h 37m — almost the same as Earth!",
        ))

    return created[:n]
