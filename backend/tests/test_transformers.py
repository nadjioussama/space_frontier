"""Transformers: raw NASA JSON → Django models. PLAN §5.2 Layer 2."""
from __future__ import annotations

from unittest import mock

from django.test import SimpleTestCase, TestCase

from apps.nasa_ingest.models import Exoplanet, NEOApproach, NEOObject
from apps.nasa_ingest.transformers.exoplanet import (
    ExoplanetTransformer, _habitability_score,
)
from apps.nasa_ingest.transformers.neows import (
    NeoWsTransformer, _size_comparison, _threat_score,
)


# --------------------------------------------------------------------------- #
# NeoWs helpers (pure functions)
# --------------------------------------------------------------------------- #

class NeoHelperTests(SimpleTestCase):
    def test_size_comparison_thresholds(self):
        self.assertEqual(_size_comparison(0.5), "pebble")
        self.assertEqual(_size_comparison(3), "basketball")
        self.assertEqual(_size_comparison(12), "car")
        self.assertEqual(_size_comparison(20), "school bus")
        self.assertEqual(_size_comparison(120), "football field")
        self.assertEqual(_size_comparison(9000), "small town")

    def test_threat_score_bounds(self):
        self.assertEqual(_threat_score(0, 1, 1), 0)
        self.assertEqual(_threat_score(100, 50000, 0), 0)
        s = _threat_score(100, 50000, 1_000_000)
        self.assertGreaterEqual(s, 0)
        self.assertLessEqual(s, 100)

    def test_threat_score_closer_is_higher(self):
        far = _threat_score(100, 50000, 5_000_000)
        near = _threat_score(100, 50000, 100_000)
        self.assertGreater(near, far)

    def test_threat_score_bigger_is_higher(self):
        small = _threat_score(10, 50000, 1_000_000)
        big = _threat_score(1000, 50000, 1_000_000)
        self.assertGreater(big, small)


class NeoTransformerTests(TestCase):
    FEED = {
        "near_earth_objects": {
            "2026-04-13": [
                {
                    "id": "54016054",
                    "name": "(2020 GE)",
                    "nasa_jpl_url": "https://ssd.jpl.nasa.gov/x",
                    "is_potentially_hazardous_asteroid": True,
                    "estimated_diameter": {
                        "meters": {"estimated_diameter_min": 18.0, "estimated_diameter_max": 40.0},
                    },
                    "close_approach_data": [
                        {
                            "close_approach_date_full": "2026-04-13 14:22",
                            "relative_velocity": {"kilometers_per_hour": "48000.5"},
                            "miss_distance": {"kilometers": "750000.0"},
                        },
                    ],
                },
            ],
        },
    }

    def test_creates_neo_and_approach(self):
        objs = NeoWsTransformer(self.FEED).to_models()
        self.assertEqual(len(objs), 1)
        neo = NEOObject.objects.get(neo_id="54016054")
        self.assertTrue(neo.is_hazardous)
        self.assertEqual(neo.approaches.count(), 1)
        appr = neo.approaches.first()
        self.assertEqual(appr.size_comparison, "school bus")  # avg ~29m
        self.assertGreater(appr.threat_score, 0)

    def test_idempotent_reingest(self):
        NeoWsTransformer(self.FEED).to_models()
        NeoWsTransformer(self.FEED).to_models()
        self.assertEqual(NEOObject.objects.count(), 1)
        self.assertEqual(NEOApproach.objects.count(), 1)

    def test_malformed_entry_is_skipped(self):
        feed = {"near_earth_objects": {"2026-04-13": [{"no_id": True}]}}
        out = NeoWsTransformer(feed).to_models()
        self.assertEqual(out, [])


# --------------------------------------------------------------------------- #
# Exoplanet helpers + transformer
# --------------------------------------------------------------------------- #

class HabitabilityTests(SimpleTestCase):
    def test_perfect_earthlike(self):
        self.assertEqual(_habitability_score(1.0, 1.0, 280), 100)

    def test_gas_giant_scores_low(self):
        self.assertLess(_habitability_score(300, 11, 120), 20)

    def test_partial_data(self):
        # Missing temp still scores on mass+radius
        self.assertEqual(_habitability_score(1.0, 1.0, None), 66)

    def test_all_none(self):
        self.assertEqual(_habitability_score(None, None, None), 0)


class ExoplanetTransformerTests(TestCase):
    def test_creates_with_derived_fields(self):
        records = [{
            "pl_name": "Kepler-442 b", "hostname": "Kepler-442",
            "pl_bmasse": 2.3, "pl_rade": 1.34, "pl_orbper": 112.3,
            "pl_eqt": 233, "disc_year": 2015, "sy_dist": 370.0,
        }]
        out = ExoplanetTransformer(records).to_models()
        self.assertEqual(len(out), 1)
        exo = Exoplanet.objects.get(name="Kepler-442 b")
        self.assertEqual(exo.habitability_score, 100)
        self.assertAlmostEqual(exo.distance_ly, 370.0 * 3.26156, places=1)

    def test_skips_unnamed(self):
        out = ExoplanetTransformer([{"hostname": "X"}]).to_models()
        self.assertEqual(out, [])

    def test_handles_missing_optionals(self):
        out = ExoplanetTransformer([{"pl_name": "Bare-1"}]).to_models()
        self.assertEqual(out[0].habitability_score, 0)
        self.assertIsNone(out[0].distance_ly)


# --------------------------------------------------------------------------- #
# APOD transformer (image download mocked)
# --------------------------------------------------------------------------- #

class APODTransformerTests(TestCase):
    @mock.patch("apps.nasa_ingest.transformers.apod.APODTransformer._download",
                return_value="/media/apod/x.jpg")
    def test_upserts_by_date(self, _):
        from apps.nasa_ingest.transformers.apod import APODTransformer
        raw = {
            "date": "2026-04-13", "title": "T", "explanation": "E",
            "media_type": "image", "url": "https://x/y.jpg", "hdurl": "",
        }
        e1 = APODTransformer(raw).to_model()
        e2 = APODTransformer({**raw, "title": "T2"}).to_model()
        self.assertEqual(e1.pk, e2.pk)
        e2.refresh_from_db()
        self.assertEqual(e2.title, "T2")

    def test_video_skips_download(self):
        from apps.nasa_ingest.transformers.apod import APODTransformer
        raw = {"date": "2026-04-12", "title": "V", "explanation": "",
               "media_type": "video", "url": "https://youtube.com/x"}
        e = APODTransformer(raw).to_model()
        self.assertEqual(e.proxied_url, "")


# --------------------------------------------------------------------------- #
# Mars transformer (image download mocked)
# --------------------------------------------------------------------------- #

class MarsTransformerTests(TestCase):
    @mock.patch("apps.nasa_ingest.transformers.mars.MarsPhotoTransformer._proxy_image",
                return_value="/media/mars/x.jpg")
    def test_creates_and_limits(self, _):
        from apps.nasa_ingest.transformers.mars import MarsPhotoTransformer
        raw = [
            {"id": i, "sol": 1000, "earth_date": "2026-04-01",
             "img_src": f"https://x/{i}.jpg",
             "rover": {"name": "Perseverance"}, "camera": {"short_name": "NAVCAM"}}
            for i in range(30)
        ]
        out = MarsPhotoTransformer(raw).to_models(limit=5)
        self.assertEqual(len(out), 5)
        self.assertEqual(out[0].rover, "perseverance")
        self.assertEqual(out[0].camera, "navcam")
