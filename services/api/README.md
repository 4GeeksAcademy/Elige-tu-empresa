# Incident API service

Database foundation and models for Brasaland's centralized incident manager. Persistence uses Python's standard-library SQLite module and the project's approved catalogs.

## Contents

- `catalogs.py`: validated channels, types, severities, responsible areas, and statuses.
- `models.py`: incident and history entities, UUID v4 IDs, and UTC timestamps.
- `database.py`: SQLite connections, constraints, and immutable history-event protection.
- `incidents.py`: registration, validated status/area changes, incident details with history, filterable listing, and severity counts.
- `tests/`: tests using `unittest` and an in-memory database.

## Checks

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v
```

Initialize a database with `createConnection(path)` and `initializeDatabase(connection)`. Use `registerIncident(connection, ...)` to register an incident; `changeIncidentStatus(...)` and `reassignIncidentArea(...)` for validated changes with transactional history events; `getIncidentDetails(...)` to retrieve a record with its history; `listIncidents(connection, statusId=..., severityId=..., responsibleAreaId=...)` to list incidents using optional validated filters; and `getOpenIncidentCountsBySeverity(connection)` to count incidents in `nueva`, `enCurso`, or `resuelta` status by severity. The summary includes every approved severity, including those with zero incidents.

> FastAPI HTTP endpoints remain pending because the dependency and lockfile cannot be prepared while `uv.lock` is excluded.

> _Versión en español: [README.es.md](./README.es.md)._
