# Estado actual

> Se actualiza en cada commit, al menos "Hecho", "En curso" y "Siguiente".

## Hecho
- Paso 01: arranque. Creados `AGENTS.md`, `.agents/rules/` (regla 00) y `memory-bank/`.
- Paso 02: resumen inicial guardado en `memory-bank/registro/resumen-inicial-agente.md`.
- Paso 03: entorno revisado; hallazgos en `memory-bank/registro/hallazgos-entorno.md`.
- Paso 04: resumen inicial contrastado con el repo; discrepancias en `memory-bank/registro/discrepancias.md`.
- Paso 05: seis convenciones evaluadas y propuesta de mejora documentada sin aplicarla.
- Paso 06: pruebas diseñadas y línea base de NC-01–NC-03 registrada.
- Paso 20: ejemplos adicionales NC-01–NC-03 implementados.
- Paso 07: reglas NC-01, NC-02 y NC-03 incorporadas en el commit `c3e6e02`.
- Paso 08: pruebas con subagente registradas en `d354891`; el usuario acepta detenerse ante el conflicto como resultado válido. Reglas conservadas sin ajustes.
- Paso 09: contexto de producto documentado y catálogos validados por el usuario en la ronda 09b.
- Paso 10: stack tecnológico y estructura actual del repositorio documentados.
- Paso 11: plan de implementación versión 1 aprobado y guardado en `7419deb`.
- Paso 12: catálogos aprobados, modelos UUID v4, restricciones SQLite y eventos inmutables implementados en `f7fb380`; 12 pruebas pasan.
- Paso 13: caso de uso SQLite para registrar incidencias y asignar área implementado en `d568bd7`; 20 pruebas pasan. La ruta HTTP permanece pendiente por la restricción de `uv.lock`.
- Paso 14: transiciones, historial de cambios de estado/área y consulta de ficha implementados en `99ba6b1`; 27 pruebas pasan.
- Paso 15: listado con filtros validados por estado, severidad y área responsable implementado en `e88b8ce`; 29 pruebas pasan.
- Paso 16: resumen de incidencias abiertas por severidad implementado en `ffb7701`; 30 pruebas pasan.
- Paso 17: recorrido integrado SQLite completado; registro de evidencia en `memory-bank/registro/verificacion.md`.
- Paso 18: memoria de cierre sincronizada con lo entregado y la limitación HTTP.
- Paso 19a: plan versión 2 aprobado para `http.server`, sin FastAPI ni dependencias; commit `12cfc19`.
- Paso 19b: API JSON y backoffice estático implementados y verificados; 35 pruebas pasan.

## En curso
- Paso 19c: auditoría C01–C15 aprobada y descripción del PR redactada. El usuario autorizó commit, push y PR; falta ejecutar la publicación.

## Siguiente
- Tras abrir el PR contra `main`, esperar revisión; no hacer merge.

## Estado del proyecto
- El repositorio contiene la plantilla monorepo, configuración de devcontainer, reglas para agentes, banco de memoria, ejemplos y metadata de un paquete TypeScript compartido.
- El servicio tiene API JSON con `http.server` de biblioteca estándar, catálogos, modelos, esquema SQLite y casos de uso para registro, cambios trazables, consulta de ficha, listado filtrable y resumen por severidad. El backoffice estático ofrece esos flujos desde el mismo origen.
- No hay comandos globales configurados para lint, pruebas o arranque de una aplicación.

## Decisiones cerradas
| Fecha | Paso | Decisión |
|---|---|---|
| 2026-10-20 | 01 | Las reglas viven en `.agents/rules/`, la memoria en `memory-bank/` y el método en `AGENTS.md` |
| 2026-10-26 | 03 | El entorno base de Python se sincroniza con `uv`; el manifiesto raíz no declara dependencias de aplicación y no configura Docker |
| 2026-10-27 | 09b | Catálogos validados: seis áreas asignables, Dirección Ejecutiva de consulta, tres canales manuales, tipos, severidades, estados y IDs `camelCase` ASCII |
| 2026-10-27 | 10 | El monorepo no configura un workspace pnpm raíz ni comandos globales de lint, pruebas o arranque; el stack de aplicación y la persistencia no están elegidos |
| 2026-10-27 | 11 | UI estática en `uis/backoffice/`, API central FastAPI en `services/`, SQLite estándar, autor manual sin autenticación, fechas UTC mostradas en zona local del navegador; «abierta» incluye `nueva`, `enCurso` y `resuelta` |
| 2026-10-27 | 12 | Los IDs de incidencias y eventos usan UUID v4 en texto; los catálogos aprobados y seis áreas asignables se aplican también en SQLite; historial append-only protegido por triggers |
| 2026-10-27 | 19a | Sustituir FastAPI por `http.server` de biblioteca estándar; no añadir dependencias ni acceder a `uv.lock`; servir API JSON y backoffice estático desde el mismo origen |
| 2026-10-27 | 19b | API y backoffice se implementan y prueban con biblioteca estándar; sin autenticación, el autor se introduce manualmente y el servidor escucha en loopback por defecto |

## Pendientes
- Esperar revisión del PR; no hacer merge.
