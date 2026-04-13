"""Prometheus business-metrics exporter. PLAN §11.11.

Exposed at /metrics (ALB-only, not via CDN). Scraped by the Grafana Cloud /
self-hosted Prometheus agent. Infra metrics come from CloudWatch; this file
covers the *business* gauges CloudWatch can't see.
"""
from __future__ import annotations

from django.http import HttpResponse
from prometheus_client import (
    CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST,
)

from apps.nasa_ingest.circuit import state as circuit_state
from apps.analytics.rollups import current_dau, redis_hit_rate, nasa_quota_used

_registry = CollectorRegistry()

G_DAU        = Gauge("nse_dau", "Distinct players active in the last 24h", registry=_registry)
G_HIT_RATE   = Gauge("nse_redis_hit_rate", "Redis cache hit rate (0-1)", registry=_registry)
G_QUOTA      = Gauge("nse_nasa_quota_used", "NASA API calls used in the current hour", registry=_registry)
G_CIRCUIT    = Gauge("nse_nasa_circuit_open", "1 if NASA circuit breaker is open", registry=_registry)


def metrics_view(_request):
    G_DAU.set(current_dau())
    G_HIT_RATE.set(redis_hit_rate())
    G_QUOTA.set(nasa_quota_used())
    G_CIRCUIT.set(1 if circuit_state() == "open" else 0)
    return HttpResponse(generate_latest(_registry), content_type=CONTENT_TYPE_LATEST)
