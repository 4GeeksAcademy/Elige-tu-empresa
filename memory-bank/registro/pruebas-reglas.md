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
