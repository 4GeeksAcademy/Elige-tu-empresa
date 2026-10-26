# Contraste del resumen inicial

> Fecha: 2026-10-26 · Resumen contrastado: `memory-bank/registro/resumen-inicial-agente.md` (generado el 2026-10-20, modo Ask). El resumen es una instantánea previa al trabajo de este encargo; se conserva sin editar.

## Afirmaciones contrastadas

| # | Afirmación del resumen | Evidencia en el repositorio | Veredicto |
|---|---|---|---|
| 1 | El repo es una plantilla educativa de monorepo para el programa AI Engineering. | `README.es.md:3-14` la describe como plantilla transversal y enumera hitos del curso. | ✅ Correcta |
| 2 | La empresa puede ser ficticia o asignada. | `README.es.md:14` describe los escenarios como empresas reales; la palabra «ficticia» del resumen no está respaldada por esa guía. | ⚠️ Imprecisa |
| 3 | El contexto de este checkout es Brasaland; `company-choice.md` propone un agente de reservas y la plantilla menciona TrackFlow y Nexova. | `CONTEXT.md:1,7`; `company-choice.md:3-4`; `README.es.md:14`. La idea de reservas es una propuesta separada, no una aplicación existente. | ✅ Correcta |
| 4 | El estado del repo es principalmente estructura y documentación, sin aplicación completa lista para ejecutar. | `README.es.md:52-58` dice que no hay aplicaciones ejecutables; `services/README.es.md:1-7` documenta el área y no implementa un servicio. El inventario versionado contiene guías, ejemplos y configuración, no una app del gestor. | ✅ Correcta |
| 5 | Hay una plantilla mínima de agente Python. | `agents/_template/agent.py` existe, pero `wc -c agents/_template/agent.py` devuelve `0`; `agents/_template/tests/` contiene solo READMEs según `git ls-files`. | ⚠️ Imprecisa: existe la estructura, no código ejecutable del agente ni pruebas. |
| 6 | Hay un ejemplo Python de limpieza de datos que usa pandas. | `skills/data-analysis/scripts/pandas_clean.py` importa pandas, lee `data.csv` y documenta la ejecución en su docstring. | ✅ Correcta |
| 7 | Hay tipos TypeScript de ejemplo en `packages/shared/types/index.ts` y metadata `@repo/shared-types`. | `packages/shared/types/index.ts:7,9`; `packages/shared/package.json:2,8`. El paquete no declara scripts. | ✅ Correcta |
| 8 | FastAPI es una recomendación para `services/`, no una app implementada. | `README.es.md:88-97` recomienda una API FastAPI; los archivos versionados de `services/` son READMEs. | ✅ Correcta |
| 9 | No había gestor/manifiesto raíz ni lockfile de workspace. | Era cierto para la instantánea del 2026-10-20. El commit `3078274` añadió después `pyproject.toml` y `uv.lock`, autorizados para preparar un entorno Python vacío. Aún no hay `pnpm-workspace.yaml` ni `package.json` raíz. | ⚠️ Correcta entonces; obsoleta como descripción del checkout actual. |
| 10 | No se especifica base de datos ni hay configuración presente. | El inventario de `git ls-files` no contiene manifiestos o configuración de base de datos; tampoco hay una aplicación backend implementada. | ✅ Correcta según los archivos versionados. |
| 11 | No se encontraron configuraciones o comandos de lint, formato o tests. | `packages/shared/package.json:8` tiene `scripts: {}`. El inventario versionado no muestra configuración de ESLint, Prettier, Ruff o un runner de tests. `pyproject.toml` solo configura el entorno vacío de `uv`. | ✅ Correcta para el checkout revisado. |
| 12 | Las carpetas y el flujo de datos separan UI, servicios, fuentes, pipelines, proceso y evaluación. | `README.es.md:37-45,103-114` describe esas responsabilidades y el flujo `raw → pipelines → process`. Son convenciones documentadas, no prueba de pipelines implementados. | ✅ Correcta, con esa distinción. |
| 13 | El repo propone workflows n8n, paquetes compartidos y `shared/` para recursos no empaquetados. | `README.es.md:155-181` distingue workflows, packages y shared; las carpetas contienen guías. | ✅ Correcta como orientación. |
| 14 | La guía no contiene instalación ni comando de arranque local. | El README no da un comando para iniciar una aplicación, pero `.devcontainer/devcontainer.json:30` ejecuta `.devcontainer/post-create.sh`; ese script instala herramientas y ejecuta `uv sync` (`.devcontainer/post-create.sh:4-10`). | ⚠️ Parcial: omite la configuración de desarrollo del devcontainer. |
| 15 | El README espera `docker-compose.yml`, pero no está presente. | `README.es.md:71,212,273` lo describe como esperado en la raíz. `git ls-files` no incluye `docker-compose.yml` ni `Dockerfile`. | ✅ Correcta |
| 16 | El ejemplo pandas requiere pandas y un `data.csv` que el repo no proporciona. | `skills/data-analysis/scripts/pandas_clean.py` importa pandas y lee `data.csv`; `git ls-files` no muestra ese archivo junto al script. | ✅ Correcta |
| 17 | La guía documenta convenciones para ubicar componentes y separar `packages/` de `shared/`. | `README.es.md:26-29,171-181,248-261` define subcarpetas por app y la diferencia entre paquetes de código y recursos compartidos. | ✅ Correcta como convención propuesta. |
| 18 | El contexto real del checkout es Brasaland, y `CONTEXT.md` no es documentación técnica de una app. | `CONTEXT.md:1-37` contiene el briefing de negocio y describe a Brasaland Digital; no especifica una implementación. | ✅ Correcta |

## Omisiones relevantes

- La configuración de desarrollo: `.devcontainer/devcontainer.json:7-9,30-32` selecciona la imagen `universal:2`, monta el socket Docker, ejecuta el script de preparación y reenvía puertos. `.devcontainer/post-create.sh:4-10` intenta habilitar Corepack/pnpm e instalar `pip`/`uv` antes de `uv sync`.
- El agente de ejemplo no tiene código: `agents/_template/agent.py` mide cero bytes; la carpeta `tests/` solo aporta documentación.
- La guía llama placeholder a `CONTEXT.md` (`README.es.md:17,56`), pero el archivo actual contiene el briefing completo de Brasaland. La instrucción genérica está desactualizada para este checkout.
- `AGENTS.md`, `.agents/rules/` y `memory-bank/` se añadieron después de la instantánea del resumen, en el commit `647f20a`; no son omisiones atribuibles al resumen original.
- El manifiesto Python y `uv.lock` también son posteriores al resumen (`3078274`); forman un entorno vacío y no significan que exista una app Python ni una configuración Docker.

## Conclusiones

1. Las recomendaciones de README describen una arquitectura prevista; no deben confundirse con servicios, pipelines o agentes implementados.
2. Toda afirmación sobre manifiestos, configuración o estructura debe fecharse: los commits posteriores cambian el checkout sin volver cierto el resumen histórico.
3. Leer solo el README pasa por alto el flujo real del devcontainer y sus dependencias; hay que contrastar también scripts y configuración.
4. La existencia de una plantilla no prueba que contenga una implementación o tests: hay que inspeccionar los archivos, no solo sus nombres.
5. Para decisiones de producto, `CONTEXT.md` y el encargo vigente prevalecen sobre placeholders genéricos del README y sobre la idea de reservas en `company-choice.md`.