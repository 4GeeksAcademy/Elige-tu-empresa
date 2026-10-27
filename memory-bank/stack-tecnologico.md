# Stack tecnológico y estructura del repositorio

> La primera sección conserva el estado de la plantilla observado en el Paso 10. La sección final registra el estado del servicio al cierre del Paso 18.

## Piezas del monorepo

La guía raíz define estas responsabilidades para las carpetas del proyecto:

| Carpeta | Responsabilidad |
|---|---|
| `uis/` | Interfaces y aplicaciones frontend |
| `services/` | API centralizada de la empresa; la guía propone FastAPI |
| `data/` | Datos, pipelines y evaluación |
| `agents/`, `skills/`, `mcps/` | Agentes, capacidades reutilizables y servidores MCP |
| `workflows/` | Automatizaciones y orquestación |
| `packages/` | Código reutilizable empaquetable; actualmente hay metadata para `@repo/shared-types` |
| `shared/` | Recursos compartidos que no son paquetes |
| `infra/`, `scripts/`, `internal/` | Infraestructura, scripts auxiliares y herramientas internas |
| `docs/` | Documentación transversal |

La guía de estructura y las reglas aplicables a componentes y recursos compartidos están en [README.es.md](../README.es.md), [regla 01](../.agents/rules/01-componentes-por-responsabilidad.md) y [regla 03](../.agents/rules/03-paquetes-y-recursos-compartidos.md).

## Dependencias y comandos

- **Python:** `pyproject.toml` declara Python `>=3.12`, no declara dependencias de aplicación y configura `uv` para no empaquetar el proyecto. El comando de sincronización configurado en el entorno de desarrollo es `uv sync`.
- **JavaScript/TypeScript:** el script del devcontainer intenta habilitar Corepack y activar `pnpm@latest`, pero ignora errores de esos comandos. Hay metadata en `packages/shared/package.json`, sin scripts; no hay workspace pnpm raíz configurado.
- **Preparación del devcontainer:** `bash .devcontainer/post-create.sh`. El script instala `pip` y `uv`, activa pnpm si está disponible y ejecuta `uv sync`.
- **Lint, tests y arranque:** el repositorio no define comandos globales para esas tareas ni una aplicación de incidencias que arrancar. No se encontró configuración de lint ni un runner de pruebas del proyecto.

La presencia del script de preparación no implica que exista un stack de aplicación. El devcontainer reserva puertos y monta el socket de Docker, pero no hay una configuración `docker-compose.yml` en la raíz.

## Estado del gestor al cierre del Paso 18

- **Servicio:** `services/api/` contiene casos de uso Python para registrar y consultar incidencias, cambiar estado y área, listar con filtros y resumir incidencias abiertas por severidad.
- **Persistencia:** SQLite mediante `sqlite3` de la biblioteca estándar. El esquema y las restricciones se inicializan desde `database.py`; las pruebas usan bases temporales o en memoria.
- **Pruebas:** `unittest` de la biblioteca estándar; se ejecutan con `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v`.
- **Dependencias de aplicación:** no se añadieron dependencias. FastAPI continúa siendo el framework aprobado para la futura API HTTP, pero no se incorporó porque `uv.lock` está excluido por la política organizativa y el usuario pidió mantener esa restricción.
- **Interfaz:** el backoffice estático todavía no se implementó. No hay endpoints HTTP ni una aplicación que arrancar; los pasos 12–17 verificaron los casos de uso SQLite.
- **Pendiente:** decidir una forma de gestionar FastAPI que respete la exclusión de `uv.lock`; no acceder, modificar ni intentar regenerar ese archivo.

## Reglas del agente

Consulta las reglas del repositorio antes de trabajar; no se repiten aquí: [00 — commits y bitácora](../.agents/rules/00-commits-y-bitacora.md), [01 — componentes por responsabilidad](../.agents/rules/01-componentes-por-responsabilidad.md), [02 — guías bilingües](../.agents/rules/02-guias-bilingues.md) y [03 — paquetes y recursos compartidos](../.agents/rules/03-paquetes-y-recursos-compartidos.md).

## Fuentes

- [Guía del monorepo](../README.es.md): responsabilidades de carpetas y estado de la plantilla.
- `pyproject.toml`, `packages/shared/package.json` y `.devcontainer/post-create.sh`: configuración y comandos existentes.
- [Hallazgos del entorno](./registro/hallazgos-entorno.md): resultados observados al preparar el entorno y ausencia de comandos generales de lint, tests y arranque.
