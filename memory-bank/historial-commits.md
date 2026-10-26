# Historial de commits (bitácora)

> Una entrada por commit, en el formato de `.agents/rules/00-commits-y-bitacora.md`.

## Paso 01 — Arranque
- **Fecha:** 2026-10-20
- **Modo:** Agent
- **Checklist:** E1, E3, RG1, BM1 · **Criterios:** C15
- **Qué se hizo:**
  - Comprobado el punto de partida: rama `feature/incident-manager`, rama principal `main` (en el remoto), sin `AGENTS.md`, `.agents/` ni `memory-bank/`.
  - `resumen.md` (Anexo A) está sin seguir en git; no se incluye en este commit.
  - Analizado `git log`: 1 commit (`1.Eleccion de empresa e idea de agente`), sin prefijo ni cuerpo; no hay convención de commits.
  - Creadas las carpetas `.agents/rules/`, `memory-bank/` y `memory-bank/registro/`.
  - Creados `AGENTS.md`, `memory-bank/encargo.md`, `memory-bank/README.md`, `memory-bank/estado-actual.md` y la regla 00.
- **Archivos:**
  - `AGENTS.md` — manual de trabajo del agente
  - `.agents/rules/00-commits-y-bitacora.md` — regla de commits y bitácora (`origen: encargo`)
  - `memory-bank/encargo.md` — ticket, checklist y plan paso a paso
  - `memory-bank/README.md` — índice de la memoria
  - `memory-bank/estado-actual.md` — estado del trabajo
  - `memory-bank/historial-commits.md` — esta bitácora
- **Reglas aplicadas:** 00-commits-y-bitacora
- **Decisiones y pendientes:**
  - La regla 00 es `origen: encargo` porque `git log` no muestra convención. El formato del asunto (Conventional Commits en español) lo propone el encargo y queda pendiente de validar.
  - Comprobar con el usuario que `AGENTS.md` aparece en *References* en un chat nuevo en modo Ask.
- **Desviaciones evitadas:** ninguna
- **Cambios respecto al plan:** ninguno
- **Commit:** `chore(memory-bank): crear manual del agente, banco de memoria y regla 00`

## Paso 02 — Resumen inicial (la hipótesis)
- **Fecha:** 2026-10-20
- **Modo:** Agent (el resumen se generó en modo Ask)
- **Checklist:** RC1, E4 · **Criterios:** —
- **Qué se hizo:**
  - Copiado el Anexo A (`resumen.md`) literalmente en `memory-bank/registro/resumen-inicial-agente.md`, con `cp`.
  - Añadida una cabecera con la fecha, el modo (Ask) y la nota de no editar.
  - Comprobado con `diff` que el cuerpo es idéntico a `resumen.md`.
- **Archivos:** `memory-bank/registro/resumen-inicial-agente.md` — hipótesis de partida, sin corregir ni comentar (el contraste es el Paso 04)
- **Reglas aplicadas:** 00-commits-y-bitacora
- **Decisiones y pendientes:** `resumen.md` de la raíz sigue sin seguir en git y no se commitea; el usuario decide si lo borra.
- **Desviaciones evitadas:** ninguna
- **Cambios respecto al plan:** ninguno
- **Commit:** `docs(memory-bank): guardar el resumen inicial del agente`

