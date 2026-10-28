# Servicio API de incidencias

API HTTP y casos de uso del gestor centralizado de incidencias de Brasaland. El servidor usa la biblioteca estándar de Python (`http.server`) y la persistencia SQLite.

## Contenido

- `catalogs.py`: canales, tipos, severidades, áreas responsables y estados validados, y los catálogos del inventario (unidades, categorías, tipos de movimiento, motivos de ajuste y locales).
- `models.py`: entidades de incidencia, historial y de artículo, lote y movimiento de inventario, IDs UUID v4 y marcas temporales UTC.
- `database.py`: conexiones, restricciones SQLite, eventos inmutables y las tablas del inventario (movimientos de solo añadir, lotes inmutables y un trigger que impide el stock negativo).
- `incidents.py`: registro, cambios validados de estado y área, consulta de ficha con historial, listado filtrable y volumen por severidad.
- `inventory.py`: casos de uso del inventario: artículos, movimientos de stock, lotes y caducidad, cálculo del stock (`calculateStock`), informe de stock y señal de reorden.
- `inventoryseed.py`: datos semilla del inventario y el comando que los carga.
- `server.py`: API JSON y servidor de archivos estáticos, sin dependencias externas.
- `tests/`: pruebas con `unittest`, una base de datos en memoria y un servidor real en un puerto efímero para la API.
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

## Inventario

El gestor de inventario comparte el servidor y el archivo SQLite (`data/incidents.sqlite`) con las incidencias. El stock disponible nunca se guarda: siempre se calcula a partir de los movimientos de stock. Las cantidades viajan como cadenas decimales (por ejemplo `"12.500"`; `kg` y `l` admiten tres decimales y `g`, `ml` y `unit` no admiten ninguno).

Carga los datos semilla (16 artículos y sus movimientos) desde la raíz del repositorio con:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m services.api.inventoryseed
```

El comando acepta `--database <ruta>` y se rechaza, sin cambiar nada, si la base ya contiene artículos.

La API de inventario está bajo `/api/inventory/`: `GET /catalogs`, `GET` y `POST /items` (el listado acepta el filtro opcional `locationId`), `GET`, `PATCH` y `DELETE /items/{id}`, `POST /items/{id}/movements`, `GET /items/{id}/report` y `GET /locations/{locationId}/reorder`. No existe ninguna ruta para editar el stock ni para modificar o eliminar un movimiento. Los rechazos usan `400` (datos inválidos), `404` (artículo, lote o local inexistente) y `409` (regla de negocio: stock negativo, lote caducado, lote de otro artículo o artículo que ya tiene movimientos).
