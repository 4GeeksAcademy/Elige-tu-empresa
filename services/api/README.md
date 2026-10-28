# Incident API service

HTTP API and use cases for Brasaland's centralized incident manager. The server uses Python's standard library (`http.server`) and SQLite persistence.

## Contents

- `catalogs.py`: validated channels, types, severities, responsible areas, and statuses, plus the inventory catalogs (units, categories, movement types, adjustment reasons, and locations).
- `models.py`: incident, history, and inventory item, lot, and movement entities, UUID v4 IDs, and UTC timestamps.
- `database.py`: SQLite connections, constraints, immutable history events, and the inventory tables (append-only movements, immutable lots, and a trigger that blocks negative stock).
- `incidents.py`: registration, validated status/area changes, incident details with history, filterable listing, and severity counts.
- `inventory.py`: inventory use cases: items, stock movements, lots and expiry, stock calculation (`calculateStock`), stock report, and reorder signal.
- `inventoryseed.py`: inventory seed data and the command that loads it.
- `server.py`: JSON API and static-file server with no external dependencies.
- `tests/`: tests using `unittest`, an in-memory database, and a real server on an ephemeral port for the API.
- `uis/backoffice/`: static interface served from the same origin.

## Checks

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v
```

From the repository root, start the local server with:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m services.api.server
```

Open `http://127.0.0.1:8000/`. The server creates `data/incidents.sqlite` and binds to loopback by default.

The API provides `GET /api/catalogs`, `GET` and `POST /api/incidents`, `GET /api/incidents/{id}`, `PATCH /api/incidents/{id}/status`, `PATCH /api/incidents/{id}/area`, and `GET /api/incidents/summary/by-severity`. The list accepts optional `statusId`, `severityId`, and `responsibleAreaId` filters. Errors are returned as JSON with a corresponding HTTP status.

The static interface supports registration, filtering, incident details and history, status/area changes, and severity counts. The manually entered author is recorded for audit history; authentication is not included.

## Inventory

The inventory manager shares the server and the SQLite file (`data/incidents.sqlite`) with incidents. Available stock is never stored: it is always calculated from the stock movements. Quantities travel as decimal strings (for example `"12.500"`; `kg` and `l` admit three decimals and `g`, `ml`, and `unit` admit none).

Load the seed data (16 items and their movements) from the repository root with:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m services.api.inventoryseed
```

The command accepts `--database <path>` and is rejected, without changing anything, if the database already contains items.

The inventory API lives under `/api/inventory/`: `GET /catalogs`, `GET` and `POST /items` (the list accepts an optional `locationId` filter), `GET`, `PATCH`, and `DELETE /items/{id}`, `POST /items/{id}/movements`, `GET /items/{id}/report`, and `GET /locations/{locationId}/reorder`. There is no route to edit stock or to modify or delete a movement. Rejections use `400` (invalid data), `404` (unknown item, lot, or location), and `409` (business rule: negative stock, expired lot, lot of another item, or an item that already has movements).

> _Versión en español: [README.es.md](./README.es.md)._
