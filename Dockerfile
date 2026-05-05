# =============================================================================
# Space Frontier — single-image build
#
# Stages:
#   1. frontend-deps   – npm install (cached layer)
#   2. frontend-build  – next build → static export
#   3. final           – Python runtime + Nginx + supervisord
#
# Services run inside the container (via supervisord):
#   • gunicorn      Django API          :8000 (internal)
#   • celery worker async tasks
#   • celery beat   scheduled tasks
#   • nginx         reverse proxy       :80  (exposed)
#                   /        → Next.js static files
#                   /api/    → gunicorn :8000
#                   /media/  → /app/media
#
# External dependencies (NOT bundled — supply via env / docker-compose):
#   • PostgreSQL
#   • Redis
#
# Build:
#   docker build --build-arg NEXT_PUBLIC_API_BASE=http://yourhost \
#                -t space-frontier .
#
# Run:
#   docker run --env-file .env -p 80:80 space-frontier
# =============================================================================

# ── Stage 1: install JS deps ────────────────────────────────────────────────
FROM node:20-alpine AS frontend-deps

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --prefer-offline


# ── Stage 2: build Next.js ──────────────────────────────────────────────────
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

# Accept the API URL at build time so Next.js can bake it in
ARG NEXT_PUBLIC_API_BASE=http://localhost
ENV NEXT_PUBLIC_API_BASE=${NEXT_PUBLIC_API_BASE}

COPY --from=frontend-deps /app/frontend/node_modules ./node_modules
COPY frontend/ .

# Produce a standalone + static-export build
RUN npm run build


# ── Stage 3: final runtime image ────────────────────────────────────────────
FROM python:3.12-slim AS final

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# ── system packages ──────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        nginx \
        supervisor \
    && rm -rf /var/lib/apt/lists/*

# ── install Node (needed only if you want SSR; for static export it's not
#    required at runtime — remove this block if using `output: "export"`) ────
# If your next.config.js adds `output: 'export'` you can delete the four
# lines below and serve the /out directory directly from Nginx.
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# ── Python deps ──────────────────────────────────────────────────────────────
WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

# ── backend source ───────────────────────────────────────────────────────────
COPY backend/ .

# ── frontend build artefacts ─────────────────────────────────────────────────
# .next/standalone   – self-contained Next.js server  (server.js)
# .next/static       – hashed JS/CSS chunks
# public/            – unprocessed static assets
COPY --from=frontend-build /app/frontend/.next/standalone /app/frontend/
COPY --from=frontend-build /app/frontend/.next/static     /app/frontend/.next/static
COPY --from=frontend-build /app/frontend/public           /app/frontend/public

# ── Django static files ───────────────────────────────────────────────────────
RUN mkdir -p /app/backend/staticfiles /app/backend/media \
    && python manage.py collectstatic --noinput 2>/dev/null || true

# ── Nginx config ──────────────────────────────────────────────────────────────
RUN rm -f /etc/nginx/sites-enabled/default
COPY <<'NGINX' /etc/nginx/conf.d/spacefrontier.conf
server {
    listen 80;
    server_name _;

    client_max_body_size 20M;

    # ── Django static files ──────────────────────────────────────
    location /static/ {
        alias /app/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # ── User-uploaded media ──────────────────────────────────────
    location /media/ {
        alias /app/backend/media/;
        expires 7d;
    }

    # ── Django REST API ──────────────────────────────────────────
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }

    # ── Admin ────────────────────────────────────────────────────
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # ── Health-check endpoint (Django) ───────────────────────────
    location /health/ {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }

    # ── Next.js app ──────────────────────────────────────────────
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade           $http_upgrade;
        proxy_set_header Connection        "upgrade";
    }
}
NGINX

# ── supervisord config ────────────────────────────────────────────────────────
COPY <<'SUPERVISOR' /etc/supervisor/conf.d/spacefrontier.conf
[supervisord]
nodaemon=true
logfile=/dev/null
logfile_maxbytes=0
pidfile=/tmp/supervisord.pid

[program:nginx]
command=/usr/sbin/nginx -g "daemon off;"
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:gunicorn]
command=gunicorn config.wsgi:application
    --bind 127.0.0.1:8000
    --workers 4
    --timeout 30
    --log-file=-
directory=/app/backend
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:celery-worker]
command=celery -A config worker -l INFO
directory=/app/backend
autostart=true
autorestart=true
stopwaitsecs=10
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:celery-beat]
command=celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/app/backend
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:nextjs]
command=node /app/frontend/server.js
environment=PORT=3000,HOSTNAME=127.0.0.1
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
SUPERVISOR

# ── entrypoint: migrate then hand off to supervisord ─────────────────────────
COPY <<'ENTRYPOINT' /entrypoint.sh
#!/bin/sh
set -e
echo "[entrypoint] Running migrations..."
python /app/backend/manage.py migrate --noinput
echo "[entrypoint] Starting services..."
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
ENTRYPOINT
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
