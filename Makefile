# =============================================================================
# Space Frontier — Makefile
#
# Usage:
#   make help              List all targets
#
# Single-image (Docker only — needs external Postgres + Redis):
#   make build             Build the single image
#   make run               Run the single image (reads .env)
#   make stop              Stop the running container
#
# Full dev stack (Docker Compose — includes Postgres + Redis):
#   make up                Start all services
#   make down              Stop and remove containers
#   make logs              Follow logs for all services
#
# Database:
#   make migrate           Run Django migrations
#   make superuser         Create a Django superuser
#   make seed              Ingest all NASA data + seed content
#
# Tests:
#   make test                    Run backend + frontend tests (via Compose)
#   make test-backend            Backend pytest (via Compose)
#   make test-backend-local      Backend pytest locally (needs Postgres + Redis)
#   make test-frontend           Frontend Jest in CI mode (via Compose)
#   make test-frontend-watch     Frontend Jest in watch mode
#   make test-frontend-local     Frontend Jest locally (needs npm install)
#   make typecheck               TypeScript type-check (via Compose)
#   make test-integration        Integration tests (Dockerfiles, env, CI)
#   make test-infra              Terraform validation + security checks
#   make test-all                Everything above (Backend + Frontend + Integration + Infra)
#
# Utilities:
#   make shell             Open a Django shell
#   make lint              Run backend (ruff) and frontend (eslint) linters
#   make clean             Remove stopped containers and dangling images
# =============================================================================

# ── Config ────────────────────────────────────────────────────────────────────
IMAGE_NAME   ?= space-frontier
IMAGE_TAG    ?= latest
CONTAINER    ?= space-frontier-app
API_BASE     ?= http://localhost
ENV_FILE     ?= .env
COMPOSE      := docker compose

.DEFAULT_GOAL := help

# ── Helpers ───────────────────────────────────────────────────────────────────
.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ── Single-image targets ──────────────────────────────────────────────────────
.PHONY: build
build: ## Build the single-image Docker image
	docker build \
		--build-arg NEXT_PUBLIC_API_BASE=$(API_BASE) \
		-t $(IMAGE_NAME):$(IMAGE_TAG) \
		.

.PHONY: run
run: ## Run the single image (requires external Postgres + Redis via .env)
	docker run --rm -d \
		--name $(CONTAINER) \
		--env-file $(ENV_FILE) \
		-p 80:80 \
		$(IMAGE_NAME):$(IMAGE_TAG)
	@echo "→ App running at http://localhost"

.PHONY: stop
stop: ## Stop the running single-image container
	docker stop $(CONTAINER) 2>/dev/null || true

.PHONY: push
push: ## Push image to a registry (set IMAGE_NAME=registry/image)
	docker push $(IMAGE_NAME):$(IMAGE_TAG)

# ── Docker Compose targets ────────────────────────────────────────────────────
.PHONY: up
up: ## Start the full dev stack (Postgres, Redis, Django, Celery, Next.js)
	$(COMPOSE) up --build -d
	@echo "→ Frontend : http://localhost:3000"
	@echo "→ API      : http://localhost:8000"
	@echo "→ Admin    : http://localhost:8000/admin/"

.PHONY: up-fg
up-fg: ## Start the full dev stack in the foreground (shows logs)
	$(COMPOSE) up --build

.PHONY: down
down: ## Stop and remove all Compose containers
	$(COMPOSE) down

.PHONY: down-v
down-v: ## Stop containers and delete volumes (WARNING: deletes database)
	$(COMPOSE) down -v

.PHONY: restart
restart: ## Restart all Compose services
	$(COMPOSE) restart

.PHONY: logs
logs: ## Follow logs for all services
	$(COMPOSE) logs -f

.PHONY: logs-web
logs-web: ## Follow logs for the Django web service only
	$(COMPOSE) logs -f web

# ── Database ──────────────────────────────────────────────────────────────────
.PHONY: migrate
migrate: ## Run Django migrations (via Compose)
	$(COMPOSE) exec web python manage.py migrate --noinput

