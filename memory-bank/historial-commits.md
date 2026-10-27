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

## Paso 09 — Documentar el contexto de producto y los catálogos
- **Fecha:** 2026-10-26
- **Modo:** Agent
- **Checklist:** BM1, BM2, BM5 · **Criterios:** C05, C13 (pendientes de validación)
- **Qué se hizo:**
  - Leído el briefing completo y documentada la operación de Brasaland con referencias a sus secciones.
  - Separadas las áreas literales de los canales candidatos y las necesidades derivadas del gestor.
  - Marcados como pendientes tipos, severidades, estados e identificadores, sin inventar valores ni convenciones.
- **Archivos:**
  - `memory-bank/contexto-producto.md` — borrador de producto, catálogos, glosario y decisiones pendientes
  - `memory-bank/README.md` — índice actualizado con el borrador creado
  - `memory-bank/estado-actual.md` — parada de validación del Paso 09
  - `memory-bank/historial-commits.md` — registro del paso
- **Reglas aplicadas:** 00-commits-y-bitacora, 02-guias-bilingues (excepción explícita del índice de memoria)
- **Decisiones y pendientes:** el usuario debe validar las propuestas y aportar o aprobar los catálogos ausentes; no se escribe código.
- **Desviaciones evitadas:** no se convirtieron los medios de comunicación del briefing en canales aprobados ni se inventaron estados o severidades.
- **Cambios respecto al plan:** ninguno
- **Commit:** `docs(memory-bank): documentar contexto de producto de Brasaland`

## Paso 10 — Documentar el stack tecnológico y el estado del proyecto
- **Fecha:** 2026-10-27
- **Modo:** Agent
- **Checklist:** BM1, BM4 · **Criterios:** C04, C14
- **Qué se hizo:**
  - Documentadas la estructura del monorepo, las dependencias existentes y los comandos disponibles.
  - Registrada la ausencia de aplicación de incidencias, persistencia y comandos globales de lint, pruebas y arranque.
  - Actualizados el estado actual y las decisiones técnicas pendientes.
- **Archivos:**
  - `memory-bank/stack-tecnologico.md` — descripción del stack existente, las responsabilidades y los límites conocidos
  - `memory-bank/estado-actual.md` — estado del proyecto, decisiones y siguiente paso
  - `memory-bank/historial-commits.md` — registro del paso
- **Reglas aplicadas:** 00-commits-y-bitacora; reglas 01–03 enlazadas como referencias
- **Decisiones y pendientes:** no se eligieron framework, base de datos, Docker ni dependencias de aplicación; sigue pendiente validar los catálogos del Paso 09.
- **Desviaciones evitadas:** no se añadieron herramientas ni se infirió configuración no comprobada; `uv.lock` quedó sin inspeccionar por restricción de contenido.
- **Cambios respecto al plan:** ninguno
- **Commit:** `docs(memory-bank): documentar stack tecnologico y estado actual`

## Paso 09b — Validar el contexto de producto y los catálogos
- **Fecha:** 2026-10-27
- **Modo:** Agent
- **Checklist:** BM2, BM5, RG1–RG4 · **Criterios:** C01–C03, C05, C13
- **Qué se hizo:**
  - Validada la propuesta de usuarios y necesidades, las seis áreas asignables y Dirección Ejecutiva como consulta.
  - Validados WhatsApp, teléfono y email como canales manuales sin integración automática.
  - Validados tipos, criterios de severidad, estados, transiciones y la convención `camelCase` ASCII para IDs.
  - Añadida una regla permanente para mantener las convenciones camelCase/PascalCase del código.
- **Archivos:**
  - `.agents/rules/04-nombres-camel-case.md` — convención de nombres para código nuevo o renombrado
  - `memory-bank/contexto-producto.md` — catálogos aprobados, identificadores, orígenes y transiciones
  - `memory-bank/estado-actual.md` — cierre de la validación del Paso 09 y siguiente paso
  - `memory-bank/historial-commits.md` — registro de la ronda de validación
