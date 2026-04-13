"""Redis-sorted-set leaderboard. PLAN §8.4, §3.8.

These tests use a real Redis (provided by docker-compose / CI) on the test DB
configured in settings.test, and clean up after themselves.
"""
from __future__ import annotations

from django.test import SimpleTestCase

from apps.progress import leaderboard as lb


class LeaderboardTests(SimpleTestCase):
    def setUp(self) -> None:
        lb._redis.delete(lb.WEEKLY_KEY)
        lb._redis.delete(f"{lb.PLANET_KEY_PREFIX}mars")

    def tearDown(self) -> None:
        lb._redis.delete(lb.WEEKLY_KEY)
        lb._redis.delete(f"{lb.PLANET_KEY_PREFIX}mars")
        for k in lb._redis.scan_iter("leaderboard:archive:*"):
            lb._redis.delete(k)

    def test_add_and_rank(self):
        lb.add_xp(1, 100, planet_slug="mars")
        lb.add_xp(2, 250, planet_slug="mars")
        lb.add_xp(1, 50, planet_slug="mars")  # accumulates

        top = lb.get_weekly_top(10)
        self.assertEqual([e["player_id"] for e in top], [2, 1])
        self.assertEqual(top[0], {"player_id": 2, "score": 250, "rank": 1})
        self.assertEqual(top[1], {"player_id": 1, "score": 150, "rank": 2})

        planet_top = lb.get_planet_top("mars", 10)
        self.assertEqual([e["player_id"] for e in planet_top], [2, 1])

    def test_player_rank_lookup(self):
        lb.add_xp(1, 100)
        lb.add_xp(2, 200)
        info = lb.get_player_rank(1)
        self.assertEqual(info, {"rank": 2, "score": 100})

    def test_unranked_player(self):
        self.assertIsNone(lb.get_player_rank(999))

    def test_empty_board(self):
        self.assertEqual(lb.get_weekly_top(), [])

    def test_reset_archives_and_clears(self):
        lb.add_xp(1, 10)
        lb.add_xp(2, 20)
        cleared = lb.reset_weekly()
        self.assertEqual(cleared, 2)
        self.assertEqual(lb.get_weekly_top(), [])
        archived = list(lb._redis.scan_iter("leaderboard:archive:*"))
        self.assertEqual(len(archived), 1)
        self.assertEqual(lb._redis.zcard(archived[0]), 2)
