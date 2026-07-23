# API Overview

All endpoints are under the `/api/v1` prefix and use JWT bearer authentication (`Authorization: Bearer <token>`), except `register` and `login`. Full interactive documentation with request/response schemas is available at `/docs` (Swagger UI) once the API is running.

A ready-to-use Postman collection with every endpoint below is available in [`postman/`](../postman/) — see the "Postman Collection" section in [README.md](../README.md) for how to import and use it.

## Auth (`/api/v1/auth`)

Register a new user (admin or driver), log in to get a JWT, and read the currently logged-in user's profile.

## Users (`/api/v1/users`)

Admin-only. Lists all users with the `driver` role, used for example to populate the "assign driver" dropdown.

## Vehicles (`/api/v1/vehicles`)

Manage the fleet: create a vehicle (admin only) with its cost/carbon coefficients, list all vehicles, and get a smart recommendation for the best vehicle for a given route (based on distance, expected revenue, and package weight).

## Routes (`/api/v1/routes`)

Create routes (admin), list routes with filtering/search/sorting/pagination, list "my routes" (driver), assign a driver to a route, and move a route through its status workflow (start, deliver, cancel).

## Stops (`/api/v1/routes/{route_id}/stops`)

Manage the individual delivery stops inside a route: list stops, and let the assigned driver mark a stop as delivered (with proof of delivery), failed, skipped, or scheduled for retry.

## Tracking (`/api/v1/tracking`)

Drivers update their own current location; admins can see the latest known location of every driver, together with their currently active route.

## Dashboard (`/api/v1/dashboard`)

Admin-only summary of the whole fleet: total routes, distance, revenue, cost, profit, carbon, best/worst route, and delivery-quality numbers (delivered/failed/skipped/retry counts, success rate).

## Alerts (`/api/v1/alerts`)

Admin-only. Rule-based warnings generated from current route and stop data, for example loss-making routes, high-carbon routes, cancelled routes, and failed deliveries.

## Recommendations (`/api/v1/recommendations`)

Admin-only. Rule-based suggestions to improve profit, reduce carbon, and improve delivery quality, based on patterns across all routes.

## Reports (`/api/v1/reports`)

Admin-only. A sustainability report combining financial, carbon, risk (alerts), and recommendation summaries, available as JSON or as a downloadable PDF.

## Imports (`/api/v1/imports`)

Admin-only. Upload a CSV file of delivery stops to create a multi-stop route in one request, with row-by-row validation errors returned if the file is invalid.

## Audit Logs (`/api/v1/audit-logs`)

Admin-only. A paginated, filterable log of important actions taken in the system (who did what, and when) — for example route creation, driver assignment, deliveries, and CSV imports.

## Health (`/health`)

A simple, unauthenticated endpoint used to check that the API is running.
