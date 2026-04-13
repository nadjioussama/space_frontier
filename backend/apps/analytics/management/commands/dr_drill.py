"""Quarterly DR drill helper. PLAN §11.10.

Times a restore-and-boot of the stack against a fresh DB and reports whether
RTO targets are met. Run inside the staging environment after pointing it at a
restored snapshot.
"""
from __future__ import annotations

import time

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Run a restore drill: migrate, warm caches, smoke-check, report timing."

    RTO_TARGET_SECONDS = 10 * 60

    def handle(self, *args, **opts):
        t0 = time.monotonic()

        self.stdout.write("→ migrate")
        call_command("migrate", interactive=False)

        self.stdout.write("→ warm caches")
        from apps.analytics.tasks import warm_caches
        warm_caches()

        self.stdout.write("→ smoke check")
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()

        elapsed = time.monotonic() - t0
        ok = elapsed <= self.RTO_TARGET_SECONDS
        self.stdout.write(
            self.style.SUCCESS(f"DR drill: {elapsed:.0f}s (target {self.RTO_TARGET_SECONDS}s) — {'PASS' if ok else 'FAIL'}")
        )
        if not ok:
            raise SystemExit(1)
