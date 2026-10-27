# Servicio API de incidencias

Base de datos y modelos del gestor centralizado de incidencias de Brasaland. La persistencia usa SQLite de la biblioteca estándar de Python y los catálogos aprobados del proyecto.

## Contenido

- `catalogs.py`: canales, tipos, severidades, áreas responsables y estados validados.
- `models.py`: entidades de incidencia e historial, IDs UUID v4 y marcas temporales UTC.
- `database.py`: conexiones, restricciones SQLite y protección de eventos inmutables.
- `incidents.py`: registro, cambios validados de estado y área, consulta de ficha con historial, listado filtrable y volumen por severidad.
- `tests/`: pruebas con `unittest` y una base de datos en memoria.

## Comprobaciones

Desde la raíz del repositorio:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v
```

Inicializa una base con `createConnection(ruta)` y `initializeDatabase(conexion)`. Usa `registerIncident(conexion, ...)` para registrar una incidencia; `changeIncidentStatus(...)` y `reassignIncidentArea(...)` para cambios validados con evento histórico transaccional; `getIncidentDetails(...)` para consultar la ficha con su historial; `listIncidents(conexion, statusId=..., severityId=..., responsibleAreaId=...)` para listar por filtros opcionales validados; y `getOpenIncidentCountsBySeverity(conexion)` para obtener el volumen de incidencias en estado `nueva`, `enCurso` o `resuelta` agrupado por severidad. El resumen incluye todas las severidades aprobadas, incluso las que tienen cero incidencias.

> Los endpoints HTTP de FastAPI siguen pendientes: la dependencia y el lockfile no se pueden preparar mientras `uv.lock` permanezca excluido.