## Paso 03 — Levantar el entorno
- **Fecha:** 2026-10-26
- **Modo:** Agent
- **Checklist:** E2 · **Criterios:** —
- **Qué se hizo:**
  - Revisado solo lo que documenta el repo: README, `.devcontainer/`, `packages/shared/package.json` y el script de pandas.
  - Ejecutado `bash .devcontainer/post-create.sh`: falla (`corepack` y `pip` no existen en este entorno Alpine); no se llegó a `uv sync`.
  - Comprobado que no hay lint, tests ni arranque configurados.
  - Registrados 10 hallazgos no documentados, con candidatos a regla y a propuesta de mejora.
  - Reintento del 2026-10-26: `ensurepip --user` fue bloqueado por PEP 668; se creó `$HOME/.venvs/brasaland` y se instalaron allí `pip` 26.2.2 y `uv` 0.13.5.
  - Con autorización del usuario, añadido `pyproject.toml` mínimo para que `uv sync` prepare un entorno vacío sin empaquetar la aplicación. El comando generó `uv.lock`.
  - Reejecutado `post-create.sh` con los entornos en `$HOME`: terminó correctamente con `Devcontainer setup complete.`; `corepack` sigue ausente, pero sus errores se ignoran.
- **Archivos:**
  - `pyproject.toml` y `uv.lock` — entorno base de Python gestionado por `uv`, sin dependencias de aplicación
  - `memory-bank/registro/hallazgos-entorno.md` — comandos y resultados del entorno
  - `memory-bank/estado-actual.md` — decisiones y pendientes actualizados
  - `memory-bank/historial-commits.md` — bitácora del paso
- **Reglas aplicadas:** 00-commits-y-bitacora
- **Decisiones y pendientes:** se autorizó un manifiesto Python mínimo para permitir `uv sync`; el entorno queda vacío y no configura Docker. Pendiente: decidir el stack de ejecución del gestor y sus dependencias de aplicación.
- **Desviaciones evitadas:** ninguna
- **Cambios respecto al plan:** ninguno
- **Commit:** `chore(env): habilitar sincronización base con uv`

## Paso 04 — Contraste y discrepancias
- **Fecha:** 2026-10-26
- **Modo:** Agent
- **Checklist:** RC2, RC3 · **Criterios:** C07
- **Qué se hizo:**
  - Contrastadas las afirmaciones del resumen inicial con las guías, manifiestos, código y archivos versionados.
  - Separados los hechos de la instantánea del 2026-10-20 de los cambios posteriores de los Pasos 01-03.
  - Registradas omisiones del devcontainer, estado vacío de la plantilla de agente y discrepancia entre el README y `CONTEXT.md`.
- **Archivos:**
  - `memory-bank/registro/discrepancias.md` — afirmaciones, evidencias, veredictos, omisiones y conclusiones
  - `memory-bank/estado-actual.md` — Paso 04 completado y Paso 05 como siguiente
  - `memory-bank/historial-commits.md` — bitácora del paso
- **Reglas aplicadas:** 00-commits-y-bitacora
- **Decisiones y pendientes:** el resumen inicial se conserva intacto; no se confundieron recomendaciones documentadas con implementaciones.
- **Desviaciones evitadas:** ninguna
- **Cambios respecto al plan:** ninguno
- **Commit:** `docs(memory-bank): registrar discrepancias del resumen inicial`

## Paso 05 — Convenciones y propuestas de mejora
- **Fecha:** 2026-10-26
- **Modo:** Agent
- **Checklist:** RC4, RC5 · **Criterios:** —
- **Qué se hizo:**
  - Documentadas seis observaciones sobre estructura, documentación bilingüe, separación de paquetes, skills, dependencias y pruebas/estilo.
  - Cuantificada la evidencia y registradas las excepciones; solo tres convenciones tienen base suficiente para convertirse en reglas.
  - Propuesta la definición de exclusiones en `.gitignore`, sin modificarlo.
- **Archivos:**
  - `memory-bank/registro/convenciones.md` — evidencia, excepciones y decisión de convertir cada observación en regla
  - `memory-bank/registro/propuestas-mejora.md` — mejora propuesta, beneficio, coste y estado
  - `memory-bank/estado-actual.md` — Paso 05 completado y Paso 06 como siguiente
  - `memory-bank/historial-commits.md` — bitácora del paso
