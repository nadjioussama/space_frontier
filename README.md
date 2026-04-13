# NASA Space Explorer

An educational space exploration game built on NASA Open APIs. Transforms real
space data into missions, puzzles, and interactive play for ages 6-14.

---

## Table of contents

- [Project structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick start (local dev)](#quick-start-local-dev)
- [Running tests](#running-tests)
- [API endpoints](#api-endpoints)
- [Celery beat schedule](#celery-beat-schedule)
- [Deployment](#deployment)
- [Architecture highlights](#architecture-highlights)
- [Documentation index](#documentation-index)

---

## Project structure

```
.
├── backend/                  Django 5 + DRF + Celery
│   ├── config/               Settings (base/dev/prod/test), Celery, URL routing, Prometheus metrics
│   ├── apps/
│   │   ├── users/            Player, ParentAccount, COPPA consent, display-name moderation
│   │   ├── nasa_ingest/      NASA API clients, transformers, ingestion tasks (APOD, Mars, NEO, EPIC, Exoplanets)
│   │   ├── games/            Mission, Quiz, Jigsaw models + generators (incl. cross-API)
│   │   ├── progress/         Attempts, DDA engine, leaderboard, constellations, streaks, achievements
│   │   ├── analytics/        Event pipeline (Redis Streams -> Postgres), rollups, A/B testing, alerts
│   │   └── media_proxy/      Placeholder for Phase 4 S3 image proxy
│   ├── api/v1/               REST API endpoint routing
│   ├── tests/                Backend test suite (pytest)
│   ├── Dockerfile            Production image (Python 3.12 + gunicorn)
│   └── requirements.txt      Python dependencies
│
├── frontend/                 Next.js 14 + TypeScript + Tailwind + Framer Motion
│   ├── src/
│   │   ├── app/              Pages (home, missions list, mission detail)
│   │   ├── components/       SpaceMap, MissionViewport, Quiz, Jigsaw, Leaderboard, Constellation, PlayerHud
│   │   ├── lib/              API client, TanStack Query hooks, offline store, sound, analytics, seed data
│   │   ├── store/            Zustand player state (XP, rank, DDA level, sound)
│   │   └── __tests__/        Jest test suite
│   ├── public/               Static assets and seed data
│   ├── Dockerfile            Dev container (Node 20)
│   └── package.json          Dependencies and scripts
│
├── infra/                    Terraform (AWS) — see infra/README.md
│   ├── modules/              network, ecs, rds, elasticache, s3, cloudfront, iam, monitoring
│   ├── environments/         staging/ and prod/ with per-env tfvars
│   ├── global/               Route53 hosted zone
│   └── tests/                Terraform validation and security checks
│
├── tests/                    Integration tests (Docker Compose, env validation, Dockerfiles, CI workflows)
├── .github/workflows/        CI (lint + test + validate) and CD (build -> staging -> prod with auto-rollback)
├── docker-compose.yml        Local dev stack: Postgres, Redis, Django, Celery worker/beat, Next.js
├── .env.example              Environment variable template
└── PLAN.md                   Full project plan (architecture, design, phases)
```

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Docker + Docker Compose v2** | Required for local dev |
| **NASA API key** | Free at https://api.nasa.gov/ (`DEMO_KEY` works but is rate-limited) |
| **Node 20+** | Only if running frontend outside Docker |
| **Python 3.12+** | Only if running backend outside Docker |

---

## Quick start (local dev)

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env -> set NASA_API_KEY (everything else has working defaults)

# 2. Start all services
docker compose up --build

# 3. First-time database setup (in a separate terminal)
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser

# 4. Seed content from NASA APIs
docker compose exec web python manage.py ingest_apod
docker compose exec web python manage.py ingest_mars
docker compose exec web python manage.py ingest_neows
docker compose exec web python manage.py ingest_epic
docker compose exec web python manage.py ingest_exoplanets
docker compose exec web python manage.py seed_constellations
docker compose exec web python manage.py generate_cross_api
```

### Running without Docker

```bash
# Backend (requires Postgres + Redis running locally)
cd backend
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=config.settings.dev
export POSTGRES_HOST=localhost
export REDIS_URL=redis://localhost:6379/0
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend
npm install
npm run dev
```

### Local URLs

| URL | What |
|-----|------|
| http://localhost:3000 | Game frontend |
| http://localhost:3000/missions | Missions browser |
| http://localhost:8000/admin/ | Django admin panel |
| http://localhost:8000/api/v1/nasa/today/ | Today's APOD + mission |
| http://localhost:8000/health/ | Health check + circuit breaker status |
| http://localhost:8000/metrics | Prometheus business metrics |

---

## Running tests

### Backend (Django / pytest)

```bash
# Inside Docker
docker compose exec web pytest

# Locally (requires Postgres + Redis)
cd backend
DJANGO_SETTINGS_MODULE=config.settings.test pytest
```

### Frontend (Jest)

```bash
cd frontend
npm install
npm test

# Watch mode
npm run test:watch

# Coverage report
npm run test:coverage
```

### Infrastructure

```bash
# Terraform syntax validation
bash infra/tests/test_terraform.sh

# Naming conventions
bash infra/tests/test_naming.sh

# Security checks (SG rules, IAM policies, encryption)
bash infra/tests/test_security.sh

# Integration tests (validates Docker Compose, Dockerfiles, env, CI workflows)
python -m pytest tests/
```

---

## API endpoints

All API routes are under `/api/v1/` unless noted.

### Game content

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/nasa/today/` | GET | Today's APOD + mission slug |
| `/api/v1/planets/` | GET | Space Map planet nodes |
| `/api/v1/planets/<slug>/` | GET | Planet detail with missions |
| `/api/v1/missions/<slug>/` | GET | Full mission (quiz, jigsaw, content) |
| `/api/v1/missions/<slug>/attempt/` | POST | Submit answers, get XP + DDA update |

### Authentication (JWT)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/token/` | POST | JWT login |
| `/api/v1/auth/token/refresh/` | POST | JWT refresh |

### Users and COPPA

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/users/me/` | GET | Player profile |
| `/api/v1/users/name/` | POST | Request display-name change |
| `/api/v1/users/parent/register/` | POST | Register parent account |
| `/api/v1/users/parent/verify/` | POST | Verify parent email |
| `/api/v1/users/consent/grant/` | POST | Grant COPPA parental consent |

### Progress and leaderboard

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/progress/me/` | GET | Player progress snapshot (auth) |
| `/api/v1/progress/dda/` | GET | DDA level + content config |
| `/api/v1/progress/constellations/` | GET | Skill tree with earned stars |
| `/api/v1/leaderboard/weekly/` | GET | Weekly top-50 rankings |
| `/api/v1/leaderboard/planet/<slug>/` | GET | Per-planet rankings |

### Analytics and experiments

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/events/` | POST | Analytics event ingest |
| `/api/v1/experiments/` | GET | A/B experiment assignments |

### System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health/` | GET | Health check + circuit breaker status |
| `/metrics` | GET | Prometheus business metrics (DAU, cache hit rate, NASA quota) |

---

## Celery beat schedule

Automated tasks managed by Celery Beat. Configured in `backend/config/celery.py`.

| Task | Schedule | Description |
|------|----------|-------------|
| APOD ingest | Daily 05:00 UTC | Fetch Astronomy Picture of the Day |
| Mars ingest | Daily 06:00 UTC | Fetch latest Mars Rover photos |
| NEO ingest | Hourly | Fetch Near Earth Objects |
| EPIC ingest | Every 6h | Fetch Earth images |
| Exoplanet ingest | Weekly (Mon 03:00) | Fetch confirmed exoplanets |
| Leaderboard reset | Weekly (Mon 00:00) | Reset weekly leaderboard |
| Cross-API missions | Weekly (Mon 04:00) | Generate multi-source missions |
| Cache warming | Every 30 min | Pre-warm today + planets cache |
| Analytics drain | Every minute | Redis Stream -> Postgres |
| Rollup refresh | Every 15 min | Refresh materialized views |
| Partition management | Daily 01:00 | Create/drop date partitions |
| Anomaly checks | Every 15 min (offset) | Run alert rules, post to Slack |
| Experiment scoring | Daily 02:00 | Recompute A/B test metrics |

---

## Deployment

### Overview

The deploy pipeline (`.github/workflows/deploy.yml`) runs on every merge to `main`:

1. **Build** Docker images and push to AWS ECR
2. **Staging** — Terraform apply to staging environment
3. **Integration test** — health check on staging
4. **Manual approval** — GitHub environment protection rule
5. **Production** — Terraform apply to production
6. **Smoke test** — ECS service stability + health check
7. **Auto-rollback** on smoke test failure (reverts all 4 services)

### Infrastructure setup (one-time)

Full details in [`infra/README.md`](infra/README.md).

1. **Bootstrap Terraform state** — create S3 bucket `nse-tfstate` and DynamoDB table `nse-tflock`
2. **Create Route53 hosted zone** — `cd infra/global/route53 && terraform init && terraform apply`
3. **Create AWS Secrets Manager secrets** — `DJANGO_SECRET_KEY`, `NASA_API_KEY`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `SENTRY_DSN`, `SLACK_WEBHOOK_URL`
4. **Set up Cloudflare** — see [Cloudflare setup](infra/README.md#cloudflare-setup) in infra docs
5. **Configure GitHub Actions secrets** — see [GitHub Actions secrets](infra/README.md#github-actions-secrets) in infra docs

### Deploy manually (staging)

```bash
cd infra/environments/staging
terraform init
terraform plan  -var image_tag=$(git rev-parse --short HEAD) -var-file=terraform.tfvars
terraform apply -var image_tag=$(git rev-parse --short HEAD) -var-file=terraform.tfvars
```

### Staging vs production

| Setting | Staging | Production |
|---------|---------|------------|
| RDS instance | db.t3.micro | db.t3.medium |
| RDS multi-AZ | No | Yes |
| RDS read replica | No | Yes |
| Redis node | cache.t3.micro | cache.t3.small |
| ECS web min/max | 1/3 | 2/20 |
| Monthly budget | $120 | $600 |

### Environment variables

See [`.env.example`](.env.example) for the full list. Production-only variables:

| Variable | Description |
|----------|-------------|
| `AWS_REGION` | AWS region for S3 storage |
| `MEDIA_BUCKET` | S3 bucket for media assets |
| `POSTGRES_REPLICA_HOST` | RDS read replica endpoint (analytics routing) |
| `SLACK_WEBHOOK_URL` | Slack webhook for anomaly alerts |
| `SENTRY_DSN` | Sentry error tracking DSN |
| `CLOUDFLARE_ZONE_ID` | Cloudflare zone ID for CDN |
| `CLOUDFLARE_API_TOKEN` | Cloudflare API token |

---

## Architecture highlights

- **Offline-first frontend**: network -> IndexedDB -> bundled seed fallback chain
- **NASA quota management**: hourly counter in Redis with soft-warn at 70%, hard-stop at 95%
- **Circuit breaker**: wraps all NASA API calls; auto-opens on repeated failures
- **Analytics pipeline**: Redis Streams -> partitioned Postgres table -> materialized view rollups
- **Dynamic Difficulty Adjustment (DDA)**: per-player, per-topic difficulty tracked in Redis
- **Leaderboard**: Redis sorted sets with weekly reset via Celery beat
- **A/B testing**: deterministic SHA256 bucketing, z-test scoring, age/new-player targeting
- **COPPA compliance**: parental consent flow, display-name moderation queue, PII scrubbing
- **Prometheus metrics**: DAU, cache hit rate, NASA API quota, circuit breaker state

---

## Documentation index

| Document | Description |
|----------|-------------|
| [`README.md`](README.md) | This file — project guide, setup, and reference |
| [`infra/README.md`](infra/README.md) | Infrastructure setup, Terraform modules, deploy, disaster recovery |
| [`PLAN.md`](PLAN.md) | Full project plan — architecture, game design, phases, and specifications |
| [`.env.example`](.env.example) | Environment variable template with all required and optional vars |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | CI pipeline — lint, test, validate on every PR and push to main |
| [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) | CD pipeline — build, staging, approval gate, production, auto-rollback |
| [`docker-compose.yml`](docker-compose.yml) | Local dev stack configuration |
