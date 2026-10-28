# Estado actual

> Se actualiza en cada commit, al menos "Hecho", "En curso" y "Siguiente".

## Hecho (gestor de incidencias, histórico)
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

## Hecho (gestor de inventario, SDD)
- Paso 01: arranque del encargo. Encargo anterior archivado en `registro/encargo-incidencias.md`, nuevo `encargo.md`, `AGENTS.md` y `memory-bank/README.md` actualizados; commit `2dd43a5`.
- Paso 02: regla `05-desarrollo-guiado-por-spec` creada y `04-nombres-camel-case` ampliada con los valores de catálogo del briefing; commit `9208abc`.
- Paso 03: `specs/inventory-manager/spec.md` v1.0 (INV-001–INV-066) aprobado con P-01–P-08 validadas; commit `464b60c`.
- Paso 04: `specs/inventory-manager/plan.md` v1.0 (PD-01–PD-16) aprobado el 2026-10-28; commit `e739c57`.
- Paso 05: `specs/inventory-manager/tasks.md` v1.0 (T-01–T-29) aprobado el 2026-10-28; commit `2673fd5`.
- Paso 06, T-01: catálogos del inventario (`inventoryCatalogs`); 39 pruebas pasan; commit `8333ab2`.
- Paso 06, T-02: `parseQuantity` y `formatQuantity` en `services/api/inventory.py`; 44 pruebas pasan; commit `0a71518`.
- Paso 06, T-03: tablas `inventoryItems` e `inventoryLots` en `initializeDatabase`; 49 pruebas pasan; commit `806c8d1`.
- Paso 06, T-04: tabla `stockMovements` con `CHECK` de signo y motivo, clave foránea compuesta y triggers de solo añadir; 57 pruebas pasan; commit `b6644dd`.
- Paso 06, T-05: trigger de stock no negativo de artículo y lote, con `stockDeltaSql` compartido; 60 pruebas pasan; commit `e3a3374`.
- Paso 06, T-06: trigger que impide cambiar local, categoría o unidad de un artículo con movimientos; la baja ya la impedía la clave foránea; 63 pruebas pasan; commit `37f144d`.
- Paso 06, T-07: `calculateStock` y modelos de inventario; 68 pruebas pasan; commit `da0e7a4`.
- Paso 06, T-08: `createItem`, `BusinessRuleError` y transacción auxiliar; 73 pruebas pasan; commit `a1bde2f`.
- Paso 06, T-09: `updateItem`; 80 pruebas pasan; commit `4ba0ab7`.
- Paso 06, T-10: `deleteItem`; 83 pruebas pasan; commit `891ea51`.
- Paso 06, T-11: `getItem` y `listItems`; 89 pruebas pasan; commit `b929193`.
- Paso 06, T-12: `registerMovement` para entradas sin lote; 96 pruebas pasan; commit `04da6cd`.
- Paso 06, T-13: salidas con rechazo por stock negativo; 102 pruebas pasan; commit `ce8f7ae`.
- Paso 06, T-14: ajustes con motivo; 108 pruebas pasan; commit `6209939`.
- Paso 06, T-15: pruebas de concurrencia con hilos sobre un archivo; 110 pruebas pasan; commit `2f6895a`.
- Paso 06, T-16: lote obligatorio en `meat` y `produce`; 113 pruebas pasan; commit `cc77f44`.
- Paso 06, T-17: entradas con lote (apertura, suma y rechazos); 120 pruebas pasan; commit `bf1c538`.
- Paso 06, T-18: salidas y ajustes sobre un lote; 125 pruebas pasan; commit `7f79857`.
- Paso 06, T-19: reglas de lotes caducados; 131 pruebas pasan; commit `3f667ba`.
- Paso 06, T-20: `getStockReport` y `expiredLots` en la vista del artículo; 139 pruebas pasan; commit `3195fed`.
- Paso 06, T-21: `getReorderSignal`; 144 pruebas pasan; commit `a03d510`.
- Paso 06, T-22: `inventoryseed.py` con los 16 artículos y sus movimientos; 149 pruebas pasan; commit `d6c83fc`.
- Paso 06, T-23: lote caducado de *Cilantro* en la semilla; 153 pruebas pasan; commit `4c1bf10`.
- Paso 06, T-24: semilla atómica, rechazo con artículos y comando `python -m services.api.inventoryseed`; 158 pruebas pasan; pendiente de commit.

## En curso
- Paso 06 del inventario: T-24 hecha, a la espera de tu `OK commit`.

## Siguiente
- Paso 06 del inventario (modo Agent): T-25 (rutas HTTP de catálogos y artículos), con tests primero.

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
| 2026-10-28 | 01 (inventario) | `company-BRIEFING.md` no existe: el usuario decide usar `CONTEXT.md` como briefing y reconciliar los huecos |
| 2026-10-28 | 03 (inventario) | Spec v1.0 aprobado: P-01 sin campos extra; P-02–P-07 según la propuesta del agente; P-08, solo los 4 locales del encargo |
| 2026-10-28 | 01 (inventario) | No existe la rama `main` (ni local ni remota): el usuario da por válido `6260bb2` (merge del PR #1) como base |

## Pendientes
- `CONTEXT.md` (Brasaland, 14 locales) no contiene el dominio del inventario: ni las entidades, ni el §3.1, §4 y §7 que cita el encargo, ni los cuatro locales (`laArepita`, `queChille`, `theBigSauce`, `chilliBeans`). Se resuelve en el Paso 03: lo que no esté en `CONTEXT.md` ni en el §4 del encargo se marca `pendiente` en el spec.
- Las referencias del encargo a «§2/§3.1/§4/§7 del briefing» no se pueden verificar contra `CONTEXT.md`.
