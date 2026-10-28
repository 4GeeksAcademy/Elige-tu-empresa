# Backoffice de incidencias

Interfaz HTML, CSS y JavaScript sin framework para el gestor de incidencias de Brasaland. No requiere dependencias de frontend: el servicio HTTP de `services/api/` sirve estos archivos y la API JSON desde el mismo origen.

## Funcionalidad

- Registrar incidencias usando los catálogos servidos por la API.
- Filtrar el listado por estado, severidad y área responsable.
- Consultar la ficha y el historial de cambios con autor y fecha local.
- Cambiar estado o reasignar área, indicando el autor del cambio.
- Consultar el volumen de incidencias abiertas por severidad.

## Inventario

La página `/inventory.html` permite gestionar el inventario por local desde la misma aplicación:

- Dar de alta, editar y dar de baja artículos; el stock siempre se calcula desde movimientos y no se edita directamente.
- Registrar entradas, salidas y ajustes, con validaciones de lotes y caducidad de la API.
- Consultar stock, punto de reorden, entradas, salidas, ajustes separados por desperdicio (`waste`), robo (`theft`) y corrección de conteo, y el detalle de lotes.
- Ver la señal de reorden por local y reconocer el stock caducado junto con sus códigos de lote.

Los archivos de la interfaz son `inventory.html` e `inventory.js`; los sirve el mismo origen que la API. La vista del inventario está enlazada desde la navegación superior.

## Ejecución y comprobaciones

Desde la raíz del repositorio:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m services.api.server
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v
```

La interfaz queda en `http://127.0.0.1:8000/`. La base de datos persistente se crea en `data/incidents.sqlite`. Para apagar el servidor, usa `Ctrl+C`.

El servidor escucha en `127.0.0.1` por defecto. No hay autenticación; el nombre de autor se introduce manualmente.
