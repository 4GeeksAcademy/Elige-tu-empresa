# Verificación de principio a fin

**Paso:** 17 · **Fecha:** 2026-10-27

El recorrido se ejecutó contra una base SQLite temporal mediante los casos de uso del servicio. No se usaron datos persistentes del proyecto.

| Escenario | Pasos | Esperado | Obtenido | ✅/❌ |
|---|---|---|---|---|
| Registro por canal, clasificación y asignación | Crear tres incidencias con `whatsapp`, `telefono` y `email`, asignando tipo, severidad y área válidos a cada una | Las tres incidencias se persisten con los valores aprobados | Se registraron las tres; los canales, tipos, severidades y áreas coincidieron con los valores enviados | ✅ |
| Reasignación de área | Cambiar una incidencia de `operacionesRestaurante` a `comprasProveedores` | El área nueva queda persistida y el cambio aparece en el historial | Área actualizada y evento con valor anterior `operacionesRestaurante` y nuevo `comprasProveedores` | ✅ |
| Ciclo completo | Cambiar una incidencia de `nueva` a `enCurso`, `resuelta` y `cerrada` | Se completa el ciclo permitido y `cerrada` queda como estado final | Se completó `nueva → enCurso → resuelta → cerrada` | ✅ |
| Transición prohibida | Intentar `nueva → resuelta` | Se rechaza y no crea evento | Se recibió `ValueError`; el historial permaneció vacío | ✅ |
| Ficha e historial de estado | Consultar la incidencia después de los cambios de estado | La ficha refleja el estado actual y el historial ordenado contiene autor y marcas UTC | La ficha mostró `resuelta` antes del cierre y los eventos `enCurso`, `resuelta`, con el autor esperado y marcas con zona UTC | ✅ |
| Historial de reasignación | Consultar la ficha de la incidencia reasignada | El evento muestra área anterior/nueva, autor y marca temporal UTC | El evento registró ambas áreas; la prueba integrada comprobó autor y UTC en el historial | ✅ |
| Filtro por estado | Consultar el listado con `statusId="resuelta"` antes del cierre | Solo aparecen incidencias resueltas | Aparecieron las dos incidencias en `resuelta` | ✅ |
| Filtro por severidad | Consultar el listado con `severityId="alta"` | Solo aparece la incidencia de severidad alta | Apareció únicamente la incidencia telefónica de severidad alta | ✅ |
| Filtro por área responsable | Consultar con `responsibleAreaId="comprasProveedores"` | Solo aparece la incidencia reasignada a esa área | Apareció únicamente la incidencia reasignada | ✅ |
| Resumen antes del cierre | Consultar el volumen tras dejar una incidencia en cada severidad abierta (`nueva`, `enCurso` o `resuelta`) | Conteos: crítica 1, alta 1, media 1, baja 0 | `{'critica': 1, 'alta': 1, 'media': 1, 'baja': 0}` | ✅ |
| Resumen después del cierre | Cerrar la incidencia crítica y consultar de nuevo | La crítica deja de contarse; las demás permanecen | `{'critica': 0, 'alta': 1, 'media': 1, 'baja': 0}` | ✅ |

## Alcance y limitaciones

- La comprobación de extremo a extremo cubre los casos de uso SQLite y el flujo de dominio. La API HTTP y la interfaz no se verificaron porque todavía no hay endpoint ni backoffice ejecutable; FastAPI sigue aplazado por la restricción acordada sobre `uv.lock`.
- Comprobación adicional: `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v` → 30 pruebas pasan.
