# Demo Guide

Suggested order for presenting LogiPulse using the demo panel (`/demo/`). Each step points to where it lives in the sidebar.

1. **Admin login** — log in with an admin account. The login screen is separate from the dashboard, and the demo account is pre-filled for convenience.
2. **Dashboard (Yönetici Özeti)** — show the fleet-wide summary: total routes, revenue, cost, profit, carbon, best/worst route, and delivery-quality numbers.
3. **Vehicle management (Araçlar)** — show the vehicle list, then add a new vehicle (plate number, type, capacity, cost/carbon per km).
4. **Smart vehicle recommendation (Akıllı Araç Önerisi)** — enter a distance, expected revenue, and package weight, and show the recommended vehicle plus alternatives with their scores.
5. **Route creation (Yeni Rota Oluştur)** — create a route: origin, destination, distance, vehicle, expected revenue, and one or more stops. Point out that cost/profit/carbon are calculated automatically.
6. **CSV import (CSV İçe Aktar)** — upload a CSV file to create a multi-stop route in one step. Optionally show what happens with an invalid file (row-level error messages).
7. **Route filtering (Rotalar)** — filter/search/sort the route list (by status, vehicle type, profit/carbon range), and page through results.
8. **Stops and proof of delivery** — open a route's stop list, and show a driver marking a stop as delivered with recipient name, note, and coordinates (this can be shown from the admin view, or continued in the driver flow below).
9. **Driver location map (Kurye Haritası)** — show the live map with driver positions and their current active route.
10. **Alerts (Uyarılar)** — show the automatically generated warnings (loss-making routes, high carbon, failed deliveries, etc.).
11. **Recommendations (Öneriler)** — show the rule-based suggestions generated from current route/stop data.
12. **Sustainability report (Sürdürülebilirlik Raporu)** — show the combined financial/carbon/risk/recommendation report on screen.
13. **PDF export** — download the same report as a PDF from the report page.
14. **Audit logs (İşlem Geçmişi)** — show the log of actions taken so far (logins, vehicle/route creation, deliveries), and demonstrate filtering by action, role, or entity type.
15. **Driver login and driver flow** — log out, log in as a driver, and show that the sidebar only has "Rotalarım" and "Konumumu Güncelle" (no admin pages). Open an assigned route, deliver/fail/skip a stop, and update the driver's location.

This order goes from "what a manager sees first" (dashboard) to "how the data gets there" (vehicles, routes, CSV import) to "what the system does with that data" (alerts, recommendations, reports, audit logs), and ends with the driver's side of the same story.