- **Reglas aplicadas:** 00-commits-y-bitacora, 04-nombres-camel-case
- **Decisiones y pendientes:** valores no literales documentados como derivados y validados por el usuario; permisos, SLA e integraciones automáticas siguen fuera de alcance.
- **Desviaciones evitadas:** no se atribuyeron al briefing los catálogos que no define; no se renombró código ajeno al alcance de esta tarea.
- **Cambios respecto al plan:** ronda separada 09b para registrar la validación del usuario.
- **Commit:** `docs(rules): mantener convenciones camelcase`

## Paso 11 — Versionar el plan de implementación
- **Fecha:** 2026-10-27
- **Modo:** Plan → Agent
- **Checklist:** BM3, E4 · **Criterios:** C06
- **Qué se hizo:**
  - Acordada la ubicación de la interfaz y la API, y aprobados FastAPI, SQLite estándar, autor manual y fechas UTC mostradas en zona horaria local.
  - Definidos modelo, eventos append-only con escritura transaccional, transiciones, filtros, resumen, pruebas y porciones de implementación.
  - Aclarado que el resumen de abiertas incluye `nueva`, `enCurso` y `resuelta`, excluyendo `cerrada`.
- **Archivos:**
  - `memory-bank/plan-implementacion.md` — plan de implementación versión 1
  - `memory-bank/estado-actual.md` — estado, decisiones cerradas y siguiente paso
  - `memory-bank/historial-commits.md` — registro del paso
- **Reglas aplicadas:** 00-commits-y-bitacora, 01-componentes-por-responsabilidad, 03-paquetes-y-recursos-compartidos, 04-nombres-camel-case; regla 02 consultada para las guías README futuras, no modificadas en este paso.
- **Decisiones y pendientes:** plan aprobado por el usuario; confirmar manifiesto `uv` y formato de IDs antes de implementarlos; Docker y despliegue quedan fuera de alcance.
- **Desviaciones evitadas:** no se eligieron dependencias adicionales, autenticación ni una zona horaria fija; no se tocó el remoto ni archivos ajenos al paso.
- **Cambios respecto al plan:** ninguno
- **Commit:** `docs(memory-bank): versionar plan del gestor`

## Paso 12 — Crear catálogos, modelos y persistencia
- **Fecha:** 2026-10-27
- **Modo:** Agent
- **Checklist:** C13, C14
- **Qué se hizo:**
  - Implementados catálogos con las etiquetas e IDs validados y la restricción de Dirección Ejecutiva como área no asignable.
  - Añadidos modelos de incidencia e historial con IDs UUID v4 y marcas temporales UTC.
  - Creado el esquema SQLite con validación de catálogos, claves foráneas e inmutabilidad de eventos de historial.
  - Añadidas pruebas estándar para valores de dominio, UUID, fechas, persistencia entre conexiones, restricciones, claves foráneas y eventos append-only.
- **Archivos:**
  - `services/api/catalogs.py` — catálogos aprobados
  - `services/api/models.py` — modelos de dominio y utilidades UUID/UTC
  - `services/api/database.py` — conexión y esquema SQLite
  - `services/api/tests/test_database.py` — pruebas del modelo y persistencia
  - `services/api/README.es.md`, `services/api/README.md` — documentación bilingüe del servicio
  - `services/api/__init__.py`, `services/api/tests/__init__.py` — paquetes Python
  - `memory-bank/plan-implementacion.md` — decisión de UUID v4 concretada tras confirmación del usuario
  - `memory-bank/estado-actual.md` — estado y siguiente paso
  - `memory-bank/historial-commits.md` — registro del paso
