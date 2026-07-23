# Tech Decisions

Short explanations for the main technology and architecture choices in LogiPulse.

## Why FastAPI?

FastAPI is async-native (fits well with an async MongoDB driver), validates requests/responses automatically through Pydantic models, and generates interactive API docs (Swagger UI) for free. That combination made it a good fit for building and testing an API quickly without giving up structure.

## Why MongoDB?

Routes in LogiPulse contain a variable, nested list of stops (each with its own status, proof of delivery, failure reason, etc.). This kind of nested, document-shaped data fits naturally into MongoDB's document model, without needing several relational tables and joins just to read one route.

## Why Docker?

Docker Compose runs the API and MongoDB together with one command (`docker compose up --build`), with the same setup on any machine. This removes "works on my machine" problems and makes onboarding (or grading) the project simple.

## Why JWT?

JWT is stateless: the server doesn't need to store session data, and the token carries the user's id and role, which is enough for role-based access control (`require_role`) on every request. It's also simple to use from the demo panel's JavaScript.

## Why Modular Monolith?

For a project of this size, running one deployable service is simpler to build, run, and test than coordinating multiple microservices over a network. Splitting the code into modules (routes, vehicles, stops, tracking, etc.) with their own models/services/repositories gives most of the organizational benefit of microservices, while staying easy to run locally and reason about. See [ARCHITECTURE.md](ARCHITECTURE.md) for more detail.

## Why Leaflet + OpenStreetMap?

Leaflet is a lightweight, free mapping library, and OpenStreetMap tiles don't require an API key or billing account. That's a good fit for a demo/MVP that needs a working map without adding a paid dependency.

## Why rule-based recommendations before AI/RAG?

Alerts and recommendations are currently generated from simple, explainable rules (thresholds and counts over route/stop data — for example "profit is negative" or "carbon is above X kg"). This was chosen first because it's predictable, easy to test, and easy to explain to a non-technical user ("why did I get this alert?" always has a clear answer). An AI/RAG-based layer could be added later on top of this same data to generate more nuanced suggestions, but the rule-based version is a solid, transparent baseline to build on rather than starting with something harder to verify.

## Why audit logs?

Once multiple people (admins and drivers) act on the same data, "who did this, and when?" becomes an important question — for troubleshooting, and for basic accountability. Audit logging was added as its own small module so it can record any important action without being tightly coupled to the business logic of that action, and so that a logging failure can never break the action itself (log-write errors are caught and swallowed).

## KVKK / personal data note

Driver location data, collected for the tracking map, can be considered personal data. This project is an MVP and does not implement consent screens, data retention limits, or granular access permissions for that data. Before any real-world use, these would need to be designed properly (explicit consent, a defined retention period, and clear rules on who can access location history) to comply with data protection regulations such as KVKK.
