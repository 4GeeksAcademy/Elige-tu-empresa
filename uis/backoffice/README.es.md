# Backoffice de incidencias

Interfaz HTML, CSS y JavaScript sin framework para el gestor de incidencias de Brasaland. No requiere dependencias de frontend: el servicio HTTP de `services/api/` sirve estos archivos y la API JSON desde el mismo origen.

## Funcionalidad

- Registrar incidencias usando los catálogos servidos por la API.
- Filtrar el listado por estado, severidad y área responsable.
- Consultar la ficha y el historial de cambios con autor y fecha local.
- Cambiar estado o reasignar área, indicando el autor del cambio.
- Consultar el volumen de incidencias abiertas por severidad.

## Ejecución y comprobaciones

Desde la raíz del repositorio:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m services.api.server
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v
```

La interfaz queda en `http://127.0.0.1:8000/`. La base de datos persistente se crea en `data/incidents.sqlite`. Para apagar el servidor, usa `Ctrl+C`.

El servidor escucha en `127.0.0.1` por defecto. No hay autenticación; el nombre de autor se introduce manualmente.
