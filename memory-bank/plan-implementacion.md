# Plan de implementación — Gestor centralizado de incidencias

> **Versión 1 · Paso 11 · 2026-10-27**
> Plan aprobado por el usuario antes de empezar a implementar. Si cambia durante la implementación, actualizar este archivo en el mismo commit que el cambio y registrar el motivo en la bitácora.

## Objetivo y alcance

Centralizar el registro y seguimiento de incidencias de Brasaland: registrar canal, tipo y severidad; asignar un área; recorrer estados; consultar la ficha e historial; filtrar el listado; y ver el volumen de incidencias abiertas por severidad.

Se usan exclusivamente los catálogos y los identificadores validados en [contexto-producto.md](./contexto-producto.md). «Abierta» incluye los estados `nueva`, `enCurso` y `resuelta`; se excluye `cerrada`.

## Decisiones aprobadas

| Tema | Decisión |
|---|---|
| Interfaz | HTML, CSS y JavaScript sin framework, en `uis/backoffice/` |
| API | API central FastAPI bajo `services/`, siguiendo la recomendación del monorepo. El usuario autorizó añadir FastAPI como dependencia. |
| Persistencia | SQLite mediante `sqlite3` de la biblioteca estándar |
| Autor | Nombre manual obligatorio al crear una incidencia y en cada cambio; no se añade autenticación. El nombre no se verifica contra una identidad externa. |
| Marcas temporales | Guardar en UTC y mostrar en la zona horaria local del navegador |
| Pruebas | `unittest` y biblioteca estándar, sin incorporar runner o framework de pruebas |
| IDs | UUID v4 en texto para incidencias y eventos de historial |

## Componentes y ubicación

- `services/api/`: servicio FastAPI central; documentar el componente según las reglas del monorepo.
- `uis/backoffice/`: aplicación interna con interfaz estática; documentar el componente según las reglas del monorepo.
- Crear guías `README.es.md` y `README.md` equivalentes para cada nuevo componente, de acuerdo con la regla bilingüe.
- No crear una carpeta de primer nivel ni mover código compartido fuera de las áreas documentadas.

## Modelo de datos y trazabilidad

### Incidencia

- Identificador.
- Canal, tipo, severidad, área responsable y estado, usando los identificadores aprobados.
- Título y descripción.
- `createdAt`, `updatedAt` y autor de creación (`createdBy`).

### Evento de historial

- Identificador e incidencia asociada.
- Tipo de cambio: cambio de estado o de área responsable.
- Valor anterior y valor nuevo.
- Autor y marca temporal UTC.
- Los eventos son append-only: la API no permite editarlos ni borrarlos y SQLite rechazará operaciones `UPDATE` y `DELETE` sobre ellos.

Cada cambio de estado o de área y su evento de historial se guardan en una única transacción de SQLite. Un fallo en cualquiera de las dos escrituras revierte ambas. La creación registra el estado y el área iniciales en la incidencia; los eventos documentan cambios posteriores.

## Estados y transiciones

| Estado actual | Transición permitida | Estado resultante |
|---|---|---|
| Nueva (`nueva`) | Iniciar atención | En curso (`enCurso`) |
| En curso (`enCurso`) | Resolver | Resuelta (`resuelta`) |
| Resuelta (`resuelta`) | Cerrar | Cerrada (`cerrada`) |
| Resuelta (`resuelta`) | Reabrir antes del cierre | En curso (`enCurso`) |

`cerrada` es terminal. Las demás transiciones se rechazan y no generan un evento de cambio exitoso.

## API e interfaz

- Registrar incidencias con canal, tipo, severidad, área, estado inicial, título, descripción y autor.
- Consultar listado con filtros por estado, severidad y área responsable.
- Consultar la ficha y los eventos históricos en orden cronológico.
- Cambiar estado o área responsable, exigiendo autor y mostrando el evento resultante.
- Mostrar un resumen de incidencias abiertas agrupadas por severidad.
- Formatear las marcas UTC en el navegador para la zona local del usuario.

