# Servicio API de incidencias

Base de datos y modelos del gestor centralizado de incidencias de Brasaland. La persistencia usa SQLite de la biblioteca estándar de Python y los catálogos aprobados del proyecto.

## Contenido

- `catalogs.py`: canales, tipos, severidades, áreas responsables y estados validados.
- `models.py`: entidades de incidencia e historial, IDs UUID v4 y marcas temporales UTC.
- `database.py`: conexiones, restricciones SQLite y protección de eventos inmutables.
- `tests/`: pruebas con `unittest` y una base de datos en memoria.

## Comprobaciones

Desde la raíz del repositorio:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v
```

Inicializa una base con `createConnection(ruta)` y `initializeDatabase(conexion)`. El llamador es responsable de cerrar la conexión. Los cambios de incidencia y sus eventos de historial se incorporarán en la misma transacción en el paso de trazabilidad.

> Esta base de persistencia aún no expone endpoints HTTP.
