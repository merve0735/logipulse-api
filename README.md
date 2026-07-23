# LogiPulse

Carbon-aware logistics and delivery management API.

## Problem

Logistics and courier companies usually track routes, vehicles, costs, carbon emissions, and delivery quality in separate tools, or in spreadsheets. This makes it hard to answer simple questions like "which routes are losing money?", "which routes produce the most carbon?", or "who delivered what, and when?".

## Solution

LogiPulse is a backend API that brings route planning, vehicle management, courier tracking, carbon and profit calculation, proof of delivery, and reporting into one system. It automatically calculates cost, profit, and carbon emission for every route, flags risky routes with business alerts, suggests improvements with rule-based recommendations, and gives admins a live map of where their drivers are. A sustainability report (with PDF export) and an audit log of important actions are included for accountability.

A small HTML/JavaScript demo panel is bundled with the API so the whole flow (admin and driver) can be tested without building a separate frontend.

## Key Features

- JWT authentication
- Admin / driver role-based access control
- Vehicle management (fleet CRUD)
- Smart vehicle recommendation (best vehicle for a given route)
- Route creation with automatic cost / profit / carbon calculation
- Multi-stop delivery management
- Proof of delivery (recipient name, signature text, photo URL, note)
- Driver location tracking with a live map (Leaflet + OpenStreetMap)
- Dashboard summary (fleet-wide financial, carbon, and delivery-quality metrics)
- Business alerts (loss-making routes, high carbon, failed deliveries, etc.)
- Rule-based green recommendations
- Sustainability report with PDF export
- CSV route import
- Audit logs (who did what, and when)
- Route filtering, search, and pagination
- Automated tests and GitHub Actions CI

## Tech Stack

- FastAPI
- MongoDB (via Motor, async driver)
- Docker & Docker Compose
- JWT (python-jose)
- Pytest
- GitHub Actions
- Leaflet + OpenStreetMap
- ReportLab (PDF generation)
- HTML / CSS / JavaScript demo panel (no frontend framework)

## Architecture

LogiPulse is built as a **Modular Monolith**: one deployable service, but internally split into clear modules (auth, routes, vehicles, stops, tracking, dashboard, alerts, recommendations, reports, imports, audit logs).

Each module follows the same layering:

- **API routes** — HTTP endpoints, request/response handling, permission checks
- **Schemas / models** — Pydantic models for validation and serialization
- **Services** — business logic and rules
- **Repositories** — MongoDB access (Repository Pattern)

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details on why this structure was chosen.

## Getting Started

1. Copy the example environment file and adjust it if needed:

   ```bash
   cp .env.example .env
   ```

2. Build and start the containers (API + MongoDB):

   ```bash
   docker compose up --build
   ```

3. Open the interactive API docs (Swagger UI):

   ```
   http://localhost:8000/docs
   ```

4. Open the demo panel:

   ```
   http://localhost:8000/demo/
   ```

## Demo Seed Data

Instead of creating everything by hand, one command fills the database with realistic demo data — enough for the dashboard, alerts, recommendations, sustainability report, map, audit logs, and proof of delivery screens to all show meaningful content right away.

```bash
docker compose exec api python -m app.scripts.seed_demo_data
```

This creates demo users, a small fleet (electric van, diesel van, motorcycle, and one inactive vehicle), and five routes covering different scenarios (profitable, loss-making, high-carbon, completed, cancelled) with their stops. It also writes one audit log entry (`demo_seeded`) so the seeding action itself is traceable.

The script is safe to run more than once: users are matched by email, vehicles by plate number, and routes by name, so re-running it does not create duplicates. It never deletes or wipes existing data — it only adds what's missing.

Demo accounts (password in parentheses):

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@logipulse.demo` | `Demo1234` |
| Driver | `driver1@logipulse.demo` | `Driver12345` |
| Driver | `driver2@logipulse.demo` | `Driver12345` |
| Driver | `driver3@logipulse.demo` (no saved location, shown as "no location" on the map) | `Driver12345` |

## Running Tests

Tests use a separate database (`logipulse_test`) and never touch the real data.

Run tests locally through Docker:

```bash
docker compose exec api pytest -q
```

GitHub Actions runs the same test suite automatically on every `push` and `pull_request` (see `.github/workflows/tests.yml`). It spins up a temporary MongoDB service, installs dependencies, and runs `pytest -q`. Results are visible under the **Actions** tab of the repository.

## Conventional Commits

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for commit messages, for example:

- `feat(auth): add jwt login`
- `fix(demo): update route form`
- `test(api): add backend tests`
- `docs(project): improve readme and technical documentation`

## Notes

**Location entry (tracking):** the "Update My Location" field in the demo panel currently takes manual latitude/longitude input. In a real mobile courier app this would come automatically from the phone's GPS; manual entry is used here to keep the MVP simple.

**KVKK / personal data note:** in real-world use, driver location data can be considered personal data. User consent, data retention period, and access permissions would need to be designed separately before production use. See [docs/TECH_DECISIONS.md](docs/TECH_DECISIONS.md) for more detail.

## Project Status

LogiPulse is an MVP (minimum viable product) built during a 30-day internship project. Core flows (auth, routes, vehicles, stops, tracking, dashboard, alerts, recommendations, reports, CSV import, audit logs) are complete and covered by automated tests.

Possible next improvements:

- Real-time location updates (WebSocket) instead of manual refresh
- Notification system (email/push) for alerts
- AI/RAG-based recommendations on top of the current rule-based engine
- Multi-tenant support for multiple companies
- Role for a third user type (e.g. dispatcher / fleet manager)

## More Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — layers, patterns, and why Modular Monolith
- [docs/API_OVERVIEW.md](docs/API_OVERVIEW.md) — endpoint groups
- [docs/FEATURES.md](docs/FEATURES.md) — features explained in plain language
- [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) — suggested order for demoing the project
- [docs/TECH_DECISIONS.md](docs/TECH_DECISIONS.md) — why each technology was chosen
