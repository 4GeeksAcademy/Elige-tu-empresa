# Banco de memoria — índice

> Qué contiene cada archivo, cuándo leerlo y cuándo actualizarlo. Si añades o renombras un archivo, actualiza este índice en el mismo commit.
> El banco de memoria **describe** el proyecto. Las reglas que **restringen** cómo se trabaja están en `.agents/rules/`, y el método, en `AGENTS.md`.

## Orden de lectura al empezar una sesión

1. `encargo.md`
2. `estado-actual.md`
3. `contexto-producto.md`
4. `stack-tecnologico.md`
5. `plan-implementacion.md`

Si un archivo aún no existe, sáltalo: la columna "Se crea en" indica cuándo aparece.

## Archivos

| Archivo | Qué contiene | Tipo | Se crea en | Se actualiza |
|---|---|---|---|---|
| `encargo.md` | Ticket del CTO, checklist con IDs (tareas y criterios) y plan paso a paso | Núcleo | Paso 01 | Solo si cambia el encargo |
| `estado-actual.md` | Hecho, en curso, siguiente, estado del proyecto, decisiones cerradas y pendientes | Núcleo | Paso 01 | En cada commit |
| `historial-commits.md` | Bitácora: una entrada por commit, con el formato de `.agents/rules/00-commits-y-bitacora.md` | Bajo demanda | Paso 01 | En cada commit |
| `contexto-producto.md` | La empresa, quién usa el backoffice, qué es una incidencia y cuándo es crítica, catálogos y glosario | Núcleo | Paso 09 | Si cambian los catálogos validados |
| `stack-tecnologico.md` | Piezas del monorepo, gestor de dependencias, comandos clave y persistencia | Núcleo | Paso 10 | Si cambia el stack |
| `plan-implementacion.md` | Plan del gestor de incidencias, versionado | Núcleo | Paso 11 | Si cambia el plan, en el mismo commit |
| `registro/resumen-inicial-agente.md` | Resumen inicial del agente, hecho sin contexto (hipótesis; no se edita) | Evidencia | Paso 02 | Nunca |
| `registro/hallazgos-entorno.md` | Comandos para levantar el entorno, sus resultados y lo que no estaba documentado | Evidencia | Paso 03 | — |
| `registro/discrepancias.md` | Contraste del resumen inicial con el repo real | Evidencia | Paso 04 | — |
| `registro/convenciones.md` | Convenciones detectadas en el código, con evidencia | Evidencia | Paso 05 | — |
| `registro/propuestas-mejora.md` | Prácticas mejorables, registradas sin aplicar | Evidencia | Paso 05 | Al añadir propuestas |
| `registro/pruebas-reglas.md` | Pruebas de las reglas: línea base y comportamiento con reglas | Evidencia | Paso 06 | Paso 08 |
| `registro/desviaciones-evitadas.md` | Qué desviaciones evitó cada regla durante el desarrollo | Evidencia | Paso 12 | Durante la implementación |
| `registro/verificacion.md` | Recorrido completo del gestor, con resultados reales | Evidencia | Paso 17 | — |
| `registro/descripcion-pr.md` | Descripción del Pull Request | Evidencia | Paso 19 | — |

- **Núcleo:** se lee al empezar cada sesión. Es conciso: no copia código ni repite lo que se lee en el repo.
- **Bajo demanda y evidencia:** se leen solo cuando hacen falta.