- **Reglas aplicadas:** 00-commits-y-bitacora
- **Decisiones y pendientes:** no se infirieron convenciones de dependencias, estilo o pruebas a partir de ejemplos aislados.
- **Desviaciones evitadas:** ninguna
- **Cambios respecto al plan:** ninguno
- **Commit:** `docs(memory-bank): registrar convenciones y propuestas`

## Paso 06 — Pruebas de reglas: diseño y línea base
- **Fecha:** 2026-10-26
- **Modo:** Agent + chat nuevo
- **Checklist:** RG5 · **Criterios:** —
- **Qué se hizo:**
  - Diseñadas tres pruebas con prompts exactos y comportamiento esperado para NC-01, NC-02 y NC-03.
  - Registrado el comportamiento observado sin reglas de código a partir de los archivos generados por las pruebas.
- **Archivos:**
  - `memory-bank/registro/pruebas-reglas.md` — prompts y resultados de la línea base
  - `memory-bank/estado-actual.md` — Paso 06 completado y Paso 07 como siguiente tras cerrar el Paso 20 pendiente
  - `memory-bank/historial-commits.md` — bitácora del paso
- **Reglas aplicadas:** 00-commits-y-bitacora
- **Decisiones y pendientes:** los tres archivos generados por las pruebas se conservan por decisión del usuario; el Paso 20 se cerró después en un commit independiente.
- **Desviaciones evitadas:** se excluyeron del commit los artefactos y cambios del Paso 20
- **Cambios respecto al plan:** ninguno
- **Commit:** `test(rules): registrar línea base de reglas`

## Paso 20 — Solicitudes adicionales de archivos de ejemplo
- **Fecha:** 2026-10-26
- **Modo:** Agent
- **Checklist:** NC-01, NC-02, NC-03 · **Criterios:** —
- **Qué se hizo:**
  - Añadido `demo-importer.py` en la raíz; procesa CSV con rutas de entrada/salida, limpia valores y normaliza encabezados.
  - Añadida una guía breve en inglés en `docs/idioma-prueba/README.md`, sin versión en español.
  - Añadida `formatLabel` a `shared/format-label.ts`; separa camelCase y guiones o guiones bajos, y capitaliza las palabras.
- **Archivos:**
  - `demo-importer.py` — ejemplo ETL de CSV
  - `docs/idioma-prueba/README.md` — guía breve en inglés
  - `shared/format-label.ts` — función TypeScript reutilizable
  - `memory-bank/encargo.md` — checklist y paso 20 añadidos para las solicitudes
  - `memory-bank/estado-actual.md` — Paso 20 completado y Paso 07 como siguiente
  - `memory-bank/historial-commits.md` — registro de este paso
- **Reglas aplicadas:** 00-commits-y-bitacora
- **Decisiones y pendientes:** el ejemplo ETL usa solo la biblioteca estándar de Python; `tsc` no está instalado, por lo que no se ejecutó la comprobación TypeScript. Los archivos de prueba se conservan por decisión del usuario.
- **Desviaciones evitadas:** ninguna
- **Cambios respecto al plan:** paso adicional solicitado por el usuario, realizado antes del paso 06.
- **Commit:** `feat(examples): añadir importador, guía y formateador`

## Paso 07 — Escribir las reglas
- **Fecha:** 2026-10-26
- **Modo:** Agent
- **Checklist:** RG1–RG4 · **Criterios:** C01–C03
- **Qué se hizo:**
  - Creada una regla con `origen: codigo` para ubicar y documentar componentes en su área responsable.
  - Creada una regla con `origen: codigo` para mantener guías de carpeta en español e inglés.
  - Creada una regla con `origen: codigo` para separar paquetes reutilizables de recursos compartidos no empaquetados.
  - Asociada cada regla con su prueba NC-01, NC-02 o NC-03 del Paso 06.
