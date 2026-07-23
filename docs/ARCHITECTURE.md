# Architecture

LogiPulse is organized as a **Modular Monolith**. This document explains what that means in this project, what each layer does, and why the code is structured this way.

## Layers

Every feature module (auth, routes, vehicles, stops, tracking, dashboard, alerts, recommendations, reports, imports, audit logs) follows the same four layers:

| Folder | Layer | Responsibility |
| --- | --- | --- |
| `app/api/v1/` | API routes | HTTP layer |
| `app/models/` | Schemas | Validation / serialization |
| `app/services/` | Services | Business logic |
| `app/repositories/` | Repositories | Database access |
| `app/db/` | MongoDB | Connection & indexes |
| `app/static/` | Demo panel | HTML / CSS / JS |

**API routes (`app/api/v1/`)**
FastAPI routers. They handle the HTTP request, check permissions (`require_role`), call a service, and return a response model. They contain almost no business logic — just wiring.

**Schemas / models (`app/models/`)**
Pydantic models used for request validation (e.g. `RouteCreate`) and response shaping (e.g. `RouteOut`). They also define enums like `RouteStatus` or `StopStatus`, which double as the single source of truth for allowed values.

**Services (`app/services/`)**
This is where the actual business rules live: how cost/profit/carbon are calculated, which status transitions are allowed, when an alert should fire, what counts as a "green recommendation", how CSV rows are validated, and so on. Services depend on repositories, never directly on MongoDB.

**Repositories (`app/repositories/`)**
Each repository wraps one MongoDB collection (`routes`, `vehicles`, `users`, `audit_logs`, ...) and exposes simple methods like `find_one`, `create`, `update_status`. This is the only layer that talks to MongoDB directly.

**Database (`app/db/`)**
Connection setup (Motor async client) and index creation, run once at startup.

**Demo panel (`app/static/`)**
A single-page HTML/CSS/JS admin+driver dashboard, served as static files at `/demo/`. It talks to the API the same way any other client would (JWT in the `Authorization` header). It is a demo/testing tool, not a production frontend.

## Why Modular Monolith, not microservices

At this project's size (one team, one deployable, one MongoDB instance), microservices would add operational cost (multiple services, network calls between them, distributed transactions, more DevOps work) without a matching benefit. A Modular Monolith gives most of the organizational benefit of microservices — clear module boundaries, each module owning its own models/services/repository — while staying a single, simple-to-run, simple-to-test application. If a module ever needs to scale or be owned by a different team, it can be extracted later because the boundaries already exist in the code.

## Repository Pattern

Instead of calling `db["routes"].find(...)` directly from services or API routes, all MongoDB access goes through a repository class (e.g. `RouteRepository`, `VehicleRepository`, `AuditLogRepository`). Each repository extends a small `BaseRepository` with generic helpers (`find_one`, `insert_one`, `update_one`) and adds collection-specific query methods.

This keeps MongoDB-specific code (queries, `ObjectId` handling, indexes) in one place per collection, so services can be written and tested without worrying about database details, and the query logic for a collection isn't duplicated across multiple services that use it.

## Service Layer

Services sit between API routes and repositories. They hold the rules that don't belong in either the HTTP layer or the database layer, for example:

- `RouteService` — which route status transitions are allowed (`_ALLOWED_TRANSITIONS`), and how a route is created with cost/profit/carbon pre-calculated
- `VehicleRecommendationService` — how to score and rank vehicles for a route
- `AlertService` / `RecommendationService` — the rule checks that turn route/stop data into alerts and recommendations
- `AuditLogService` — writes an audit log entry without ever failing the calling request

Because services don't depend on FastAPI or HTTP concepts, they can be reused across different endpoints (for example, the CSV import feature reuses `RouteService.create_route` instead of duplicating route-creation logic).

## Other patterns used

- **Strategy Pattern (early implementation):** `app/services/carbon/` contains a `CarbonEmissionStrategy` interface with one strategy class per vehicle type (bicycle, motorcycle, van, electric van, truck). This was the original approach to carbon calculation. It is still in the codebase, but the live route-creation flow now uses `vehicle_economics.py`, which reads cost/carbon coefficients directly from each vehicle record (set by the admin when the vehicle is created). This is more flexible, since fleet vehicles can have their own real-world numbers instead of one fixed value per vehicle type.
- **Centralized transition table:** route status changes are validated against a single dictionary (`_ALLOWED_TRANSITIONS` in `RouteService`) instead of scattered `if` checks, so the whole state machine is visible and editable in one place.
