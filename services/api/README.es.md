# Servicio API de incidencias

API HTTP y casos de uso del gestor centralizado de incidencias de Brasaland. El servidor usa la biblioteca estándar de Python (`http.server`) y la persistencia SQLite.

## Contenido

- `catalogs.py`: canales, tipos, severidades, áreas responsables y estados validados.
- `models.py`: entidades de incidencia e historial, IDs UUID v4 y marcas temporales UTC.
- `database.py`: conexiones, restricciones SQLite y protección de eventos inmutables.
- `incidents.py`: registro, cambios validados de estado y área, consulta de ficha con historial, listado filtrable y volumen por severidad.
- `server.py`: API JSON y servidor de archivos estáticos, sin dependencias externas.
- `tests/`: pruebas con `unittest` y una base de datos en memoria.
- `uis/backoffice/`: interfaz estática servida desde el mismo origen.

## Comprobaciones

Desde la raíz del repositorio:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v
```

Desde la raíz, inicia el servidor local con:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m services.api.server
```

Abre `http://127.0.0.1:8000/`. El servidor crea `data/incidents.sqlite` y escucha en loopback por defecto.

La API ofrece `GET /api/catalogs`, `GET` y `POST /api/incidents`, `GET /api/incidents/{id}`, `PATCH /api/incidents/{id}/status`, `PATCH /api/incidents/{id}/area` y `GET /api/incidents/summary/by-severity`. El listado acepta filtros opcionales `statusId`, `severityId` y `responsibleAreaId`. Los errores se devuelven como JSON con un estado HTTP correspondiente.

La interfaz estática permite registrar, filtrar, consultar ficha e historial, cambiar estado o área y ver conteos por severidad. Usa el nombre manual para autorizar el registro de auditoría; no hay autenticación.
