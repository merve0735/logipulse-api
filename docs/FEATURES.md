# Features

This document describes what LogiPulse does, in plain language, without code details.

## Accounts and access

Every user is either an **admin** (fleet/operations manager) or a **driver**. Admins manage vehicles, routes, and see company-wide data. Drivers only see and act on the routes assigned to them. Logging in returns a token that keeps the user signed in for their session.

## Vehicle management

Admins keep a list of vehicles (plate number, type, capacity, average cost per km, average carbon emission per km, active/inactive). This is the fleet LogiPulse plans routes with.

## Smart vehicle recommendation

Before creating a route, an admin can ask "which vehicle should I use for this trip?" by giving the distance, expected revenue, and package weight. LogiPulse scores every active vehicle by expected profit and carbon impact, checks whether its capacity is enough, and returns the best choice plus the alternatives, each with a short reason.

## Route creation and economics

When a route is created, LogiPulse automatically calculates the estimated cost, carbon emission, and profit for that route, based on the chosen vehicle's numbers and the trip distance. Nothing has to be calculated by hand.

## Multi-stop delivery management

A single route can contain several delivery stops, each with its own customer, address, and package details. Stops are tracked individually as the driver works through the route.

## Proof of delivery

When a driver completes a stop, they record proof: recipient name, an optional signature text, an optional delivery photo link, delivery coordinates, and a note. This proof stays attached to the stop's history.

## Driver location tracking map

Drivers can update their current location. Admins see all drivers on a live map (built with Leaflet and OpenStreetMap), along with which route each driver is currently working on.

## Dashboard summary

A single screen for admins showing the health of the whole fleet: total routes, distance, revenue, cost, profit, carbon emissions, the most and least profitable route, vehicle-type breakdown, and delivery-quality numbers (delivered, failed, skipped, retried, pending, and overall success rate).

## Business alerts

LogiPulse automatically flags situations that need attention: routes losing money, routes with unusually high carbon emissions, cancelled routes, high-emission diesel trips, failed deliveries, skipped stops, and stops scheduled for retry.

## Green recommendations

Beyond alerts, LogiPulse looks for patterns and suggests actions: optimizing loss-making routes, reducing carbon on high-emission routes, shifting more trips to electric vehicles, reviewing cancelled routes, and investigating failed or retried deliveries.

## Sustainability report and PDF export

A combined report pulling together financial performance, carbon impact, risk (from alerts), and improvement opportunities (from recommendations) into one readable summary — viewable on screen or downloaded as a PDF for sharing outside the system.

## CSV route import

Instead of creating a route stop-by-stop, an admin can upload a CSV file with a list of delivery stops and have LogiPulse create the whole multi-stop route in one step. If some rows in the file are invalid, LogiPulse reports exactly which rows and fields have problems instead of silently failing or importing bad data.

## Audit logs

LogiPulse keeps a record of important actions across the system — registrations, logins, vehicle creation, route lifecycle events, stop deliveries, location updates, CSV imports, and report downloads — so an admin can always answer "who did this, and when?". Writing this log never blocks or breaks the action it is recording.

## Filtering, search, and pagination

Route lists (and audit logs) support filtering by status, vehicle type, driver, profit/carbon range, and free-text search, plus sorting and page-by-page loading, so the system stays usable as the amount of data grows.

## Automated tests and CI

The core behaviors above (auth, permissions, vehicles, routes, stops, tracking, dashboard, audit logs) are covered by automated tests, which run automatically on every push through GitHub Actions.
