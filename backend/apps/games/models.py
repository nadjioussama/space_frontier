"""Game / Mission / Quiz / Jigsaw models. PLAN §8.2.

Phases 1+2: APOD slice only.
Phase 4: adds mission_type variants and content FKs for Mars, NEO, EPIC, Exoplanet.
Phase 5: adds prerequisites, achievements, DDA difficulty.
"""
from django.db import models

from apps.nasa_ingest.models import (
    APODEntry, EPICImage, Exoplanet, MarsPhoto, NEOObject,
)

MISSION_TYPES = [
    ("apod_daily", "APOD Daily"),
    ("mars_rover", "Mars Rover"),
    ("neo_defense", "Planetary Defense (NEO)"),
    ("epic_observer", "Earth Observer (EPIC)"),
    ("exoplanet_explorer", "Exoplanet Explorer"),
    ("cross_api", "Cross-API Mission"),
]


class Planet(models.Model):
    """Nodes on the Space Map."""
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    is_unlocked = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Mission(models.Model):
    slug = models.SlugField(unique=True, max_length=80)
    title = models.CharField(max_length=255)
    planet = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name="missions")
    mission_type = models.CharField(max_length=32, choices=MISSION_TYPES, default="apod_daily")

    # Content FKs — a mission links to ONE content source. Nullable because not
    # all types use all FKs. Phase 5 may add GenericRelation for cross-API missions.
    apod = models.ForeignKey(
        APODEntry, on_delete=models.CASCADE, related_name="missions",
        null=True, blank=True,
    )
    mars_photo = models.ForeignKey(
        MarsPhoto, on_delete=models.SET_NULL, related_name="missions",
        null=True, blank=True,
    )
    neo = models.ForeignKey(
        NEOObject, on_delete=models.SET_NULL, related_name="missions",
        null=True, blank=True,
    )
    epic_image = models.ForeignKey(
        EPICImage, on_delete=models.SET_NULL, related_name="missions",
        null=True, blank=True,
    )
    exoplanet = models.ForeignKey(
        Exoplanet, on_delete=models.SET_NULL, related_name="missions",
        null=True, blank=True,
    )

    xp_reward = models.IntegerField(default=50)
    difficulty = models.IntegerField(default=3)   # 1..10; DDA reads this
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Phase 5: cross-API missions can reference multiple content sources
    is_cross_api = models.BooleanField(default=False)
    cross_api_sources = models.JSONField(default=list, blank=True)

    # Phase 5: prerequisite missions for skill-tree gating
    prerequisites = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="unlocked_by")

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.title


class Quiz(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name="quizzes")
    question = models.TextField()
    correct_answer = models.CharField(max_length=500)
    # Postgres-agnostic: keep as JSON list of strings (3 distractors).
    distractors = models.JSONField(default=list)
    explanation = models.TextField(blank=True)
    difficulty = models.IntegerField(default=3)
    auto_generated = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.question[:60]


class JigsawPuzzle(models.Model):
    mission = models.OneToOneField(Mission, on_delete=models.CASCADE, related_name="jigsaw")
    image_url = models.URLField(max_length=1000)
    piece_count = models.IntegerField(default=12)          # 12 / 24 / 48
    grid_cols = models.IntegerField(default=4)
    grid_rows = models.IntegerField(default=3)
    # Phase 1 uses a simple grid. Irregular edge shapes come later; piece_data
    # stays as a JSON blob so the renderer contract is forward-compatible.
    piece_data = models.JSONField(default=list)

    def __str__(self) -> str:
        return f"Jigsaw x{self.piece_count} for {self.mission_id}"
