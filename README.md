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
- [Building the image](#building-the-image)
- [Makefile reference](#makefile-reference)
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

All test commands come in two flavours: **via Docker Compose** (no local toolchain
needed beyond Docker) and **locally** (faster feedback loop, requires the relevant
runtime installed). The Makefile wraps every variant — see the
[Makefile reference](#makefile-reference) for the full list.

---

### Backend (Django / pytest)

```bash
# ── via Docker Compose ────────────────────────────────────────
# Basic run
docker compose exec web pytest

# With terminal + HTML coverage report (written to backend/htmlcov/)
docker compose exec web pytest --cov=. --cov-report=term-missing --cov-report=html

# ── locally (requires Postgres + Redis running) ───────────────
cd backend
DJANGO_SETTINGS_MODULE=config.settings.test pytest
```

**With make:**

```bash
make test-backend             # basic run (Compose)
make test-backend-coverage    # with coverage report (Compose)
make test-backend-local       # locally
```

---

### Frontend (Jest + TypeScript)

```bash
# ── via Docker Compose ────────────────────────────────────────
# CI mode (runs once, no watch)
docker compose exec frontend npm test -- --watchAll=false

# Watch mode (re-runs on file changes)
docker compose exec frontend npm run test:watch

# Coverage report
docker compose exec frontend npm run test:coverage

# TypeScript type-check (no test runner, just tsc)
docker compose exec frontend npm run typecheck

# ── locally (requires npm install) ────────────────────────────
cd frontend
npm install
npm test -- --watchAll=false   # CI mode
npm run test:watch             # watch mode
npm run test:coverage          # coverage
npm run typecheck              # type-check only
```

**With make:**

```bash
make test-frontend             # CI mode (Compose)
make test-frontend-watch       # watch mode (Compose)
make test-frontend-coverage    # with coverage (Compose)
make test-frontend-local       # locally
make typecheck                 # TypeScript check (Compose)
make typecheck-local           # TypeScript check locally
```

---

### Integration tests

Validates the Docker Compose setup, Dockerfiles, env file, and CI workflow files.
Runs against the host — no services need to be up.

```bash
python -m pytest tests/
```

**With make:**

```bash
make test-integration
```

---

### Infrastructure (Terraform)

```bash
# Syntax validation
bash infra/tests/test_terraform.sh

# Naming conventions
bash infra/tests/test_naming.sh

# Security checks (SG rules, IAM policies, encryption)
bash infra/tests/test_security.sh
```

**With make:**

```bash
make test-infra     # runs all three scripts in sequence
```

---

### Run everything at once

```bash
# Backend + frontend + integration (skips infra — requires AWS creds)
make test-all

# All four suites including infra
make test-all test-infra
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

## Building the image

The repo ships with a `Dockerfile` that produces a **single self-contained image**
running Nginx, Gunicorn, Next.js, and two Celery processes via supervisord.
It still requires an external **PostgreSQL** and **Redis** instance — supply these
via environment variables (see `.env.example`).

> **Before building**, add `output: 'standalone'` to `frontend/next.config.js`
> so Next.js emits a self-contained `server.js`:
>
> ```js
> module.exports = {
>   output: 'standalone',   // ← required for the single-image build
>   reactStrictMode: true,
>   // ...
> };
> ```

---

### Option A — manual Docker build

```bash
# 1. Build (swap in your real API host)
docker build \
  --build-arg NEXT_PUBLIC_API_BASE=http://localhost \
  -t space-frontier:latest \
  .

# 2. Run (reads credentials from .env; map port 80)
docker run --rm -d \
  --name space-frontier-app \
  --env-file .env \
  -p 80:80 \
  space-frontier:latest

# App is now at http://localhost
# Admin panel : http://localhost/admin/
# API         : http://localhost/api/v1/
```

To stop:

```bash
docker stop space-frontier-app
```

---

### Option B — Docker Compose (full dev stack, recommended locally)

`docker-compose.yml` starts Postgres and Redis alongside the app services — no
external dependencies needed.

```bash
# 1. Copy and edit env
cp .env.example .env

# 2. Start everything (builds images on first run)
docker compose up --build -d

# 3. First-time setup
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser

# 4. Seed NASA content
docker compose exec web python manage.py ingest_apod
docker compose exec web python manage.py ingest_mars
docker compose exec web python manage.py seed_constellations
# (see Quick start for the full seed sequence)
```

| URL | What |
|-----|------|
| http://localhost:3000 | Game frontend |
| http://localhost:8000/admin/ | Django admin |
| http://localhost:8000/api/v1/ | REST API |
| http://localhost:8000/health/ | Health check |

Stop and clean up:

```bash
docker compose down        # stops containers, keeps volumes
docker compose down -v     # stops containers AND deletes the database volume
```

---

### Option C — Makefile (wraps both workflows above)

See the [Makefile reference](#makefile-reference) below for all available targets.

```bash
# Full dev stack (Compose)
make up           # build + start everything
make migrate      # run migrations
make seed         # ingest all NASA data
make logs         # tail all logs

# Single image (Docker only)
make build        # build space-frontier:latest
make run          # docker run with .env
make stop         # docker stop
```

Override defaults at call time:

```bash
make build IMAGE_TAG=v1.2.3 API_BASE=https://api.mysite.com
make push  IMAGE_NAME=ghcr.io/myorg/space-frontier IMAGE_TAG=v1.2.3
```

---

## Makefile reference

Run `make help` to print this table at any time.

| Target | Description |
|--------|-------------|
| **Single-image (Docker)** | |
| `make build` | Build `space-frontier:latest` (pass `IMAGE_TAG=` and `API_BASE=` to override) |
| `make run` | `docker run` the image on port 80, reading `.env` |
| `make stop` | Stop the running container |
| `make push` | Push to a registry (set `IMAGE_NAME=registry/image`) |
| **Dev stack (Compose)** | |
| `make up` | Build and start all services in the background |
| `make up-fg` | Same but in the foreground (streams all logs) |
| `make down` | Stop and remove containers (keeps volumes) |
| `make down-v` | Stop containers **and delete the database volume** |
| `make restart` | Restart all services |
| `make logs` | Follow logs for all services |
| `make logs-web` | Follow logs for the Django service only |
| **Database** | |
| `make migrate` | Run Django migrations |
| `make makemigrations` | Create new migration files |
| `make superuser` | Create a Django superuser (interactive) |
| `make seed` | Run all NASA ingest + seed commands |
| **Tests** | |
| `make test` | Run backend + frontend tests (Compose) |
| `make test-all` | Run backend + frontend + integration tests |
| `make test-backend` | Backend pytest (Compose) |
| `make test-backend-coverage` | Backend pytest with coverage report (Compose) |
| `make test-backend-local` | Backend pytest locally (needs Postgres + Redis) |
| `make test-frontend` | Frontend Jest in CI mode (Compose) |
| `make test-frontend-watch` | Frontend Jest in watch mode (Compose) |
| `make test-frontend-coverage` | Frontend Jest with coverage report (Compose) |
| `make test-frontend-local` | Frontend Jest locally (needs npm install) |
| `make typecheck` | TypeScript type-check (Compose) |
| `make typecheck-local` | TypeScript type-check locally |
| `make test-integration` | Integration tests (Compose, Dockerfiles, env, CI) |
| `make test-infra` | Terraform validation + security checks |
| **Utilities** | |
| `make shell` | Open a Django shell |
| `make bash-web` | Open a bash shell in the web container |
| `make bash-frontend` | Open a shell in the frontend container |
| `make lint` | Run ruff (backend) + eslint (frontend) |
| `make collectstatic` | Collect Django static files |
| `make clean` | Remove stopped containers and dangling images |
| `make clean-all` | Remove **all** unused Docker resources (⚠ destructive) |

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
| [`Makefile`](Makefile) | Build, run, test, and utility shortcuts |
| [`infra/README.md`](infra/README.md) | Infrastructure setup, Terraform modules, deploy, disaster recovery |
| [`PLAN.md`](PLAN.md) | Full project plan — architecture, game design, phases, and specifications |
| [`.env.example`](.env.example) | Environment variable template with all required and optional vars |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | CI pipeline — lint, test, validate on every PR and push to main |
| [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) | CD pipeline — build, staging, approval gate, production, auto-rollback |
| [`docker-compose.yml`](docker-compose.yml) | Local dev stack configuration |