- **Reglas aplicadas:** 00-commits-y-bitacora, 02-guias-bilingues, 04-nombres-camel-case.
- **Decisiones y pendientes:** UUID v4 en texto confirmado por el usuario para incidencias y eventos. FastAPI está autorizada pero no se incorporó en esta porción, que no expone endpoints; `uv.lock` no pudo inspeccionarse por la política de exclusión de contenido.
- **Desviaciones evitadas:** no se asigna Dirección Ejecutiva; no se introdujeron dependencias de persistencia o de pruebas; no se intentó leer `uv.lock` por otra vía.
- **Cambios respecto al plan:** se concretó el formato de IDs pendiente en la versión 1: UUID v4, confirmado por el usuario.
- **Commit:** `feat(incidents): añadir modelo y persistencia sqlite`

## Paso 13 — Registrar incidencias y asignarlas a un área
- **Fecha:** 2026-10-27
- **Modo:** Agent
- **Checklist:** C08
- **Qué se hizo:**
  - Añadido el caso de uso `registerIncident`, que valida canal, tipo, severidad, título, descripción, autor y un área asignable.
  - La función persiste la incidencia en estado `nueva`, con UUID v4 y marcas temporales UTC, y devuelve el modelo creado.
  - Añadidas pruebas para los tres canales, las seis áreas asignables, valores válidos e inválidos, datos obligatorios y persistencia.
- **Archivos:**
  - `services/api/incidents.py` — caso de uso de registro sobre SQLite
  - `services/api/tests/test_incidents.py` — pruebas del registro y asignación
  - `services/api/README.es.md`, `services/api/README.md` — documentación bilingüe del caso de uso y la limitación HTTP
  - `memory-bank/plan-implementacion.md` — restricción de entorno y ruta HTTP pendiente
  - `memory-bank/estado-actual.md` — avance y limitación del paso
  - `memory-bank/historial-commits.md` — registro del paso
- **Reglas aplicadas:** 00-commits-y-bitacora, 01-componentes-por-responsabilidad, 02-guias-bilingues, 03-paquetes-y-recursos-compartidos, 04-nombres-camel-case.
- **Decisiones y pendientes:** no se modificó ni se accedió a `uv.lock`. El registro funciona como caso de uso Python; no hay endpoint HTTP porque FastAPI no está disponible y no se puede gestionar su dependencia mientras el lockfile siga excluido.
- **Desviaciones evitadas:** se respetó la exclusión deliberada de `uv.lock`; no se instaló un gestor o dependencia por vías no coordinadas, ni se cambió el framework aprobado.
- **Cambios respecto al plan:** el registro se implementó en la capa de servicio SQLite; la ruta HTTP se pospone explícitamente por la restricción del entorno, sin alterar la política.
- **Commit:** `feat(incidents): registrar incidencias por servicio`

## Paso 14 — Aplicar transiciones y consultar historial
- **Fecha:** 2026-10-27
- **Modo:** Agent
- **Checklist:** V2 · **Criterios:** C09, C10
- **Qué se hizo:**
  - Implementadas las transiciones aprobadas, incluida la reapertura desde `resuelta`; `cerrada` permanece terminal.
  - Cada cambio de estado y de área registra autor, valor anterior/nuevo y marca UTC en la misma transacción SQLite que actualiza la incidencia.
  - Añadida la consulta de ficha con historial cronológico y campos de auditoría.
  - Añadidas pruebas de transiciones permitidas/prohibidas, cierre, reasignación, ficha, autor, UTC y rollback si falla la escritura del evento.
- **Archivos:**
  - `services/api/incidents.py` — transiciones, reasignación y consulta de ficha/historial
  - `services/api/models.py` — modelo compuesto `IncidentDetails`
  - `services/api/tests/test_incidents.py` — pruebas de ciclo, trazabilidad y atomicidad
  - `services/api/README.es.md`, `services/api/README.md` — documentación bilingüe de los casos de uso y la limitación HTTP
  - `memory-bank/estado-actual.md` — avance y siguiente paso
  - `memory-bank/historial-commits.md` — registro del paso
