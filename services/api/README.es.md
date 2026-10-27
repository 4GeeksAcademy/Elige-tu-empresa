# Servicio API de incidencias

Base de datos y modelos del gestor centralizado de incidencias de Brasaland. La persistencia usa SQLite de la biblioteca estándar de Python y los catálogos aprobados del proyecto.

## Contenido

- `catalogs.py`: canales, tipos, severidades, áreas responsables y estados validados.
- `models.py`: entidades de incidencia e historial, IDs UUID v4 y marcas temporales UTC.
- `database.py`: conexiones, restricciones SQLite y protección de eventos inmutables.
- `incidents.py`: validación y registro de incidencias en su estado inicial.
- `tests/`: pruebas con `unittest` y una base de datos en memoria.

## Comprobaciones

Desde la raíz del repositorio:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v
```

Inicializa una base con `createConnection(ruta)` y `initializeDatabase(conexion)`. Registra una incidencia con `registerIncident(conexion, ...)`; valida los catálogos y persiste el autor y las marcas UTC. La función devuelve el modelo creado. El llamador es responsable de cerrar la conexión.

> Los endpoints HTTP de FastAPI siguen pendientes: la dependencia y el lockfile no se pueden preparar mientras `uv.lock` permanezca excluido.
