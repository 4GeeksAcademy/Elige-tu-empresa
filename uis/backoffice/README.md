# Incident Backoffice

Framework-free HTML, CSS, and JavaScript interface for Brasaland's incident manager. It has no frontend dependencies: the `services/api/` HTTP service serves these files and the JSON API from the same origin.

## Features

- Register incidents using catalogs served by the API.
- Filter the incident list by status, severity, and responsible area.
- View incident details and change history with author and local timestamps.
- Change status or reassign an area while recording the author.
- View open incident counts by severity.

## Inventory

The `/inventory.html` page manages inventory by location within the same application:

- Create, edit, and deactivate items; stock is always calculated from movements and is never edited directly.
- Register inbound, outbound, and adjustment movements, with API validation for lots and expiry dates.
- View stock, reorder point, inbound and outbound totals, adjustments split into waste, theft, and count correction, and lot details.
- View the reorder signal by location and identify expired stock together with its lot codes.

The interface files are `inventory.html` and `inventory.js`; they are served from the same origin as the API. The inventory view is linked from the top navigation.

## Run and check

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m services.api.server
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v
```

The interface is available at `http://127.0.0.1:8000/`. The persistent database is created at `data/incidents.sqlite`. Stop the server with `Ctrl+C`.

The server binds to `127.0.0.1` by default. Authentication is not included; the author name is entered manually.

> _Versión en español: [README.es.md](./README.es.md)._
