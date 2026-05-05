"""Minimal quiz generator. PLAN §7.5.

LLM-quality distractor mining is Phase 4+; Phase 1 uses template questions
derived from APOD metadata (title, date, media_type) with a handful of curated
distractors. Good enough to prove the end-to-end loop and exercise the schema.
"""
from __future__ import annotations

import random

from apps.nasa_ingest.models import APODEntry
from ..models import Mission, Quiz

_OBJECT_TYPES = ["nebula", "galaxy", "star cluster", "planet", "comet", "supernova remnant"]
_MEDIA = ["image", "video", "interactive 3D model"]


def _question_about_date(entry: APODEntry) -> dict:
    correct = entry.date.isoformat()
    # 3 plausible wrong dates near the real one
    others = set()
    while len(others) < 3:
        delta = random.choice([-5, -3, -1, 1, 2, 4, 7, 10])
        candidate = entry.date.fromordinal(entry.date.toordinal() + delta).isoformat()
        if candidate != correct:
            others.add(candidate)
    return {
        "question": f"On what date did NASA publish '{entry.title}' as the Picture of the Day?",
        "correct_answer": correct,
        "distractors": list(others),
        "explanation": (
            f"NASA's Astronomy Picture of the Day publishes a new image every "
            f"24 hours. This one appeared on {correct}."
        ),
        "difficulty": 2,
    }


def _question_about_media(entry: APODEntry) -> dict:
    correct = entry.media_type
    distractors = [m for m in _MEDIA if m != correct][:3]
    return {
        "question": f"What kind of media is today's APOD, '{entry.title}'?",
        "correct_answer": correct,
        "distractors": distractors,
        "explanation": "APOD publishes images most days, and occasionally videos.",
        "difficulty": 1,
    }


def _question_about_explanation(entry: APODEntry) -> dict:
    # Pull the first sentence as a fact; produce a "true/false"-style question.
    # Robust-ish: strip trailing whitespace, bail gracefully if text is short.
    first = (entry.explanation or "").strip().split(".")[0].strip()
    if len(first) < 20:
        first = "The object shown was photographed for the APOD archive"
    return {
        "question": f"True or false: {first}.",
        "correct_answer": "True",
        "distractors": ["False", "Not enough information", "Only partially true"],
        "explanation": f"The full NASA explanation: {entry.explanation[:240]}...",
        "difficulty": 3,
    }


def generate(mission: Mission, entry: APODEntry, n: int = 3) -> list[Quiz]:
    # Clear existing auto-generated questions on re-ingest
    Quiz.objects.filter(mission=mission, auto_generated=True).delete()
    generators = [_question_about_date, _question_about_media, _question_about_explanation]
    random.shuffle(generators)
    created: list[Quiz] = []
    for g in generators[:n]:
        data = g(entry)
        created.append(Quiz.objects.create(mission=mission, auto_generated=True, **data))
    return created
