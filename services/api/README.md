# Incident API service

Database foundation and models for Brasaland's centralized incident manager. Persistence uses Python's standard-library SQLite module and the project's approved catalogs.

## Contents

- `catalogs.py`: validated channels, types, severities, responsible areas, and statuses.
- `models.py`: incident and history entities, UUID v4 IDs, and UTC timestamps.
- `database.py`: SQLite connections, constraints, and immutable history-event protection.
- `incidents.py`: validation and registration of incidents in their initial status.
- `tests/`: tests using `unittest` and an in-memory database.

## Checks

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v
```

Initialize a database with `createConnection(path)` and `initializeDatabase(connection)`. Register an incident with `registerIncident(connection, ...)`; the function validates catalogs and persists the author and UTC timestamps, then returns the created model. The caller is responsible for closing the connection.

> FastAPI HTTP endpoints remain pending because the dependency and lockfile cannot be prepared while `uv.lock` is excluded.

> _Versión en español: [README.es.md](./README.es.md)._
