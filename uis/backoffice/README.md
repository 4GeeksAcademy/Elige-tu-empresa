# Incident Backoffice

Framework-free HTML, CSS, and JavaScript interface for Brasaland's incident manager. It has no frontend dependencies: the `services/api/` HTTP service serves these files and the JSON API from the same origin.

## Features

- Register incidents using catalogs served by the API.
- Filter the incident list by status, severity, and responsible area.
- View incident details and change history with author and local timestamps.
- Change status or reassign an area while recording the author.
- View open incident counts by severity.

## Run and check

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m services.api.server
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v
```

The interface is available at `http://127.0.0.1:8000/`. The persistent database is created at `data/incidents.sqlite`. Stop the server with `Ctrl+C`.

The server binds to `127.0.0.1` by default. Authentication is not included; the author name is entered manually.

> _Versión en español: [README.es.md](./README.es.md)._
