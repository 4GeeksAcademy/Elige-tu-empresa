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
