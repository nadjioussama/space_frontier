"""Mission generation per content type. PLAN §7.5, §2.3."""
from __future__ import annotations

from django.core.cache import cache
from django.test import TestCase

from apps.games import services
from apps.games.models import Mission, Planet

from .factories import (
    make_apod, make_epic, make_exoplanet, make_mars_photo, make_neo,
)


class APODMissionTests(TestCase):
    def setUp(self) -> None:
        cache.clear()

    def test_creates_mission_with_jigsaw_and_quizzes(self):
        entry = make_apod()
        m = services.generate_apod_mission(entry)
        self.assertEqual(m.mission_type, "apod_daily")
        self.assertEqual(m.planet.slug, "earth")
        self.assertEqual(m.apod_id, entry.id)
        self.assertTrue(hasattr(m, "jigsaw"))
        self.assertEqual(m.jigsaw.piece_count, 12)
        self.assertEqual(m.quizzes.count(), 3)

    def test_idempotent(self):
        entry = make_apod()
        m1 = services.generate_apod_mission(entry)
        m2 = services.generate_apod_mission(entry)
        self.assertEqual(m1.pk, m2.pk)
        self.assertEqual(Mission.objects.count(), 1)

    def test_video_apod_skips_jigsaw(self):
        from apps.games.models import JigsawPuzzle
        entry = make_apod(media_type="video", proxied_url="", image_url="")
        m = services.generate_apod_mission(entry)
        self.assertFalse(JigsawPuzzle.objects.filter(mission=m).exists())


class MarsMissionTests(TestCase):
    def test_groups_by_sol(self):
        photos = [
            make_mars_photo(nasa_id=1, sol=100),
            make_mars_photo(nasa_id=2, sol=100),
            make_mars_photo(nasa_id=3, sol=101),
        ]
        missions = services.generate_mars_missions(photos)
        slugs = {m.slug for m in missions}
        self.assertEqual(slugs, {"mars-perseverance-sol-100", "mars-perseverance-sol-101"})
        for m in missions:
            self.assertEqual(m.mission_type, "mars_rover")
            self.assertEqual(m.planet.slug, "mars")
            self.assertGreater(m.quizzes.count(), 0)

    def test_empty(self):
        self.assertEqual(services.generate_mars_missions([]), [])


class NEOMissionTests(TestCase):
    def test_single_daily_mission(self):
        neos = [make_neo("1", hazardous=True), make_neo("2")]
        missions = services.generate_neo_missions(neos)
        self.assertEqual(len(missions), 1)
        m = missions[0]
        self.assertEqual(m.mission_type, "neo_defense")
        self.assertEqual(m.planet.slug, "asteroid-belt")
        self.assertGreater(m.quizzes.count(), 0)


class EPICMissionTests(TestCase):
    def test_creates_with_jigsaw(self):
        imgs = [make_epic("e1"), make_epic("e2")]
        missions = services.generate_epic_missions(imgs)
        self.assertEqual(len(missions), 1)
        m = missions[0]
        self.assertEqual(m.mission_type, "epic_observer")
        self.assertEqual(m.planet.slug, "earth")
        self.assertEqual(m.jigsaw.piece_count, 12)


class ExoplanetMissionTests(TestCase):
    def test_top_n_by_habitability(self):
        planets = [
            make_exoplanet(name=f"P{i}", habitability_score=i * 10) for i in range(1, 8)
        ]
        missions = services.generate_exoplanet_missions(planets)
        self.assertEqual(len(missions), 5)
        # Highest scores first
        self.assertEqual(missions[0].title, "Explore P7")
        for m in missions:
            self.assertEqual(m.mission_type, "exoplanet_explorer")
            self.assertGreater(m.quizzes.count(), 0)


class CrossAPIMissionTests(TestCase):
    def test_creates_all_templates(self):
        missions = services.generate_cross_api_missions()
        self.assertEqual(len(missions), len(services.CROSS_API_TEMPLATES))
        for m in missions:
            self.assertTrue(m.is_cross_api)
            self.assertEqual(m.mission_type, "cross_api")
            self.assertGreater(len(m.cross_api_sources), 0)
            self.assertGreater(m.quizzes.count(), 0)

    def test_idempotent(self):
        services.generate_cross_api_missions()
        services.generate_cross_api_missions()
        self.assertEqual(
            Mission.objects.filter(mission_type="cross_api").count(),
            len(services.CROSS_API_TEMPLATES),
        )


class PlanetFactoryTests(TestCase):
    def test_lazy_creates_once(self):
        services._earth()
        services._earth()
        self.assertEqual(Planet.objects.filter(slug="earth").count(), 1)
