# Banco de memoria — índice

> Qué contiene cada archivo, cuándo leerlo y cuándo actualizarlo. Si añades o renombras un archivo, actualiza este índice en el mismo commit.
> El banco de memoria **describe** el proyecto. Las reglas que **restringen** cómo se trabaja están en `.agents/rules/`, y el método, en `AGENTS.md`.

## Orden de lectura al empezar una sesión

1. `encargo.md`
2. `estado-actual.md`
3. `contexto-producto.md`
4. `stack-tecnologico.md`
5. `specs/inventory-manager/` (`spec.md`, `plan.md`, `tasks.md`), en la raíz del repo, cuando existan

`plan-implementacion.md` y `registro/encargo-incidencias.md` son históricos del gestor de incidencias: se leen bajo demanda.

Si un archivo aún no existe, sáltalo: la columna "Se crea en" indica cuándo aparece (los pasos de los archivos del encargo de incidencias son de aquel encargo; los de inventario se marcan "Inventario, Paso NN").

## Archivos

| Archivo | Qué contiene | Tipo | Se crea en | Se actualiza |
|---|---|---|---|---|
| `README.md` | Índice de archivos y orden de lectura de la memoria | Núcleo | Paso 01 | Al añadir o renombrar archivos |
| `encargo.md` | Encargo en curso: gestor de inventario (SDD); ticket del CTO, decisiones de dominio y plan paso a paso | Núcleo | Inventario, Paso 01 | Solo si cambia el encargo |
| `estado-actual.md` | Hecho, en curso, siguiente, estado del proyecto, decisiones cerradas y pendientes | Núcleo | Paso 01 | En cada commit |
| `historial-commits.md` | Bitácora: una entrada por commit, con el formato de `.agents/rules/00-commits-y-bitacora.md` | Bajo demanda | Paso 01 | En cada commit |
| `contexto-producto.md` | La empresa, usuarios propuestos, incidencias, catálogos y glosario; borrador con valores pendientes de validación | Núcleo | Paso 09 | Si cambian los catálogos validados |
| `stack-tecnologico.md` | Piezas del monorepo, gestor de dependencias, comandos clave y persistencia | Núcleo | Paso 10 | Si cambia el stack |
| `plan-implementacion.md` | Plan del gestor de incidencias, versionado (histórico, bajo demanda) | Evidencia | Paso 11 | Nunca |
| `registro/encargo-incidencias.md` | Encargo anterior, el gestor de incidencias, ya mergeado en `main` (histórico, bajo demanda) | Evidencia | Inventario, Paso 01 | Nunca |
| `registro/resumen-inicial-agente.md` | Resumen inicial del agente, hecho sin contexto (hipótesis; no se edita) | Evidencia | Paso 02 | Nunca |
| `registro/hallazgos-entorno.md` | Comandos para levantar el entorno, sus resultados y lo que no estaba documentado | Evidencia | Paso 03 | — |
| `registro/discrepancias.md` | Contraste del resumen inicial con el repo real | Evidencia | Paso 04 | — |
| `registro/convenciones.md` | Convenciones detectadas en el código, con evidencia | Evidencia | Paso 05 | — |
| `registro/propuestas-mejora.md` | Prácticas mejorables, registradas sin aplicar | Evidencia | Paso 05 | Al añadir propuestas |
| `registro/pruebas-reglas.md` | Pruebas de las reglas: línea base y comportamiento con reglas | Evidencia | Paso 06 | Paso 08 |
| `registro/verificacion.md` | Recorrido completo del gestor, con resultados reales | Evidencia | Paso 17 | — |
| `registro/descripcion-pr.md` | Descripción del Pull Request (prevista) | Evidencia | Paso 19 | — |
| `registro/trazabilidad-inventario.md` | Tabla INV → tarea → test → commit del gestor de inventario | Evidencia | Inventario, Paso 07 | Al cerrar un cambio de requisito |
| `registro/verificacion-inventario.md` | Recorrido real con los datos semilla y sus resultados | Evidencia | Inventario, Paso 07 | — |
| `registro/cambio-requisito-inventario.md` | Texto literal del cambio de requisito, análisis de impacto y cierre | Evidencia | Inventario, Paso 08 | Durante el cambio |
| `registro/descripcion-pr-inventario.md` | Descripción del Pull Request del inventario (prevista) | Evidencia | Inventario, Paso 09 | — |

## Spec, plan y tareas del inventario

Viven fuera de la memoria, en [`specs/inventory-manager/`](../specs/inventory-manager/) (se crean en los Pasos 03–05 del encargo): el spec es el qué, el plan es el cómo y las tareas son el orden. La memoria los enlaza y no los copia.

- **Núcleo:** se lee al empezar cada sesión. Es conciso: no copia código ni repite lo que se lee en el repo.
- **Bajo demanda y evidencia:** se leen solo cuando hacen falta.
