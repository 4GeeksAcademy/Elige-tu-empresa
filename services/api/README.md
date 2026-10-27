# Incident API service

HTTP API and use cases for Brasaland's centralized incident manager. The server uses Python's standard library (`http.server`) and SQLite persistence.

## Contents

- `catalogs.py`: validated channels, types, severities, responsible areas, and statuses.
- `models.py`: incident and history entities, UUID v4 IDs, and UTC timestamps.
- `database.py`: SQLite connections, constraints, and immutable history-event protection.
- `incidents.py`: registration, validated status/area changes, incident details with history, filterable listing, and severity counts.
- `server.py`: JSON API and static-file server with no external dependencies.
- `tests/`: tests using `unittest` and an in-memory database.
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

> _Versión en español: [README.es.md](./README.es.md)._
