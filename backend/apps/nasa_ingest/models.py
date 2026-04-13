"""NASA content models. PLAN §8.2.

Phase 1 had only APOD. Phase 4 adds MarsPhoto, NEOObject, NEOApproach,
EPICImage, and Exoplanet — each subclassing `NASAContent`.
"""
from django.db import models


class NASAContent(models.Model):
    """Abstract base: everything we ingest from NASA shares these fields."""
    source_api = models.CharField(max_length=32)
    source_id = models.CharField(max_length=255)
    raw_url = models.URLField(max_length=1000, blank=True)
    ingested_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        abstract = True


# --------------------------------------------------------------------------- #
# APOD (Phase 1)
# --------------------------------------------------------------------------- #

class APODEntry(NASAContent):
    date = models.DateField(unique=True)
    title = models.CharField(max_length=255)
    explanation = models.TextField()
    media_type = models.CharField(max_length=16)
    image_url = models.URLField(max_length=1000)
    hd_image_url = models.URLField(max_length=1000, blank=True)
    proxied_url = models.URLField(max_length=1000, blank=True)
    copyright = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ("-date",)
        indexes = [models.Index(fields=["-date"])]

    def __str__(self) -> str:
        return f"APOD {self.date}: {self.title}"


# --------------------------------------------------------------------------- #
# Mars Rover Photos (Phase 4) — PLAN §2.2.2
# --------------------------------------------------------------------------- #

class MarsPhoto(NASAContent):
    ROVERS = [("curiosity", "Curiosity"), ("perseverance", "Perseverance"), ("opportunity", "Opportunity")]
    CAMERAS = [
        ("fhaz", "Front Hazard"), ("rhaz", "Rear Hazard"), ("mast", "Mast"),
        ("chemcam", "ChemCam"), ("mahli", "MAHLI"), ("mardi", "MARDI"),
        ("navcam", "Navcam"), ("pancam", "Pancam"), ("minites", "Mini-TES"),
        ("mcz", "Mastcam-Z"), ("skycam", "SkyCam"), ("sherloc", "SHERLOC"),
    ]
    rover = models.CharField(max_length=32, choices=ROVERS)
    camera = models.CharField(max_length=32, choices=CAMERAS)
    sol = models.IntegerField()
    earth_date = models.DateField()
    image_url = models.URLField(max_length=1000)
    proxied_url = models.URLField(max_length=1000, blank=True)
    nasa_photo_id = models.IntegerField(unique=True)

    class Meta:
        ordering = ("-earth_date", "-sol")
        indexes = [
            models.Index(fields=["rover", "-sol"]),
            models.Index(fields=["-earth_date"]),
        ]

    def __str__(self) -> str:
        return f"Mars {self.rover} Sol {self.sol} ({self.camera})"


# --------------------------------------------------------------------------- #
# NeoWs — Near Earth Objects (Phase 4) — PLAN §2.2.3
# --------------------------------------------------------------------------- #

class NEOObject(NASAContent):
    neo_id = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    diameter_min_m = models.FloatField()
    diameter_max_m = models.FloatField()
    is_hazardous = models.BooleanField()

    class Meta:
        ordering = ("-ingested_at",)

    def __str__(self) -> str:
        haz = " (HAZARDOUS)" if self.is_hazardous else ""
        return f"NEO {self.name}{haz}"


class NEOApproach(models.Model):
    neo = models.ForeignKey(NEOObject, on_delete=models.CASCADE, related_name="approaches")
    approach_date = models.DateTimeField()
    velocity_kmh = models.FloatField()
    miss_distance_km = models.FloatField()
    # Derived fields for gameplay (PLAN §2.2.3)
    threat_score = models.IntegerField(default=0)           # computed 0-100
    size_comparison = models.CharField(max_length=64, blank=True)  # "school bus", "football field"

    class Meta:
        ordering = ("approach_date",)
        indexes = [models.Index(fields=["approach_date"])]
        unique_together = [("neo", "approach_date")]

    def __str__(self) -> str:
        return f"{self.neo.name} approach on {self.approach_date.date()}"


# --------------------------------------------------------------------------- #
# EPIC — Earth Polychromatic Camera (Phase 4) — PLAN §2.2.5
# --------------------------------------------------------------------------- #

class EPICImage(NASAContent):
    identifier = models.CharField(max_length=64, unique=True)
    caption = models.TextField(blank=True)
    image_name = models.CharField(max_length=128)
    image_url = models.URLField(max_length=1000)
    proxied_url = models.URLField(max_length=1000, blank=True)
    date_taken = models.DateTimeField()
    # Centroid coordinates — useful for "find your continent" minigame
    centroid_lat = models.FloatField(null=True, blank=True)
    centroid_lon = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ("-date_taken",)
        indexes = [models.Index(fields=["-date_taken"])]

    def __str__(self) -> str:
        return f"EPIC {self.date_taken.date()} ({self.image_name})"


# --------------------------------------------------------------------------- #
# Exoplanets (Phase 4) — PLAN §2.2.6
# --------------------------------------------------------------------------- #

class Exoplanet(NASAContent):
    name = models.CharField(max_length=128, unique=True)
    host_star = models.CharField(max_length=128)
    mass_earth = models.FloatField(null=True, blank=True)
    radius_earth = models.FloatField(null=True, blank=True)
    orbital_period_days = models.FloatField(null=True, blank=True)
    equilibrium_temp_k = models.FloatField(null=True, blank=True)
    distance_ly = models.FloatField(null=True, blank=True)
    discovery_year = models.IntegerField(null=True, blank=True)
    # Derived (PLAN §2.2.6)
    habitability_score = models.IntegerField(default=0)     # computed 0-100
    fun_fact = models.TextField(blank=True)                 # admin-editable

    class Meta:
        ordering = ("-discovery_year", "name")
        indexes = [
            models.Index(fields=["-discovery_year"]),
            models.Index(fields=["-habitability_score"]),
        ]

    def __str__(self) -> str:
        return f"Exoplanet {self.name} (hab={self.habitability_score})"