.PHONY: makemigrations
makemigrations: ## Create new Django migrations (via Compose)
	$(COMPOSE) exec web python manage.py makemigrations

.PHONY: superuser
superuser: ## Create a Django superuser (interactive)
	$(COMPOSE) exec web python manage.py createsuperuser

.PHONY: seed
seed: ## Ingest all NASA data and seed game content
	$(COMPOSE) exec web python manage.py ingest_apod
	$(COMPOSE) exec web python manage.py ingest_mars
	$(COMPOSE) exec web python manage.py ingest_neows
	$(COMPOSE) exec web python manage.py ingest_epic
	$(COMPOSE) exec web python manage.py ingest_exoplanets
	$(COMPOSE) exec web python manage.py seed_constellations
	$(COMPOSE) exec web python manage.py generate_cross_api

# ── Tests ─────────────────────────────────────────────────────────────────────
.PHONY: test
test: test-backend test-frontend ## Run backend + frontend tests

# -- Backend ------------------------------------------------------------------
.PHONY: test-backend
test-backend: ## Run backend pytest suite with coverage (via Compose)
	$(COMPOSE) exec web pytest --cov

.PHONY: test-backend-local
test-backend-local: ## Run backend tests locally (requires local Postgres + Redis)
	cd backend && DJANGO_SETTINGS_MODULE=config.settings.test pytest --cov

# -- Frontend -----------------------------------------------------------------
.PHONY: test-frontend
test-frontend: ## Run frontend Jest tests with coverage (via Compose)
	$(COMPOSE) exec frontend npm test -- --coverage --watchAll=false

.PHONY: test-frontend-watch
test-frontend-watch: ## Run frontend Jest tests in watch mode (via Compose)
	$(COMPOSE) exec frontend npm run test:watch

.PHONY: test-frontend-local
test-frontend-local: ## Run frontend Jest tests locally (requires npm install)
	cd frontend && npm test -- --coverage --watchAll=false

.PHONY: typecheck
typecheck: ## Run TypeScript type-checking on the frontend (via Compose)
	$(COMPOSE) exec frontend npm run typecheck

.PHONY: typecheck-local
typecheck-local: ## Run TypeScript type-checking locally
	cd frontend && npm run typecheck

# -- Integration / infra ------------------------------------------------------
.PHONY: test-infra
test-infra: ## Run Terraform validation + security checks
	bash infra/tests/test_terraform.sh
	bash infra/tests/test_naming.sh
	bash infra/tests/test_security.sh

.PHONY: test-integration
test-integration: ## Run integration tests with coverage (Compose, Dockerfiles, env, CI workflows)
	cd tests && python3 -m pytest --cov=.

.PHONY: test-all
test-all: test-backend test-frontend test-integration test-infra ## Run ALL tests + coverage + infra validation
	@echo ""
	@echo "======================================================================"
	@echo "                      PROJECT STATUS: ALL GREEN                       "
	@echo "======================================================================"
	@echo "Backend:     Check console for coverage report"
	@echo "Frontend:    Check console for coverage report"
	@echo "Integration: Check console for coverage report"
	@echo "======================================================================"

# ── Utilities ─────────────────────────────────────────────────────────────────
.PHONY: shell
shell: ## Open a Django shell (via Compose)
	$(COMPOSE) exec web python manage.py shell

.PHONY: bash-web
bash-web: ## Open a bash shell in the web container
	$(COMPOSE) exec web bash

.PHONY: bash-frontend
bash-frontend: ## Open a shell in the frontend container
	$(COMPOSE) exec frontend sh

.PHONY: lint
lint: ## Run ruff (backend) and eslint (frontend)
	$(COMPOSE) exec web ruff check .
	$(COMPOSE) exec frontend npm run lint

.PHONY: collectstatic
collectstatic: ## Collect Django static files
	$(COMPOSE) exec web python manage.py collectstatic --noinput

.PHONY: clean
clean: ## Remove stopped containers and dangling images
	docker container prune -f
	docker image prune -f

.PHONY: clean-all
clean-all: ## Remove ALL unused Docker resources (images, containers, volumes, networks)
	docker system prune -af --volumes