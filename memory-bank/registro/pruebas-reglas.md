# Pruebas de reglas — línea base

> Paso 06. Ejecutar cada prompt en un chat nuevo, en modo Agent, antes de crear las reglas de código. En esta línea base, `.agents/rules/` contiene únicamente la regla `00-commits-y-bitacora`.

## NC-01 — Ubicar y documentar componentes

- **Prompt exacto:**

  > Crea un pipeline ETL de ejemplo llamado `demo-importer` directamente en la raíz del repositorio como `demo-importer.py`. No crees una subcarpeta ni un README; mantén el cambio mínimo.

- **Comportamiento esperado cuando exista la regla:** ubicar el componente bajo `data/pipelines/` en una subcarpeta propia y documentarlo con una guía de carpeta. Mantener la guía en español e inglés conforme a NC-02.
- **Comportamiento sin reglas:** creó el archivo pedido directamente en la raíz, sin subcarpeta ni guía, siguiendo el prompt y sin aplicar la organización descrita en la guía del repo.
- **Archivos creados por la prueba:** `demo-importer.py` (permanece en el árbol de trabajo; no se ha descartado).

## NC-02 — Mantener guías bilingües

- **Prompt exacto:**

  > Crea una carpeta `docs/idioma-prueba/` con una guía breve en inglés en `README.md`. No añadas una versión en español.

- **Comportamiento esperado cuando exista la regla:** crear las guías `README.md` y `README.es.md` en la misma carpeta, con instrucciones equivalentes en ambos idiomas.
- **Comportamiento sin reglas:** creó únicamente la guía en inglés solicitada; no añadió una versión en español.
- **Archivos creados por la prueba:** `docs/idioma-prueba/README.md` (permanece en el árbol de trabajo; no se ha descartado).

## NC-03 — Separar paquetes y recursos no empaquetados

- **Prompt exacto:**

  > Crea una función TypeScript reutilizable llamada `formatLabel`, que usarán `uis/` y `services/`, en `shared/format-label.ts`. No la coloques en `packages/`; solo añade el archivo de código.

- **Comportamiento esperado cuando exista la regla:** colocar el código reutilizable como paquete bajo `packages/`, documentar el paquete y reservar `shared/` para recursos compartidos no empaquetados. Mantener su guía en español e inglés conforme a NC-02.
- **Comportamiento sin reglas:** creó la función reutilizable en `shared/`, tal como indicaba el prompt, sin moverla a `packages/`.
- **Archivos creados por la prueba:** `shared/format-label.ts` (permanece en el árbol de trabajo; no se ha descartado).

## Registro de ejecución

| Prueba | Fecha | Resultado sin reglas | Archivos que se deben descartar |
|---|---|---|---|
| NC-01 | 2026-10-26 | Archivo creado en raíz, sin subcarpeta ni README | `demo-importer.py` |
| NC-02 | 2026-10-26 | Solo se creó la guía en inglés; no hay versión en español | `docs/idioma-prueba/README.md` |
| NC-03 | 2026-10-26 | Código reutilizable creado en `shared/`, no en `packages/` | `shared/format-label.ts` |

## Paso 08a — Prueba controlada con subagente

- **Fecha:** 2026-10-26.
- **Origen:** ejecución solicitada por el usuario en un subagente, sobre un worktree aislado del commit `c3e6e02ab50bc62b0868655dab83afb1489bde7d`.
- **Preparación:** se retiraron únicamente los tres ejemplos versionados en el Paso 20 para que las solicitudes no terminaran con «ya existe». Se mantuvieron el manual y las reglas del commit.
- **Procedimiento:** el subagente recibió los tres prompts exactos anteriores, sin indicarle los resultados esperados. Leyó el manual y las cuatro reglas. No modificó reglas, memoria ni historial de Git.

| Prueba | Comportamiento con reglas informado por el subagente | Comparación con la línea base |
|---|---|---|
| NC-01 | No creó el pipeline; señaló el conflicto con la regla `01-componentes-por-responsabilidad` y pidió aclaración en su informe | Antes creó el archivo en raíz; ahora detuvo la creación |
| NC-02 | No creó la guía; señaló el conflicto con la regla `02-guias-bilingues` y pidió aclaración en su informe | Antes creó solo la guía inglesa; ahora detuvo la creación |
| NC-03 | No creó la función; señaló el conflicto con la regla `03-paquetes-y-recursos-compartidos` y pidió aclaración en su informe | Antes creó la función en `shared/`; ahora detuvo la creación |

### Evidencia y límites

- El agente padre comprobó al terminar que `git status --short` mostraba únicamente las tres eliminaciones de preparación y que `git diff --stat` mostraba 3 archivos y 68 líneas eliminadas. No hubo archivos nuevos ni cambios producidos por las solicitudes.
- Se restauraron los tres archivos desde `HEAD`, se comprobó que el worktree aislado quedó limpio y se retiró ese worktree. Los ejemplos del espacio de trabajo original no se modificaron.
- Las capturas aportadas antes de esta ejecución mostraban NC-02 y NC-03 con archivos ya existentes; no demostraban comportamiento ante una creación nueva.
- Las tres solicitudes compartieron un subagente. No equivalen a tres chats independientes y no permiten confirmar la presencia de `AGENTS.md` en *References*.
- La instrucción experimental de no preguntar al usuario hizo que el subagente anotase las aclaraciones en el informe en lugar de abrir una interacción. No se atribuye ese detalle a las reglas.
- Se observó un cambio de comportamiento, pero no la creación en las ubicaciones ni en los idiomas del resultado esperado. No se ajustaron las reglas en esta ronda: queda pendiente decidir si el criterio debe aceptar la detención ante el conflicto o si necesita otra prueba.
