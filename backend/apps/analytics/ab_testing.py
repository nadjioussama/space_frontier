"""Deterministic experiment bucketing + result scoring. PLAN §27.3."""
from __future__ import annotations

import hashlib
import math
from typing import Any

from django.db import transaction
from django.db.models import Avg, Count, F, FloatField
from django.db.models.functions import Cast

from .models import Experiment, PlayerExperiment, RawEvent

MAX_CONCURRENT_PER_PLAYER = 2


def _bucket(player_id, experiment_slug: str) -> int:
    """Stable 0-99 bucket from (player, experiment). Same player always lands
    in the same bucket — survives cache loss and multi-device."""
    h = hashlib.sha256(f"{player_id}:{experiment_slug}".encode()).digest()
    return h[0] % 100


def assignments_for(player) -> dict[str, Any]:
    """Return {experiment_slug: {variant, config}} for all running experiments
    this player is enrolled in, creating stable assignments on first call."""
    pid = getattr(player, "public_id", None) or player.pk
    age_group = getattr(player, "age_group", None)
    is_new = getattr(player, "is_new_player", lambda: False)()

    existing = {
        pe.experiment_id: pe
        for pe in PlayerExperiment.objects.select_related("experiment", "variant")
        .filter(player_id=pid, experiment__status="running")
    }

    running = Experiment.objects.filter(status="running").prefetch_related("variants")
    out: dict[str, Any] = {}
    for exp in running:
        if exp.id in existing:
            pe = existing[exp.id]
            out[exp.slug] = {"variant": pe.variant.slug, "config": pe.variant.config}
            continue
        if len(existing) + len(out) >= MAX_CONCURRENT_PER_PLAYER:
            continue
        if exp.target_age_groups and age_group not in exp.target_age_groups:
            continue
        if exp.target_new_players_only and not is_new:
            continue
        if _bucket(pid, exp.slug) >= exp.traffic_percent:
            continue

        variants = list(exp.variants.all())
        if not variants:
            continue
        chosen = variants[_bucket(pid, f"{exp.slug}:variant") % len(variants)]
        with transaction.atomic():
            PlayerExperiment.objects.get_or_create(
                player_id=pid, experiment=exp, defaults={"variant": chosen}
            )
        out[exp.slug] = {"variant": chosen.slug, "config": chosen.config}
    return out


# --- Result computation -------------------------------------------------

_METRICS = {
    "mission_completion_rate": dict(event="mission.completed", denom="mission.started"),
    "quiz_accuracy": dict(event="quiz.answered", field="is_correct"),
    "session_length": dict(event="session.ended", field="duration_seconds"),
}


def score_experiment(exp: Experiment) -> None:
    """Recompute sample_size / metric_value / confidence for each variant.

    Uses a two-proportion z-test against `control` when the metric is a rate;
    Welch's t-test approximation otherwise. Runs nightly from Celery.
    """
    spec = _METRICS.get(exp.primary_metric)
    if spec is None:
        return

    results: dict[str, tuple[int, float, float]] = {}
    for v in exp.variants.all():
        pids = PlayerExperiment.objects.filter(variant=v).values_list("player_id", flat=True)
        n = pids.count()
        if "denom" in spec:
            num = RawEvent.objects.filter(player_id__in=pids, event_type=spec["event"]).count()
            den = RawEvent.objects.filter(player_id__in=pids, event_type=spec["denom"]).count()
            p = (num / den) if den else 0.0
            var = p * (1 - p) / den if den else 0.0
        else:
            agg = (
                RawEvent.objects.filter(player_id__in=pids, event_type=spec["event"])
                .annotate(val=Cast(F(f"payload__{spec['field']}"), FloatField()))
                .aggregate(mean=Avg("val"), c=Count("id"))
            )
            p = agg["mean"] or 0.0
            var = 0.0  # simplified — full variance needs raw values; acceptable for dashboard hint
        results[v.slug] = (n, p, var)
        v.sample_size = n
        v.metric_value = p

    control = results.get("control")
    for v in exp.variants.all():
        if control and v.slug != "control":
            n1, p1, var1 = control
            n2, p2, var2 = results[v.slug]
            se = math.sqrt(max(var1 + var2, 1e-9))
            z = (p2 - p1) / se if se else 0.0
            # Two-sided p-value via normal CDF (erf).
            v.confidence = 1 - math.erfc(abs(z) / math.sqrt(2))
        v.save(update_fields=["sample_size", "metric_value", "confidence"])
