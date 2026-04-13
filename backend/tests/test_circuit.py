"""Circuit breaker state machine. PLAN §6.7."""
from __future__ import annotations

import time

from django.core.cache import cache
from django.test import SimpleTestCase

from apps.nasa_ingest import circuit


class CircuitBreakerTests(SimpleTestCase):
    def setUp(self) -> None:
        cache.delete_many([circuit._STATE_KEY, circuit._FAIL_KEY, circuit._OPENED_AT_KEY])

    def tearDown(self) -> None:
        cache.delete_many([circuit._STATE_KEY, circuit._FAIL_KEY, circuit._OPENED_AT_KEY])

    def test_closed_passes_through(self):
        self.assertEqual(circuit.state(), "CLOSED")
        self.assertEqual(circuit.call(lambda: "ok"), "ok")
        self.assertEqual(circuit.state(), "CLOSED")

    def test_opens_after_threshold_failures(self):
        boom = RuntimeError("nasa down")
        for i in range(circuit.FAILURE_THRESHOLD - 1):
            with self.assertRaises(RuntimeError):
                circuit.call(lambda: (_ for _ in ()).throw(boom))
            self.assertEqual(circuit.state(), "CLOSED", f"stayed closed after {i + 1} fails")
        with self.assertRaises(RuntimeError):
            circuit.call(lambda: (_ for _ in ()).throw(boom))
        self.assertEqual(circuit.state(), "OPEN")

    def test_open_short_circuits_without_calling(self):
        cache.set(circuit._STATE_KEY, "OPEN", timeout=None)
        cache.set(circuit._OPENED_AT_KEY, time.time(), timeout=None)
        called = []
        with self.assertRaises(circuit.CircuitOpenError):
            circuit.call(lambda: called.append(1))
        self.assertEqual(called, [], "underlying fn must not be invoked while OPEN")

    def test_half_open_probe_success_closes(self):
        cache.set(circuit._STATE_KEY, "OPEN", timeout=None)
        cache.set(circuit._OPENED_AT_KEY, time.time() - circuit.RECOVERY_TIMEOUT - 1, timeout=None)
        result = circuit.call(lambda: "recovered")
        self.assertEqual(result, "recovered")
        self.assertEqual(circuit.state(), "CLOSED")

    def test_half_open_probe_failure_reopens(self):
        cache.set(circuit._STATE_KEY, "OPEN", timeout=None)
        cache.set(circuit._OPENED_AT_KEY, time.time() - circuit.RECOVERY_TIMEOUT - 1, timeout=None)
        cache.set(circuit._FAIL_KEY, circuit.FAILURE_THRESHOLD, timeout=3600)
        with self.assertRaises(RuntimeError):
            circuit.call(lambda: (_ for _ in ()).throw(RuntimeError("still down")))
        self.assertEqual(circuit.state(), "OPEN")

    def test_success_resets_failure_count(self):
        cache.set(circuit._FAIL_KEY, 3, timeout=3600)
        circuit.call(lambda: "ok")
        self.assertIsNone(cache.get(circuit._FAIL_KEY))
