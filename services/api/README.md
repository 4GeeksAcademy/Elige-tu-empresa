# Incident API service

Database foundation and models for Brasaland's centralized incident manager. Persistence uses Python's standard-library SQLite module and the project's approved catalogs.

## Contents

- `catalogs.py`: validated channels, types, severities, responsible areas, and statuses.
- `models.py`: incident and history entities, UUID v4 IDs, and UTC timestamps.
- `database.py`: SQLite connections, constraints, and immutable history-event protection.
- `tests/`: tests using `unittest` and an in-memory database.

## Checks

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v
```

Initialize a database with `createConnection(path)` and `initializeDatabase(connection)`. The caller is responsible for closing the connection. Incident updates and their history events will be committed in one transaction in the traceability step.

> This persistence foundation does not expose HTTP endpoints yet.

> _Versión en español: [README.es.md](./README.es.md)._
