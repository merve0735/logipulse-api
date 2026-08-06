# Deployment Guide

This document explains how LogiPulse is prepared for production and what to check before actually deploying it anywhere. It does **not** deploy the project — it only makes it deploy-ready.

Two deployment shapes are both valid and both described in this doc:

- **Self-hosted MongoDB**: `docker-compose.prod.yml` runs the API *and* a MongoDB container together on the same host (see below). Data lives in the `mongo_data_prod` named volume.
- **Managed database (e.g. MongoDB Atlas) + a container platform (e.g. Render)**: only `Dockerfile.prod` is used to build and run the API; `docker-compose.prod.yml`'s `mongodb` service is not involved at all. `MONGO_URI` simply points at the Atlas connection string instead of the local `mongodb` service name — the application code does not know or care which one it is, since it only ever talks to `MONGO_URI`/`MONGO_DB_NAME` from `app/core/config.py`. This is the shape covered in detail in "Production Data Safety" below.

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

## Production Data Safety

This section is for the "API on Render + database on MongoDB Atlas" shape specifically — the question it answers is: **if I redeploy the API, can I lose or corrupt real user data (users, routes, vehicles, deliveries, audit logs)?**

### Where the data actually lives

The API never embeds a database inside itself. It connects to whatever `MONGO_URI`/`MONGO_DB_NAME` point at (`app/core/config.py` → `app/db/mongodb.py`) — on Render that's an external MongoDB Atlas cluster, not anything inside the Render container. This matters because it means:

- **Redeploying the API does not touch the database at all.** A Render redeploy rebuilds the image from `Dockerfile.prod` and restarts the process; it has no code path that creates, drops, or migrates a database. The only thing the app does to Mongo on startup is create three indexes (`users.email`, `vehicles.plate_number`, `audit_logs.created_at`) — index creation is safe and idempotent, and does not touch existing documents.
- **The container is stateless.** If the Render instance is destroyed and rebuilt, your data is unaffected, because it was never stored there — it's in Atlas.
- **The one thing that *does* matter is the `MONGO_URI` value itself.** If a redeploy accidentally changes `MONGO_URI` to point at a different (e.g. empty, or a staging) cluster/database name, the app will look like it "lost" all its data — it didn't; it's just talking to a different database now. Always double check `MONGO_URI` and `MONGO_DB_NAME` in Render's environment variables before/after a deploy, especially after rotating credentials.

### No destructive operations exist in the codebase

This was verified directly, not assumed: there is no `delete_one`, `delete_many`, `drop_database`, `.drop()`, or `remove()` call anywhere in `app/`. `BaseRepository` (`app/repositories/base.py`) only exposes `find_one`, `insert_one`, and `update_one` (which uses `$set`, never a full document replace) — there is structurally no way for a normal API request to delete a document. The only way data could be lost is at the infrastructure level (someone manually dropping the Atlas cluster/collection, or a `MONGO_URI` pointed at the wrong database) — not from application code.

### Seed script guard

`app/scripts/seed_demo_data.py` is idempotent and never deletes data even when run against the wrong database — but it *does* insert demo users with known passwords (`admin@logipulse.demo` / `Demo1234`, etc.) and fake routes/vehicles, which is exactly the kind of thing you don't want mixed into real user data by accident.

It now refuses to run when `ENVIRONMENT=production`, unless you explicitly opt in:

```bash
# Blocked by default:
ENVIRONMENT=production python -m app.scripts.seed_demo_data
# -> HATA: ENVIRONMENT=production tespit edildi. ... (exits 1, never connects to the DB)

# Only if you really mean it:
ALLOW_SEED_IN_PRODUCTION=yes python -m app.scripts.seed_demo_data
```

Covered by `tests/test_production_safety.py::test_seed_guard_blocks_in_production` and `::test_seed_guard_allows_production_with_explicit_override`.

### Old-record / schema-drift compatibility

When a new optional field is added to a model in the future, existing MongoDB documents written before that change won't have it. This codebase already reads documents defensively for every field that's genuinely optional — `doc.get("stops", [])`, `doc.get("assigned_driver_id")`, `doc.get("last_location")`, `doc.get("customer_phone")`, etc. (see `app/api/v1/routes.py`, `app/services/tracking_service.py`) — so a record from before a given optional field existed loads without error; the field just comes back as `None`/empty instead of crashing the response.

`tests/test_production_safety.py` locks this behavior in with two regression tests: a route document with no `stops` key at all, and a stop document missing every optional field (`customer_phone`, `latitude`/`longitude`, `package_weight_kg`, `delivery_note`, `failure_reason`, `delivered_at`, `proof_of_delivery`) — both must convert to their API response models without raising.

If a *required* field is ever added to a model later, that's the one case that would need a real migration (a one-off script that backfills the new field on existing documents) — there isn't one today because no required field has changed since this schema was introduced.

### Backup / export strategy (MongoDB Atlas)

Keep this simple — you don't need a backup pipeline for a project at this stage, just a habit before anything risky:

**Before any deploy that changes data shape, or any manual database operation:**

```bash
mongodump --uri="$MONGO_URI" --out="./backups/$(date +%Y-%m-%d_%H%M)"
```

This dumps every collection in the target database to a local folder. Restoring (if you ever need to) is the mirror command:

```bash
mongorestore --uri="$MONGO_URI" "./backups/2026-08-06_1200"
```

Two lower-effort alternatives, in order of how little setup they need:

1. **Atlas UI export** — in the Atlas dashboard, open a collection → "Export Collection" → download as JSON. No tooling install required, good for a quick one-off snapshot of a single collection (e.g. `users` before a risky change).
2. **Atlas Cloud Backups** (if your cluster tier supports it) — Atlas can take automatic scheduled snapshots with point-in-time restore. This is the "set it up once and forget it" option; check it under Atlas → your cluster → Backup. Free/shared (M0) tiers don't include this, so `mongodump` is the fallback until the project is on a paid tier.

Either way: **take a snapshot before every production deploy that changes a model's required fields**, and before running any manual database command by hand. Routine deploys that only change API/frontend code (no model changes) don't need a backup first, since (as above) they never touch existing documents.

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
- [ ] `MONGO_URI` / `MONGO_DB_NAME` double-checked against the target environment before every deploy (a wrong value silently points the app at an empty or different database — see "Production Data Safety" above)
- [ ] `ALLOW_SEED_IN_PRODUCTION` is **not** set in the production environment's variables (it must stay unset so `seed_demo_data.py` keeps refusing to run there by default)
- [ ] Demo/seed accounts are not relied upon for real access control
