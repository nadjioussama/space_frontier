"""Tests for DRF serializers in apps/games/serializers.py."""
from __future__ import annotations


from django.core.cache import cache
from django.test import TestCase

from apps.games.models import JigsawPuzzle, Quiz
from apps.games.serializers import (
    APODSerializer,
    EPICImageSerializer,
    ExoplanetSerializer,
    JigsawSerializer,
    MarsPhotoSerializer,
    MissionDetailSerializer,
    NEOObjectSerializer,
    PlanetSerializer,
    QuizSerializer,
    TodayPayloadSerializer,
)

from .factories import (
    make_apod,
    make_epic,
    make_exoplanet,
    make_mars_photo,
    make_mission,
    make_neo,
    make_planet,
)


class QuizSerializerTests(TestCase):
    def setUp(self) -> None:
        cache.clear()
        self.mission = make_mission(slug="quiz-ser-test")
        self.quiz = Quiz.objects.create(
            mission=self.mission,
            question="What is the Sun?",
            correct_answer="A star",
            distractors=["A planet", "A moon", "An asteroid"],
            difficulty=3,
        )

    def test_options_contain_correct_answer(self):
        data = QuizSerializer(self.quiz).data
        self.assertIn("A star", data["options"])

    def test_correct_answer_field_not_leaked(self):
        data = QuizSerializer(self.quiz).data
        self.assertNotIn("correct_answer", data)

    def test_options_has_all_choices(self):
        data = QuizSerializer(self.quiz).data
        self.assertEqual(len(data["options"]), 4)
        self.assertIn("A planet", data["options"])
        self.assertIn("A moon", data["options"])
        self.assertIn("An asteroid", data["options"])

    def test_options_are_shuffled_sometimes(self):
        """Run serialization multiple times; at least one ordering should differ."""
        orderings = set()
        for _ in range(20):
            data = QuizSerializer(self.quiz).data
            orderings.add(tuple(data["options"]))
        # With 4 items and 20 tries, extremely unlikely to always get the same order
        self.assertGreater(len(orderings), 1)


class JigsawSerializerTests(TestCase):
    def setUp(self) -> None:
        cache.clear()
        self.mission = make_mission(slug="jigsaw-ser-test")
        self.jigsaw = JigsawPuzzle.objects.create(
            mission=self.mission,
            image_url="https://example.com/puzzle.jpg",
            piece_count=12,
            grid_cols=4,
            grid_rows=3,
            piece_data=[],
        )

    def test_all_fields_present(self):
        data = JigsawSerializer(self.jigsaw).data
        expected_fields = {"image_url", "piece_count", "grid_cols", "grid_rows", "piece_data"}
        self.assertEqual(set(data.keys()), expected_fields)


class APODSerializerTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    def test_image_resolves_proxied_url_first(self):
        entry = make_apod(
            d=None,
            image_url="https://nasa.gov/original.jpg",
            proxied_url="/media/apod/proxied.jpg",
        )
        data = APODSerializer(entry).data
        self.assertEqual(data["image"], "/media/apod/proxied.jpg")

    def test_image_falls_back_to_image_url_when_no_proxy(self):
        entry = make_apod(
            d=None,
            source_id="2026-04-14",
            date=__import__("datetime").date(2026, 4, 14),
            image_url="https://nasa.gov/original.jpg",
            proxied_url="",
        )
        data = APODSerializer(entry).data
        self.assertEqual(data["image"], "https://nasa.gov/original.jpg")


class MissionDetailSerializerTests(TestCase):
    def setUp(self) -> None:
        cache.clear()
        self.entry = make_apod()
        self.mission = make_mission(slug="detail-ser-test", apod=self.entry)
        self.jigsaw = JigsawPuzzle.objects.create(
            mission=self.mission,
            image_url="https://example.com/puzzle.jpg",
            piece_count=12,
            grid_cols=4,
            grid_rows=3,
            piece_data=[],
        )
        for i in range(3):
            Quiz.objects.create(
                mission=self.mission,
                question=f"Question {i}?",
                correct_answer=f"Answer {i}",
                distractors=[f"Wrong {j}" for j in range(3)],
                difficulty=3,
            )

    def test_full_payload_shape(self):
        data = MissionDetailSerializer(self.mission).data
        self.assertIn("slug", data)
        self.assertIn("title", data)
        self.assertIn("mission_type", data)
        self.assertIn("xp_reward", data)
        self.assertIn("difficulty", data)
        self.assertIn("apod", data)
        self.assertIn("jigsaw", data)
        self.assertIn("quizzes", data)
        self.assertIn("is_cross_api", data)
        self.assertIn("cross_api_sources", data)

    def test_nested_apod_present(self):
        data = MissionDetailSerializer(self.mission).data
        self.assertIsNotNone(data["apod"])
        self.assertEqual(data["apod"]["title"], "Test Nebula")

    def test_nested_jigsaw_present(self):
        data = MissionDetailSerializer(self.mission).data
        self.assertIsNotNone(data["jigsaw"])
        self.assertEqual(data["jigsaw"]["piece_count"], 12)

    def test_nested_quizzes_present(self):
        data = MissionDetailSerializer(self.mission).data
        self.assertEqual(len(data["quizzes"]), 3)


class PlanetSerializerTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    def test_mission_count_computed_correctly(self):
        planet = make_planet(slug="planet-ser-test")
        make_mission(slug="pub-1", planet=planet, is_published=True)
        make_mission(slug="pub-2", planet=planet, is_published=True)
        make_mission(slug="unpub-1", planet=planet, is_published=False)

        data = PlanetSerializer(planet).data
        self.assertEqual(data["mission_count"], 2)

    def test_mission_count_zero_when_no_missions(self):
        planet = make_planet(slug="empty-planet-ser")
        data = PlanetSerializer(planet).data
        self.assertEqual(data["mission_count"], 0)


class TodayPayloadSerializerTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    def test_build_returns_correct_shape(self):
        entry = make_apod()
        # Create a mission linked to the entry so the builder can find it
        from apps.games.services import generate_apod_mission
        mission = generate_apod_mission(entry)

        payload = TodayPayloadSerializer.build(entry)
        self.assertIn("apod", payload)
        self.assertIn("mission_slug", payload)
        self.assertIn("neo_approaching_count", payload)
        self.assertEqual(payload["mission_slug"], mission.slug)

    def test_includes_neo_count_from_cache(self):
        cache.set("neo:approaching_count", 7)
        entry = make_apod()
        from apps.games.services import generate_apod_mission
        generate_apod_mission(entry)

        payload = TodayPayloadSerializer.build(entry)
        self.assertEqual(payload["neo_approaching_count"], 7)

    def test_neo_count_defaults_to_zero(self):
        entry = make_apod()
        from apps.games.services import generate_apod_mission
        generate_apod_mission(entry)

        payload = TodayPayloadSerializer.build(entry)
        self.assertEqual(payload["neo_approaching_count"], 0)


class MarsPhotoSerializerTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    def test_image_resolves_proxied_url_first(self):
        photo = make_mars_photo(nasa_id=200, proxied_url="/media/mars/proxied.jpg")
        data = MarsPhotoSerializer(photo).data
        self.assertEqual(data["image"], "/media/mars/proxied.jpg")

    def test_image_falls_back_to_image_url(self):
        photo = make_mars_photo(nasa_id=201, proxied_url="")
        data = MarsPhotoSerializer(photo).data
        self.assertEqual(data["image"], "https://example.com/mars.jpg")

    def test_fields_present(self):
        photo = make_mars_photo(nasa_id=202)
        data = MarsPhotoSerializer(photo).data
        for field in ("rover", "camera", "sol", "earth_date", "image"):
            self.assertIn(field, data)


class NEOObjectSerializerTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    def test_fields_present(self):
        neo = make_neo(neo_id="ser-1")
        data = NEOObjectSerializer(neo).data
        for field in ("neo_id", "name", "diameter_min_m", "diameter_max_m", "is_hazardous", "approaches"):
            self.assertIn(field, data)

    def test_approaches_nested(self):
        neo = make_neo(neo_id="ser-2", with_approach=True)
        data = NEOObjectSerializer(neo).data
        self.assertEqual(len(data["approaches"]), 1)
        approach = data["approaches"][0]
        self.assertIn("threat_score", approach)
        self.assertIn("size_comparison", approach)


class EPICImageSerializerTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    def test_image_resolves_proxied_url_first(self):
        img = make_epic(identifier="epic-ser-1", proxied_url="/media/epic/proxied.png")
        data = EPICImageSerializer(img).data
        self.assertEqual(data["image"], "/media/epic/proxied.png")

    def test_fields_present(self):
        img = make_epic(identifier="epic-ser-2")
        data = EPICImageSerializer(img).data
        for field in ("identifier", "caption", "date_taken", "image", "centroid_lat", "centroid_lon"):
            self.assertIn(field, data)


class ExoplanetSerializerTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    def test_fields_present(self):
        exo = make_exoplanet(name="Ser-Test-Planet")
        data = ExoplanetSerializer(exo).data
        for field in ("name", "host_star", "mass_earth", "radius_earth",
                      "orbital_period_days", "equilibrium_temp_k", "distance_ly",
                      "discovery_year", "habitability_score", "fun_fact"):
            self.assertIn(field, data)

    def test_habitability_score_value(self):
        exo = make_exoplanet(name="Hab-Planet", habitability_score=95)
        data = ExoplanetSerializer(exo).data
        self.assertEqual(data["habitability_score"], 95)
