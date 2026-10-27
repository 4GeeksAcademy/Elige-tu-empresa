# Plan de implementación — Gestor centralizado de incidencias

> **Versión 2 · Paso 19a · 2026-10-27**
> La versión 1 fue aprobada en el Paso 11. Esta versión incorpora el cambio de arquitectura solicitado por el usuario después del Paso 18; su aprobación y registro se hacen antes de implementar el servidor.

## Objetivo y alcance

Centralizar el registro y seguimiento de incidencias de Brasaland: registrar canal, tipo y severidad; asignar un área; recorrer estados; consultar la ficha e historial; filtrar el listado; y ver el volumen de incidencias abiertas por severidad.

Se usan exclusivamente los catálogos y los identificadores validados en [contexto-producto.md](./contexto-producto.md). «Abierta» incluye los estados `nueva`, `enCurso` y `resuelta`; se excluye `cerrada`.

## Decisiones aprobadas

| Tema | Decisión |
|---|---|
| Interfaz | HTML, CSS y JavaScript sin framework, en `uis/backoffice/` |
| API | API JSON en `services/api/`, servida con `http.server` de la biblioteca estándar de Python; no se añade FastAPI ni otra dependencia. |
| Persistencia | SQLite mediante `sqlite3` de la biblioteca estándar |
| Autor | Nombre manual obligatorio al crear una incidencia y en cada cambio; no se añade autenticación. El nombre no se verifica contra una identidad externa. |
| Marcas temporales | Guardar en UTC y mostrar en la zona horaria local del navegador |
| Pruebas | `unittest` y biblioteca estándar, sin incorporar runner o framework de pruebas |
| IDs | UUID v4 en texto para incidencias y eventos de historial |

## Componentes y ubicación

- `services/api/`: servicio HTTP JSON de biblioteca estándar; documentar el componente según las reglas del monorepo.
- `uis/backoffice/`: aplicación interna con interfaz estática; documentar el componente según las reglas del monorepo.
- Crear guías `README.es.md` y `README.md` equivalentes para cada nuevo componente, de acuerdo con la regla bilingüe.
- No crear una carpeta de primer nivel ni mover código compartido fuera de las áreas documentadas.

La API estándar servirá los archivos estáticos del backoffice desde el mismo origen. El servidor se limitará por defecto a `127.0.0.1`, y abrirá una conexión SQLite por solicitud.

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

### Contrato HTTP sin dependencias externas

- `GET /api/catalogs`: devolver los catálogos validados para los controles del backoffice.
- `GET /api/incidents`: aceptar los filtros opcionales `statusId`, `severityId` y `responsibleAreaId`.
- `POST /api/incidents`: registrar los campos aprobados y el autor manual.
- `GET /api/incidents/{id}`: devolver la incidencia y el historial.
- `PATCH /api/incidents/{id}/status`: aplicar una transición con `statusId` y `author`.
- `PATCH /api/incidents/{id}/area`: reasignar con `responsibleAreaId` y `author`.
- `GET /api/incidents/summary/by-severity`: devolver los conteos de incidencias abiertas.
- La UI HTML/CSS/JavaScript permitirá registrar, filtrar, consultar ficha e historial, cambiar estado/área y visualizar los conteos.
- El servidor usará solo `http.server`, `json`, `urllib.parse` y demás biblioteca estándar; los datos seguirán pasando por los casos de uso existentes. No habrá CORS ni dependencia de un servicio externo.

## Pruebas y verificación

- Ejecutar `unittest` con una base SQLite temporal.
- Comprobar catálogos y validaciones; transiciones válidas y rechazadas; filtros; conteo por severidad; autor, fechas y orden del historial; y atomicidad de la escritura de cambio e historial.
- Probar las rutas HTTP con `unittest`, servidor local y base SQLite temporal; verificar también que la UI estática se sirve por HTTP.
- Verificar el recorrido de interfaz y API en local, sin datos persistentes de prueba.
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
| 19a | Actualizar el plan aprobado para usar HTTP estándar sin dependencias | C06, C12, C14 |
| 19b | Implementar API JSON y backoffice estático; verificar el recorrido HTTP | C06, C08–C14, V1, V2 |
| 19c | Auditoría y descripción del PR | EN1–EN4, V3; cualquier acción remota requiere autorización explícita |

Cada paso se implementa en un commit separado, con sus IDs en el asunto/cuerpo según la regla 00. Se revisa y valida cada porción antes del commit.

## Estado de entrega al cierre del Paso 19b

| Paso | Estado | Evidencia o desviación |
|---|---|---|
| 12 | Completado | Catálogos, modelos y persistencia SQLite; `f7fb380` |
| 13 | Completado | Registro y asignación SQLite; el endpoint HTTP se implementó y verificó en el Paso 19b. |
| 14 | Completado en la capa de casos de uso | Estados, historial y ficha; `99ba6b1` |
| 15 | Completado en la capa de casos de uso | Listado y filtros; `e88b8ce` |
| 16 | Completado en la capa de casos de uso | Resumen por severidad; `ffb7701` |
| 17 | Completado | Recorrido de dominio SQLite registrado en `registro/verificacion.md`; la misma evidencia se amplió con el recorrido HTTP del Paso 19b. |
| 18 | Completado | Memoria de cierre sincronizada; `efd5492`. |
| 19a | Completado | Plan versión 2 para `http.server`, sin dependencias; `12cfc19`. |
| 19b | Completado | API JSON, backoffice estático y 35 pruebas aprobadas. |
| 19c | Pendiente | Auditoría y descripción del PR; las acciones remotas requieren autorización explícita. |

**Cambio de arquitectura solicitado:** el usuario confirmó que no se use FastAPI y aprobó `http.server` de la biblioteca estándar, API JSON y backoffice estático. No se modificarán ni se leerán `uv.lock`; no se añadirán dependencias. La integración HTTP y la UI se implementarán en el Paso 19b, después de registrar esta versión del plan.

## Pendientes y decisiones técnicas

- Auditar C01–C15 y redactar la descripción del PR en el Paso 19c.
- No añadir dependencias de aplicación sin autorización adicional.
- Docker y despliegue no están incluidos en el alcance aprobado; no configurarlos como parte de estos pasos.

## Fuera de alcance

- Autenticación, autorización y permisos.
- Integración automática con WhatsApp, teléfono, email o puntos de venta.
- SLA, escalados, catálogo de locales o proveedores.
- Los demás productos descritos en el briefing, como CRM, pedidos, RRHH, formación y compras.
- Framework de UI, framework de pruebas o dependencias adicionales no aprobadas.
