# Deployment Guide

This document explains how LogiPulse is prepared for production and what to check before actually deploying it anywhere. It does **not** deploy the project — it only makes it deploy-ready. No platform (Railway, Render, Fly.io, ...) or domain is chosen yet.

## Local development vs. production

| | Development | Production |
| --- | --- | --- |
| Compose file | `docker-compose.yml` | `docker-compose.prod.yml` |
| Dockerfile | `Dockerfile` | `Dockerfile.prod` |
| API server | `uvicorn --reload` (auto-restarts on code changes) | `uvicorn` without `--reload` |
| Source code | Bind-mounted (`.:/app`) so edits apply instantly | Copied into the image at build time (`COPY . .`) — a real rebuild is needed to deploy new code |
| MongoDB port | Published to the host (`27017:27017`), handy for a local GUI client | Not published — only reachable from the `api` container over the Docker network |
| Swagger / ReDoc | Enabled (`ENVIRONMENT=development`) | Disabled automatically when `ENVIRONMENT=production` |
| Restart policy | None (you start/stop it manually) | `restart: unless-stopped` on both services |

## Dockerfile vs. Dockerfile.prod

`Dockerfile` is built for a smooth local dev loop: it runs `uvicorn --host 0.0.0.0 --port 8000 --reload`, and `docker-compose.yml` bind-mounts the project directory over it so code edits show up immediately without rebuilding the image.

`Dockerfile.prod` drops `--reload` (a live reloader has no place in production — it costs CPU and isn't needed once the code isn't changing under it) and sets `PYTHONDONTWRITEBYTECODE=1` / `PYTHONUNBUFFERED=1` so `.pyc` files aren't written and logs are flushed immediately instead of buffered. Otherwise it's intentionally almost identical to the dev Dockerfile — same base image, same `pip install`, no multi-stage build or extra tooling, so the two stay easy to compare and reason about.

## docker-compose.yml vs. docker-compose.prod.yml

`docker-compose.prod.yml` is a separate file, not a modification of the dev one, so local development is never at risk of picking up a production-only setting by accident. Differences:

- Builds `Dockerfile.prod`, not `Dockerfile`.
- No source bind-mount — the image is the deployable artifact.
- MongoDB's `27017` port is **not** published to the host (see "MongoDB security" below).
- Both services have `restart: unless-stopped`.
- Both services have a healthcheck (see "Healthcheck" below), and `api` waits for MongoDB to report healthy before starting (`depends_on: condition: service_healthy`).
- MongoDB's root username/password come from `MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD` in `.env`, instead of being hard-coded in the compose file.

Run it with:

```bash
docker compose -f docker-compose.prod.yml up --build -d
docker compose -f docker-compose.prod.yml logs api -f
docker compose -f docker-compose.prod.yml down
```

## Environment variables

All variables are documented with comments in `.env.example` — copy it to `.env` and fill in real values before running the production stack. The important ones for a deployment:

- `ENVIRONMENT` — set to `production`. This disables `/docs` and `/redoc` (API documentation shouldn't be publicly browsable by default in production).
- `JWT_SECRET_KEY` — must be a long, random, unguessable value. Generate one with `openssl rand -hex 32`. If this leaks, every issued token is effectively compromised.
- `MONGO_URI`, `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD` — real database credentials. The last two configure the MongoDB container itself (used only by `docker-compose.prod.yml`); `MONGO_URI` is what the API actually connects with, and it must contain the *same* username/password.
- `GEMINI_API_KEY` — your real Gemini key, or leave it empty to run without the AI Advisor (the endpoint then returns a clear 503 instead of failing unpredictably).
- `CORS_ORIGINS` — see below.
- `LOG_LEVEL` — `INFO` by default; `WARNING` to only see slow requests and errors.

## CORS

The API only accepts cross-origin browser requests from the origins listed in `CORS_ORIGINS` (a comma-separated string, parsed in `app/core/config.py` and wired into FastAPI's `CORSMiddleware` in `app/main.py`). There is no `allow_origins=["*"]` anywhere — in production, set `CORS_ORIGINS` to the exact domain(s) that will call this API (for example, `https://logipulse.example.com`). Anything not in that list is rejected by the browser itself.

## MongoDB security

Two things keep MongoDB from being an open door in production:

1. `docker-compose.prod.yml` does **not** publish MongoDB's port to the host, so it can't be reached from outside the Docker network at all — the `api` container talks to it internally by service name (`mongodb`), the same way it does in development.
2. Root credentials are set from `.env` (`MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD`), not hard-coded — change them from the example values before deploying, and keep `MONGO_URI` in sync.

If you ever deploy MongoDB on a separate host from the API (instead of the same Docker network), make sure it still isn't reachable from the public internet — bind it to a private network or firewall it to only the API's IP.

## Gemini API key

Treat `GEMINI_API_KEY` like any other secret: it lives in `.env` (or your hosting platform's secret/environment variable store) and nowhere else. It must never be committed to the repository, pasted into code, or written to logs — the application logging system (see the README's "Application Logging" section) never logs it, request bodies, or any other secret by design.

## Logs

Backend logs go to stdout in the `HH:MM:SS | LEVEL | scope | message` format described in the README — that's what `docker compose -f docker-compose.prod.yml logs api -f` shows. On most hosting platforms, stdout/stderr from a container is automatically captured and searchable in that platform's log viewer, so no extra logging infrastructure is required for a first deployment. Slow requests (>1 second) are logged as `WARNING`, which is a reasonable thing to alert on later if the hosting platform supports log-based alerts.

## Healthcheck

Both services in `docker-compose.prod.yml` have a healthcheck:

- `api` calls its own `GET /health` endpoint using Python's standard library (no extra tool needs to be installed in the image just for this).
- `mongodb` runs `mongosh --eval "db.adminCommand('ping')"` with the configured root credentials.

`api` won't be marked healthy — and won't start serving traffic that depends on the database — until `mongodb` itself reports healthy (`depends_on: condition: service_healthy`). Most container hosting platforms (and `docker compose ps`) surface this health status, which is useful for knowing whether a deployment actually came up correctly instead of just "the process started."

## Before choosing a deployment platform: checklist

- [ ] `.env` created locally with real, non-example values (never committed)
- [ ] `JWT_SECRET_KEY` changed to a strong random value
- [ ] `MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD` changed, and `MONGO_URI` updated to match
- [ ] `CORS_ORIGINS` set to the real frontend domain(s) — no `*`
- [ ] `ENVIRONMENT=production` set (disables `/docs` and `/redoc`)
- [ ] `GEMINI_API_KEY` set only if the AI Advisor should be enabled; never committed
- [ ] `docker compose -f docker-compose.prod.yml up --build -d` runs cleanly and both services report healthy
- [ ] `pytest -q` passes against the dev stack (or in CI) before building the production image — `tests/` is intentionally excluded from the production image via `.dockerignore`
- [ ] MongoDB is confirmed unreachable from outside the Docker network (or, if hosted separately, from the public internet)
- [ ] A plan exists for where MongoDB data actually persists (the named volume `mongo_data_prod` is fine for a single host, but won't survive that host being destroyed — back it up, or use a managed database, before real users depend on it)
- [ ] Demo/seed accounts are not relied upon for real access control