## Pruebas y verificación

- Ejecutar `unittest` con una base SQLite temporal.
- Comprobar catálogos y validaciones; transiciones válidas y rechazadas; filtros; conteo por severidad; autor, fechas y orden del historial; y atomicidad de la escritura de cambio e historial.
- Verificar manualmente el recorrido de la interfaz y la comunicación con la API.
- En el Paso 17, ejecutar el recorrido integral descrito en `encargo.md` y registrar resultados reales en `memory-bank/registro/verificacion.md`.

## Pasos de implementación

| Paso | Trabajo | IDs y criterios |
|---|---|---|
| 12 | Catálogos, modelo de datos y persistencia SQLite | C13, C14 |
| 13 | Registro de incidencias y asignación a un área | C08 |
| 14 | Transiciones, historial trazable y ficha | C09, C10 |
| 15 | Listado y filtros | C11 |
| 16 | Resumen de incidencias abiertas por severidad | C12 |
| 17 | Verificación de principio a fin y registro de evidencia | V1 |
| 18 | Cierre y actualización de memoria | BM4 |
| 19 | Auditoría, descripción del PR y entrega | EN1–EN4, V3; cualquier acción remota requiere autorización explícita |

Cada paso se implementa en un commit separado, con sus IDs en el asunto/cuerpo según la regla 00. Se revisa y valida cada porción antes del commit.

## Estado de entrega al cierre del Paso 18

| Paso | Estado | Evidencia o desviación |
|---|---|---|
| 12 | Completado | Catálogos, modelos y persistencia SQLite; `f7fb380` |
| 13 | Completado en la capa de casos de uso | Registro y asignación SQLite; `d568bd7`. Endpoint HTTP aplazado por la restricción documentada sobre `uv.lock`. |
| 14 | Completado en la capa de casos de uso | Estados, historial y ficha; `99ba6b1` |
| 15 | Completado en la capa de casos de uso | Listado y filtros; `e88b8ce` |
| 16 | Completado en la capa de casos de uso | Resumen por severidad; `ffb7701` |
| 17 | Completado para SQLite | Recorrido integrado registrado en `registro/verificacion.md`; HTTP e interfaz no se verificaron porque no están implementados. |
| 18 | En revisión | Sincronización de la memoria de cierre. |
| 19 | Pendiente | Auditoría y descripción del PR; las acciones remotas requieren autorización explícita. |

**Desviación de alcance:** la API FastAPI y el backoffice estático aprobados en el plan no se entregaron en los pasos 12–17. Se mantienen pendientes para no alterar la exclusión organizativa de `uv.lock`, de acuerdo con la decisión expresa del usuario. La lógica y persistencia SQLite sí se implementaron y verificaron.

## Pendientes de implementación y decisiones técnicas

- FastAPI está aprobado como dependencia, pero su integración queda pendiente hasta gestionar la dependencia sin acceder a `uv.lock`, que permanece excluido por la política organizativa.
- No añadir dependencias aparte de FastAPI sin autorización adicional.
- Docker y despliegue no están incluidos en el alcance aprobado; no configurarlos como parte de estos pasos.

## Restricción de entorno registrada durante el Paso 13

El entorno no tiene `uv` y la política organizativa excluye `uv.lock`. Para respetar esa restricción, el Paso 13 entrega el caso de uso de registro sobre SQLite sin añadir FastAPI ni exponer todavía un endpoint HTTP. No se lee, edita ni se intenta actualizar el lockfile. La exposición HTTP queda pendiente hasta que pueda gestionarse la dependencia sin acceder al archivo excluido.

## Fuera de alcance

- Autenticación, autorización y permisos.
- Integración automática con WhatsApp, teléfono, email o puntos de venta.
- SLA, escalados, catálogo de locales o proveedores.
- Los demás productos descritos en el briefing, como CRM, pedidos, RRHH, formación y compras.
- Framework de UI, framework de pruebas o dependencias adicionales no aprobadas.
