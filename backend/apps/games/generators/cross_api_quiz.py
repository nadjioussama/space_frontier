"""Quiz generator for cross-API missions. PLAN §2.3.

These missions combine knowledge from multiple NASA data sources into
thematic question sets that encourage systems thinking.
"""
from __future__ import annotations

from ..models import Mission, Quiz

# Pre-authored question banks keyed by cross-API mission slug.
# In production these would be admin-editable; for the walking skeleton
# we ship a curated set per template.

_BANKS: dict[str, list[dict]] = {
    "cross-is-there-life": [
        {
            "question": "Which of these is NOT a factor scientists consider when rating an exoplanet's habitability?",
            "correct_answer": "Whether it has rings",
            "distractors": ["Distance from its star", "Surface temperature", "Presence of liquid water"],
            "explanation": "Habitability depends on temperature, water, and atmospheric conditions — rings are irrelevant.",
            "difficulty": 5,
        },
        {
            "question": "Mars rovers have found evidence of ancient water. Which mineral is the strongest indicator?",
            "correct_answer": "Clay minerals (phyllosilicates)",
            "distractors": ["Iron oxide (rust)", "Quartz", "Diamond"],
            "explanation": "Clay minerals form in the presence of water over long periods — strong evidence Mars once had liquid water.",
            "difficulty": 6,
        },
        {
            "question": "Why does solar activity matter when searching for life on other planets?",
            "correct_answer": "Solar flares can strip away a planet's atmosphere",
            "distractors": ["Solar flares make planets hotter", "Stars with flares can't have planets", "Solar wind creates water"],
            "explanation": "Intense solar activity can erode planetary atmospheres, making it harder for life to survive on the surface.",
            "difficulty": 7,
        },
        {
            "question": "The 'Goldilocks zone' around a star is where conditions are...",
            "correct_answer": "Not too hot, not too cold — just right for liquid water",
            "distractors": ["Always exactly like Earth", "Perfect for gold mining", "Protected from all radiation"],
            "explanation": "The habitable zone is the region where temperatures allow liquid water to exist on a planet's surface.",
            "difficulty": 3,
        },
    ],
    "cross-defend-the-planet": [
        {
            "question": "What is the main way NASA tracks potentially hazardous asteroids?",
            "correct_answer": "Ground-based telescopes that detect reflected sunlight",
            "distractors": ["Sending probes to every asteroid", "Listening for radio signals", "Satellite cameras pointed outward"],
            "explanation": "Most NEOs are discovered by ground telescopes that spot sunlight bouncing off their surfaces.",
            "difficulty": 4,
        },
        {
            "question": "NASA's DART mission successfully tested what planetary defense technique?",
            "correct_answer": "Kinetic impactor — crashing a spacecraft into an asteroid to change its orbit",
            "distractors": ["Nuclear explosion near the asteroid", "Gravity tractor pulling", "Laser ablation of the surface"],
            "explanation": "DART hit asteroid Dimorphos in 2022 and measurably changed its orbit — the first real planetary defense test.",
            "difficulty": 5,
        },
        {
            "question": "EPIC images of Earth help planetary defense by...",
            "correct_answer": "Showing Earth's atmosphere and how it protects us from small impacts",
            "distractors": ["Tracking asteroids directly", "Predicting earthquakes", "Finding underground shelters"],
            "explanation": "EPIC observations help us understand Earth's atmospheric shield — most small asteroids burn up before reaching the surface.",
            "difficulty": 6,
        },
    ],
    "cross-day-in-space": [
        {
            "question": "The APOD (Astronomy Picture of the Day) has been published since which year?",
            "correct_answer": "1995",
            "distractors": ["2005", "1980", "2010"],
            "explanation": "APOD has published a new astronomy image every day since June 16, 1995 — one of the oldest websites still running!",
            "difficulty": 3,
        },
        {
            "question": "A Martian day (sol) is about how long compared to an Earth day?",
            "correct_answer": "About 24 hours and 37 minutes",
            "distractors": ["Exactly 24 hours", "About 12 hours", "About 48 hours"],
            "explanation": "A sol is very close to an Earth day, just 37 minutes longer.",
            "difficulty": 2,
        },
        {
            "question": "The EPIC camera orbits at the L1 point. What makes L1 special?",
            "correct_answer": "Gravity from Earth and Sun balance, so a satellite can stay between them",
            "distractors": ["It's the closest point to the Sun", "There's no gravity there", "It's where the Moon orbits"],
            "explanation": "L1 is a Lagrange point where gravitational forces balance, allowing DSCOVR to always face Earth's sunlit side.",
            "difficulty": 5,
        },
    ],
    "cross-scale-of-everything": [
        {
            "question": "Put these in order from smallest to largest: Mars rover wheel, school-bus-sized asteroid, Earth, the Sun.",
            "correct_answer": "Rover wheel → asteroid → Earth → Sun",
            "distractors": ["Asteroid → rover wheel → Sun → Earth", "Earth → Sun → asteroid → rover wheel", "Sun → Earth → rover wheel → asteroid"],
            "explanation": "A rover wheel is ~50cm, a school-bus asteroid ~12m, Earth ~12,700km, the Sun ~1.4 million km across.",
            "difficulty": 2,
        },
        {
            "question": "How many Earths could fit inside the Sun?",
            "correct_answer": "About 1.3 million",
            "distractors": ["About 100", "About 10,000", "About 10 million"],
            "explanation": "The Sun is so large that approximately 1.3 million Earths could fit inside its volume.",
            "difficulty": 4,
        },
        {
            "question": "If the Sun were a basketball, how far away would the nearest star (Proxima Centauri) be?",
            "correct_answer": "About 6,500 km (New York to London)",
            "distractors": ["About 1 km", "About 100 meters", "About 1 million km"],
            "explanation": "Even at basketball scale, the nearest star would be thousands of kilometers away — space is incredibly vast.",
            "difficulty": 6,
        },
    ],
}


def generate(mission: Mission, template_slug: str) -> list[Quiz]:
    """Generate quiz questions for a cross-API mission from the curated bank."""
    Quiz.objects.filter(mission=mission, auto_generated=True).delete()
    bank = _BANKS.get(template_slug, [])
    created = []
    for q in bank:
        created.append(Quiz.objects.create(
            mission=mission,
            auto_generated=True,
            question=q["question"],
            correct_answer=q["correct_answer"],
            distractors=q["distractors"],
            explanation=q["explanation"],
            difficulty=q["difficulty"],
        ))
    return created