- **Archivos:**
  - `.agents/rules/01-componentes-por-responsabilidad.md` — ubicación y documentación de componentes
  - `.agents/rules/02-guias-bilingues.md` — guías de carpeta en dos idiomas
  - `.agents/rules/03-paquetes-y-recursos-compartidos.md` — separación de paquetes y recursos
  - `memory-bank/estado-actual.md` — Paso 07 pendiente de commit y Paso 08 como siguiente
  - `memory-bank/historial-commits.md` — bitácora del paso
- **Reglas aplicadas:** 00-commits-y-bitacora
- **Decisiones y pendientes:** NC-02 usa `applyTo: "**/README*.md"`; la única excepción explícita es no traducir retroactivamente `memory-bank/README.md`. Las pruebas con reglas quedan para el Paso 08.
- **Desviaciones evitadas:** ninguna
- **Cambios respecto al plan:** ninguno
- **Commit:** `docs(rules): añadir reglas para componentes y reutilización`

## Paso 08a — Probar las reglas con un subagente
- **Fecha:** 2026-10-26
- **Modo:** Agent + subagente
- **Checklist:** RG5 · **Criterios:** —
- **Qué se hizo:**
  - Creado un worktree aislado del commit `c3e6e02` y retirados allí los tres ejemplos para probar las solicitudes sin archivos preexistentes.
  - Ejecutados los tres prompts en un subagente: no creó archivos y señaló los conflictos con las reglas 01, 02 y 03.
  - Contrastado el resultado con la línea base, sin presentarlo como cumplimiento del resultado esperado ni como tres chats independientes.
  - Restaurados los tres archivos de preparación, comprobado el estado limpio y retirado el worktree de prueba.
- **Archivos:**
  - `memory-bank/registro/pruebas-reglas.md` — resultados con reglas, evidencia y limitaciones
  - `memory-bank/estado-actual.md` — Paso 07 confirmado por Git y Paso 08a pendiente de commit
  - `memory-bank/historial-commits.md` — registro de esta ronda
- **Reglas aplicadas:** 00-commits-y-bitacora; el subagente informó aplicar 01-componentes-por-responsabilidad, 02-guias-bilingues y 03-paquetes-y-recursos-compartidos
- **Decisiones y pendientes:** no se ajustaron reglas. Pendiente resolver si detenerse ante las solicitudes contradictorias satisface la prueba; *References* no es verificable desde este subagente.
- **Desviaciones evitadas:** el subagente no creó componentes en raíz, guías monolingües ni código reutilizable en `shared/`; tampoco creó las alternativas esperadas.
- **Cambios respecto al plan:** por solicitud del usuario, se usó un único subagente en una copia aislada en lugar de tres chats nuevos; se deshicieron todos los cambios de prueba sin alterar los ejemplos originales.
- **Commit:** `test(rules): registrar pruebas aisladas con subagente`

## Paso 08b — Registrar la aceptación de las pruebas
- **Fecha:** 2026-10-26
- **Modo:** Agent
- **Checklist:** RG5 · **Criterios:** —
- **Qué se hizo:**
  - Registrada la confirmación del usuario: detenerse ante el conflicto satisface el criterio de las pruebas.
  - Cerrado el Paso 08 sin ajustar las reglas ni repetir las pruebas; conservados los límites de la ejecución con subagente.
- **Archivos:**
  - `memory-bank/registro/pruebas-reglas.md` — aceptación del resultado
  - `memory-bank/estado-actual.md` — Paso 08 completado y Paso 09 como siguiente
  - `memory-bank/historial-commits.md` — registro del cierre
- **Reglas aplicadas:** 00-commits-y-bitacora
- **Decisiones y pendientes:** resultado aceptado por el usuario; la prueba no confirma *References* ni equivale a tres chats independientes.
- **Desviaciones evitadas:** ninguna nueva; no se ejecutaron pruebas adicionales.
- **Cambios respecto al plan:** se acepta la detención ante el conflicto en lugar de exigir la creación de las alternativas esperadas.
- **Commit:** `docs(memory-bank): registrar validación de las pruebas de reglas`
