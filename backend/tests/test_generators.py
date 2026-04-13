"""Quiz + jigsaw generators. PLAN §7.5."""
from __future__ import annotations

from django.test import SimpleTestCase, TestCase

from apps.games.generators import (
    cross_api_quiz, epic_quiz, exoplanet_quiz, jigsaw, mars_quiz, neo_quiz, quiz,
)
from apps.games.generators.jigsaw import _grid_for, build_grid_pieces
from apps.games.models import JigsawPuzzle, Quiz

from .factories import (
    make_apod, make_epic, make_exoplanet, make_mars_photo, make_mission, make_neo,
)


# --------------------------------------------------------------------------- #
# Jigsaw
# --------------------------------------------------------------------------- #

class JigsawGridTests(SimpleTestCase):
    def test_supported_piece_counts(self):
        self.assertEqual(_grid_for(12), (4, 3))
        self.assertEqual(_grid_for(24), (6, 4))
        self.assertEqual(_grid_for(48), (8, 6))

    def test_unknown_count_falls_back(self):
        self.assertEqual(_grid_for(7), (4, 3))

    def test_pieces_tile_unit_square(self):
        pieces = build_grid_pieces(4, 3)
        self.assertEqual(len(pieces), 12)
        # ids unique and sequential
        self.assertEqual(sorted(p["id"] for p in pieces), list(range(12)))
        # row-of-4 widths sum to 1.0
        row0 = [p for p in pieces if p["row"] == 0]
        self.assertAlmostEqual(sum(p["w"] for p in row0), 1.0, places=5)
        # col-of-3 heights sum to 1.0
        col0 = [p for p in pieces if p["col"] == 0]
        self.assertAlmostEqual(sum(p["h"] for p in col0), 1.0, places=5)
        # last piece sits at bottom-right
        last = next(p for p in pieces if p["id"] == 11)
        self.assertEqual((last["row"], last["col"]), (2, 3))


class JigsawPersistTests(TestCase):
    def test_generate_persists_and_is_idempotent(self):
        m = make_mission()
        jigsaw.generate(m, "https://x/img.jpg", piece_count=24)
        jigsaw.generate(m, "https://x/img.jpg", piece_count=24)
        self.assertEqual(JigsawPuzzle.objects.filter(mission=m).count(), 1)
        jp = m.jigsaw
        self.assertEqual(jp.piece_count, 24)
        self.assertEqual((jp.grid_cols, jp.grid_rows), (6, 4))
        self.assertEqual(len(jp.piece_data), 24)


# --------------------------------------------------------------------------- #
# Quiz generators — every generator must produce well-formed Quiz rows where
# the correct answer is never duplicated in distractors.
# --------------------------------------------------------------------------- #

def _assert_well_formed(tc: TestCase, quizzes: list[Quiz]) -> None:
    tc.assertGreater(len(quizzes), 0)
    for q in quizzes:
        tc.assertTrue(q.question)
        tc.assertTrue(q.correct_answer)
        tc.assertIsInstance(q.distractors, list)
        tc.assertNotIn(q.correct_answer, q.distractors,
                       f"correct answer leaked into distractors: {q.question}")
        tc.assertGreaterEqual(len(q.distractors), 1)


class APODQuizTests(TestCase):
    def test_generates_and_replaces(self):
        m = make_mission()
        e = make_apod()
        quiz.generate(m, e, n=3)
        self.assertEqual(m.quizzes.count(), 3)
        quiz.generate(m, e, n=3)  # re-ingest replaces
        self.assertEqual(m.quizzes.count(), 3)
        _assert_well_formed(self, list(m.quizzes.all()))


class MarsQuizTests(TestCase):
    def test_generates(self):
        m = make_mission(slug="mars-m")
        photos = [make_mars_photo(nasa_id=i) for i in range(1, 4)]
        out = mars_quiz.generate(m, photos, n=3)
        self.assertEqual(len(out), 3)
        _assert_well_formed(self, out)

    def test_empty_input_yields_nothing(self):
        m = make_mission(slug="mars-empty")
        self.assertEqual(mars_quiz.generate(m, [], n=3), [])


class NeoQuizTests(TestCase):
    def test_generates(self):
        m = make_mission(slug="neo-m")
        neos = [make_neo("1", hazardous=True), make_neo("2"), make_neo("3")]
        out = neo_quiz.generate(m, neos, n=4)
        self.assertGreaterEqual(len(out), 3)
        _assert_well_formed(self, out)
        # First question is the hazardous-count one
        self.assertEqual(out[0].correct_answer, "1")


class EpicQuizTests(TestCase):
    def test_generates(self):
        m = make_mission(slug="epic-m")
        imgs = [make_epic("e1"), make_epic("e2")]
        out = epic_quiz.generate(m, imgs, n=3)
        self.assertEqual(len(out), 3)
        _assert_well_formed(self, out)

    def test_no_images_still_yields_static_questions(self):
        m = make_mission(slug="epic-empty")
        out = epic_quiz.generate(m, [], n=3)
        self.assertEqual(len(out), 2)


class ExoplanetQuizTests(TestCase):
    def test_generates_with_full_data(self):
        m = make_mission(slug="exo-m")
        exo = make_exoplanet()
        out = exoplanet_quiz.generate(m, exo, n=3)
        self.assertEqual(len(out), 3)
        _assert_well_formed(self, out)

    def test_sparse_planet_uses_fallback(self):
        m = make_mission(slug="exo-sparse")
        exo = make_exoplanet(name="Bare-1", equilibrium_temp_k=None,
                             radius_earth=None, discovery_year=None)
        out = exoplanet_quiz.generate(m, exo, n=3)
        self.assertGreaterEqual(len(out), 1)
        _assert_well_formed(self, out)


class CrossAPIQuizTests(TestCase):
    def test_every_template_has_a_bank(self):
        from apps.games.services import CROSS_API_TEMPLATES
        for tmpl in CROSS_API_TEMPLATES:
            self.assertIn(tmpl["slug"], cross_api_quiz._BANKS,
                          f"no question bank for {tmpl['slug']}")

    def test_generates_from_bank(self):
        m = make_mission(slug="cross-m")
        out = cross_api_quiz.generate(m, "cross-scale-of-everything")
        self.assertEqual(len(out), len(cross_api_quiz._BANKS["cross-scale-of-everything"]))
        _assert_well_formed(self, out)

    def test_unknown_template_yields_empty(self):
        m = make_mission(slug="cross-unknown")
        self.assertEqual(cross_api_quiz.generate(m, "nope"), [])
