# NASA Space Explorer — Phases 1–6

An educational space exploration game built on NASA Open APIs. Transforms real
space data into missions, puzzles, and interactive play for ages 6–14.

## What's here

```
backend/         Django + DRF + Celery
  apps/
    nasa_ingest/ — NASA API clients, transformers, ingestion tasks (APOD, Mars, NEO, EPIC, Exoplanets)
    games/       — Mission, Quiz, Jigsaw models + generators (incl. cross-API)
    progress/    — Attempts, DDA engine, leaderboard, constellations, streaks
    users/       — Player, ParentAccount, COPPA consent, display-name moderation
    media_proxy/ — Content-addressed media pipeline

frontend/        Next.js + TS + PixiJS + Tailwind + Framer Motion + Howler.js
  components/
    SpaceMap      — Planet navigation with per-planet accent colors
    MissionViewport — Game shell (jigsaw + quiz) with DDA feedback
    Leaderboard   — Weekly Redis sorted-set rankings
    Constellation — SVG skill-tree visualization
    AgeGroupSelector — UI density adjustment (6-8 / 9-11 / 12-14)
    SoundToggle   — Audio control

docker-compose.yml
```

## Quick start

```bash
# 1. Add your NASA API key (DEMO_KEY works, but rate-limited)
cp .env.example .env
# edit NASA_API_KEY

# 2. Bring everything up
docker compose up --build

# 3. One-time setup
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py ingest_apod
docker compose exec web python manage.py seed_constellations
docker compose exec web python manage.py generate_cross_api

# 4. Visit
#   http://localhost:3000                         game
#   http://localhost:3000/missions                all missions
#   http://localhost:8000/admin/                  admin panel
#   http://localhost:8000/api/v1/nasa/today/      APOD API
#   http://localhost:8000/api/v1/leaderboard/weekly/  leaderboard
#   http://localhost:8000/api/v1/progress/constellations/  skill tree
```

## Phase summary

| Phase | Status | What it adds |
|-------|--------|-------------|
| **0** Foundations | Done | Monorepo, Docker, CI skeleton |
| **1** Backend skeleton | Done | APOD ingest → DRF API → Redis cache, circuit breaker, quota counter |
| **2** Frontend skeleton | Done | Next.js + PixiJS jigsaw + quiz, IndexedDB offline, seed bundle |
| **3** Identity & safety | Done | Player/ParentAccount, COPPA consent flow, display-name moderation, audit log, Sentry PII scrubbing |
| **4** Content catalog | Done | Mars Rover, NeoWs, EPIC, Exoplanet clients + transformers + quiz generators |
| **5** Progression & social | Done | Knowledge Constellation skill tree, DDA engine (Redis), leaderboards (sorted sets), daily streaks, cross-API missions |
| **6** Look & feel | Done | Full theme tokens (§16), framer-motion animations, Howler.js sound manager, age-adaptive UI density, glassmorphism panels |

## Key API endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/nasa/today/` | GET | Today's APOD + mission slug |
| `/api/v1/planets/` | GET | Space Map nodes |
| `/api/v1/missions/<slug>/` | GET | Full mission detail (quiz, jigsaw, content) |
| `/api/v1/missions/<slug>/attempt/` | POST | Submit answers, get XP + DDA update |
| `/api/v1/progress/me/` | GET | Full progress snapshot (auth required) |
| `/api/v1/progress/dda/` | GET | Current DDA level + content config |
| `/api/v1/progress/constellations/` | GET | Skill tree with earned stars |
| `/api/v1/leaderboard/weekly/` | GET | Weekly top-50 rankings |
| `/api/v1/leaderboard/planet/<slug>/` | GET | Per-planet rankings |

## What is intentionally NOT here

See `PLAN.md` Phases 7–8: production Terraform (ECS, RDS, CloudFront), PgBouncer,
analytics event pipeline, A/B testing, Three.js 3D, and remaining NASA APIs
(DONKI, EONET, ISS/TLE, Image Library, Insight Weather, TechTransfer, SSD/CNEOS).
