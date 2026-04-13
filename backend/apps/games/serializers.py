"""DRF serializers + the payload builder used to warm the Redis 'today' cache."""
from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.nasa_ingest.models import (
    APODEntry, EPICImage, Exoplanet, MarsPhoto, NEOApproach, NEOObject,
)
from .models import JigsawPuzzle, Mission, Planet, Quiz


# --------------------------------------------------------------------------- #
# Shared sub-serializers
# --------------------------------------------------------------------------- #

class QuizSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ("id", "question", "options", "difficulty")

    def get_options(self, obj: Quiz) -> list[str]:
        import random
        opts = [obj.correct_answer, *obj.distractors]
        random.shuffle(opts)
        return opts


class JigsawSerializer(serializers.ModelSerializer):
    class Meta:
        model = JigsawPuzzle
        fields = ("image_url", "piece_count", "grid_cols", "grid_rows", "piece_data")


# --------------------------------------------------------------------------- #
# NASA content serializers
# --------------------------------------------------------------------------- #

class APODSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = APODEntry
        fields = ("date", "title", "explanation", "media_type", "image", "copyright")

    def get_image(self, obj: APODEntry) -> str:
        return obj.proxied_url or obj.image_url


class MarsPhotoSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = MarsPhoto
        fields = ("rover", "camera", "sol", "earth_date", "image")

    def get_image(self, obj: MarsPhoto) -> str:
        return obj.proxied_url or obj.image_url


class NEOApproachSerializer(serializers.ModelSerializer):
    class Meta:
        model = NEOApproach
        fields = ("approach_date", "velocity_kmh", "miss_distance_km",
                  "threat_score", "size_comparison")


class NEOObjectSerializer(serializers.ModelSerializer):
    approaches = NEOApproachSerializer(many=True, read_only=True)

    class Meta:
        model = NEOObject
        fields = ("neo_id", "name", "diameter_min_m", "diameter_max_m",
                  "is_hazardous", "approaches")


class EPICImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = EPICImage
        fields = ("identifier", "caption", "date_taken", "image",
                  "centroid_lat", "centroid_lon")

    def get_image(self, obj: EPICImage) -> str:
        return obj.proxied_url or obj.image_url


class ExoplanetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exoplanet
        fields = ("name", "host_star", "mass_earth", "radius_earth",
                  "orbital_period_days", "equilibrium_temp_k", "distance_ly",
                  "discovery_year", "habitability_score", "fun_fact")


# --------------------------------------------------------------------------- #
# Mission serializers
# --------------------------------------------------------------------------- #

class MissionListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = ("slug", "title", "mission_type", "xp_reward", "difficulty")


class MissionDetailSerializer(serializers.ModelSerializer):
    apod = APODSerializer(read_only=True)
    mars_photo = MarsPhotoSerializer(read_only=True)
    neo = NEOObjectSerializer(read_only=True)
    epic_image = EPICImageSerializer(read_only=True)
    exoplanet = ExoplanetSerializer(read_only=True)
    jigsaw = JigsawSerializer(read_only=True)
    quizzes = QuizSerializer(many=True, read_only=True)
    is_cross_api = serializers.BooleanField(read_only=True)
    cross_api_sources = serializers.JSONField(read_only=True)

    class Meta:
        model = Mission
        fields = ("slug", "title", "mission_type", "xp_reward", "difficulty",
                  "apod", "mars_photo", "neo", "epic_image", "exoplanet",
                  "jigsaw", "quizzes", "is_cross_api", "cross_api_sources")


class PlanetSerializer(serializers.ModelSerializer):
    mission_count = serializers.SerializerMethodField()

    class Meta:
        model = Planet
        fields = ("slug", "name", "description", "is_unlocked", "mission_count")

    def get_mission_count(self, obj: Planet) -> int:
        return obj.missions.filter(is_published=True).count()


# --------------------------------------------------------------------------- #
# /nasa/today/ builder
# --------------------------------------------------------------------------- #

class TodayPayloadSerializer:
    """Not a ModelSerializer — builds the /nasa/today/ dict for Redis caching."""

    @staticmethod
    def build(entry: APODEntry) -> dict[str, Any]:
        from django.core.cache import cache
        mission = entry.missions.filter(is_published=True).first()
        neo_count = cache.get("neo:approaching_count") or 0
        return {
            "apod": APODSerializer(entry).data,
            "mission_slug": mission.slug if mission else None,
            "neo_approaching_count": neo_count,
        }