- **Reglas aplicadas:** 00-commits-y-bitacora, 01-componentes-por-responsabilidad, 02-guias-bilingues, 03-paquetes-y-recursos-compartidos, 04-nombres-camel-case.
- **Decisiones y pendientes:** la ficha e historial están disponibles como caso de uso SQLite; no hay endpoint HTTP mientras no pueda añadirse FastAPI respetando la exclusión de `uv.lock`.
- **Desviaciones evitadas:** ninguna.
- **Cambios respecto al plan:** ninguno en el comportamiento de dominio; la exposición HTTP continúa pospuesta conforme a la restricción registrada en el Paso 13.
- **Commit:** `feat(incidents): trazar cambios y consultar ficha`

## Paso 15 — Listar incidencias con filtros
- **Fecha:** 2026-10-27
- **Modo:** Agent
- **Checklist:** implementación por porciones · **Criterios:** C11
- **Qué se hizo:**
  - Añadido `listIncidents`, con filtros opcionales por estado, severidad y área responsable; los valores se validan contra los catálogos aprobados.
  - Los filtros se pueden combinar; el listado devuelve primero las incidencias más recientes y usa el orden de inserción para desempatar.
  - Añadidas pruebas para cada filtro, combinación de filtros y rechazo de valores desconocidos o áreas no asignables.
  - Actualizadas las guías bilingües del servicio.
  - Sincronizado el estado del Paso 14 con su commit `99ba6b1`; la entrada anterior había dejado el estado como pendiente tras el commit.
- **Archivos:**
  - `services/api/incidents.py` — caso de uso de listado y filtros
  - `services/api/tests/test_incidents.py` — cobertura de filtros y validación de catálogos
  - `services/api/README.es.md`, `services/api/README.md` — documentación bilingüe del listado
  - `memory-bank/estado-actual.md` — estado y siguiente paso
  - `memory-bank/historial-commits.md` — registro del paso
- **Reglas aplicadas:** 00-commits-y-bitacora, 02-guias-bilingues, 04-nombres-camel-case.
- **Decisiones y pendientes:** listado sin paginación, ordenado de más reciente a más antiguo; los filtros omitidos no restringen resultados. La exposición HTTP sigue pendiente por la restricción vigente de `uv.lock`.
- **Desviaciones evitadas:** ninguna.
- **Cambios respecto al plan:** ninguno.
- **Commit:** `feat(incidents): filtrar listado de incidencias`

## Paso 16 — Resumir incidencias abiertas por severidad
- **Fecha:** 2026-10-27
- **Modo:** Agent
- **Checklist:** implementación por porciones · **Criterios:** C12
- **Qué se hizo:**
  - Añadido `getOpenIncidentCountsBySeverity`, que agrupa por severidad las incidencias en `nueva`, `enCurso` y `resuelta`.
  - El resultado incluye todas las severidades del catálogo validado, con cero para las que no tienen incidencias abiertas.
  - Añadidas pruebas para un conjunto vacío, el recuento en estados abiertos y la exclusión de incidencias cerradas.
  - Actualizadas las guías bilingües del servicio.
  - Sincronizado el estado del Paso 15 con su commit `e88b8ce`.
- **Archivos:**
  - `services/api/incidents.py` — caso de uso de resumen por severidad
  - `services/api/tests/test_incidents.py` — pruebas de recuento y estados abiertos
  - `services/api/README.es.md`, `services/api/README.md` — documentación bilingüe del resumen
  - `memory-bank/estado-actual.md` — estado y siguiente paso
  - `memory-bank/historial-commits.md` — registro del paso
- **Reglas aplicadas:** 00-commits-y-bitacora, 02-guias-bilingues, 04-nombres-camel-case.
- **Decisiones y pendientes:** «abiertas» incluye `nueva`, `enCurso` y `resuelta`, tal como está aprobado en `plan-implementacion.md`; `cerrada` se excluye. La exposición HTTP sigue pendiente por la restricción vigente de `uv.lock`.
- **Desviaciones evitadas:** ninguna.
- **Cambios respecto al plan:** ninguno.
- **Commit:** `feat(incidents): resumir abiertas por severidad`
