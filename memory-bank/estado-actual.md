# Estado actual

> Se actualiza en cada commit, al menos "Hecho", "En curso" y "Siguiente".

## Hecho
- Paso 01: arranque. Creados `AGENTS.md`, `.agents/rules/` (regla 00) y `memory-bank/`.
- Paso 02: resumen inicial guardado en `memory-bank/registro/resumen-inicial-agente.md`.
- Paso 03: entorno revisado; hallazgos en `memory-bank/registro/hallazgos-entorno.md`.
- Paso 04: resumen inicial contrastado con el repo; discrepancias en `memory-bank/registro/discrepancias.md`.

## En curso
- —

## Siguiente
- Paso 05: identificar convenciones y registrar propuestas de mejora.

## Estado del proyecto
- El gestor de incidencias no existe todavía.
- El repositorio no tenía reglas para agentes ni banco de memoria antes de este trabajo.

## Decisiones cerradas
| Fecha | Paso | Decisión |
|---|---|---|
| 2026-10-20 | 01 | Las reglas viven en `.agents/rules/`, la memoria en `memory-bank/` y el método en `AGENTS.md` |
| 2026-10-26 | 03 | El entorno base de Python se sincroniza con `uv`; el manifiesto raíz no declara dependencias de aplicación y no configura Docker |

## Pendientes
- Decidir el stack de ejecución del gestor, si se usará Docker y qué dependencias de aplicación declarar. El entorno base de `uv` ya funciona, pero está vacío.
