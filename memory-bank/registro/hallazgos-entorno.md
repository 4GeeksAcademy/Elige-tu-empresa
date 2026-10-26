# Hallazgos del entorno (Paso 03)

> Primera ejecución: 2026-10-20 · Modo: Agent · Solo se ha seguido lo que indica el repo (README, `.devcontainer/`, manifiestos). En esa ejecución no se modificó configuración ni se instaló nada fuera de lo que ejecuta `post-create.sh`.

## Qué documenta el repo para levantar el entorno

| Fuente | Qué indica |
|---|---|
| `README.md` (líneas 25-29) | Clonar o abrir en Codespaces; no da comandos de instalación, lint, test ni arranque |
| `.devcontainer/devcontainer.json` | Imagen `mcr.microsoft.com/devcontainers/universal:2`, `postCreateCommand: bash .devcontainer/post-create.sh`, puertos 3000, 8000 y 5678, montaje de `/var/run/docker.sock`, extensiones (Python, Jupyter, Docker, Prettier, ESLint) y `editor.formatOnSave: true` |
| `.devcontainer/post-create.sh` | `corepack enable` y `corepack prepare pnpm@latest --activate` (ambos con `|| true`), `python -m pip install --upgrade pip uv` y `uv sync` |
| `packages/shared/package.json` | Único manifiesto: `@repo/shared-types`, `scripts: {}` (sin comandos) |
| `skills/data-analysis/scripts/pandas_clean.py` | `python pandas_clean.py`, con pandas instalado y un `data.csv` |

## Comandos ejecutados y resultado real

Entorno donde se ejecutó: Alpine Linux, usuario `vscode`, Python 3.12.15. No es la imagen `universal:2` del devcontainer.

| # | Comando | Resultado |
|---|---|---|
| 1 | `which corepack uv pnpm` | no existe ninguno de los tres |
| 2 | `node --version`, `npm --version`, `pip --version`, `docker --version` | `command not found` en los cuatro |
| 3 | `python --version` | `Python 3.12.15` |
| 4 | `python -m pip --version` | `No module named pip` |
| 5 | `ls pyproject.toml uv.lock` | `No such file or directory` en ambos |
| 6 | `bash .devcontainer/post-create.sh` | `corepack: command not found` (líneas 5 y 6, absorbido por `\|\| true`), luego `No module named pip` y `exit=1`. No llegó a `uv sync` |
| 7 | `python -c "import pandas"` | `ModuleNotFoundError: No module named 'pandas'` |
| 8 | `python agents/_template/agent.py` | `exit=0`, sin salida: el archivo mide 0 bytes |
| 9 | `python -m pytest --version`, `python -m ruff --version` | `No module named pytest` y `No module named ruff` |
| 10 | `git status --short` tras ejecutarlo todo | solo `?? resumen.md` (el script no creó archivos) |

## Resultado por tarea

| Tarea | Resultado |
|---|---|
| Instalación | La primera ejecución falló por falta de `pip` y `pyproject.toml`. Tras crear el entorno virtual y el manifiesto mínimo, el script terminó correctamente; `corepack` sigue ausente, pero sus errores se ignoran. |
| Lint | No aplica: no hay configuración de ESLint, Prettier ni Ruff en el repo (`git ls-files` sin coincidencias) |
| Tests | No aplica: no hay runner ni tests; `agents/_template/tests/` solo contiene READMEs |
| Arranque | No aplica: no hay aplicación, ni `docker-compose.yml`, ni scripts de arranque (`scripts/` e `internal/` solo contienen READMEs) |

## Lo que no estaba documentado

Cada punto es un candidato a regla (CR) o a propuesta de mejora (PM).

1. **Gestores de dependencias parcialmente definidos.** El README no nombra ninguno. `post-create.sh` apunta a `pnpm` (JS/TS) y a `uv` (Python). Con autorización del usuario, en el reintento se añadieron `pyproject.toml` y `uv.lock` para el entorno Python; sigue sin haber `pnpm-workspace.yaml` ni configuración de workspace JS. → CR: no añadir gestor ni manifiestos sin OK del usuario.
2. **`uv sync` requiere `pyproject.toml`.** Confirmado en el reintento: sin manifiesto falla; con el manifiesto mínimo completa la sincronización. Este manifiesto no declara dependencias de aplicación y configura `package = false`.
3. **`pnpm@latest` sin versión fijada.** → PM.
4. **`.gitignore` vacío (0 bytes).** `.env`, `__pycache__/` y `node_modules/` no están ignorados. → CR: no commitear secretos ni artefactos, comprobando `git status` antes de cada `git add`. También PM.
5. **El entorno real no coincide con el devcontainer.** Aquí no hay Node, pip ni Docker. Las comprobaciones de Node y Docker no se pueden hacer en este entorno.
6. **`docker-compose.yml` no existe**, aunque el README lo sitúa en la raíz (README línea 71).
7. **ESLint y Prettier están en las extensiones y con `formatOnSave`, pero no hay configuración.** No hay un formato verificable por comando.
8. **`agents/_template/agent.py` está vacío** y la plantilla no trae pruebas.
9. **Puertos reservados:** 3000, 8000 y 5678 (`forwardPorts`).
10. **El ejemplo de pandas** exige instalar pandas y aportar `data.csv`; el repo no da ninguno de los dos pasos.

## Pendiente de decidir contigo

- Definir el stack de ejecución del gestor y sus dependencias de aplicación. `pyproject.toml` solo permite sincronizar un entorno Python vacío; no configura Docker. El repo sigue sin `Dockerfile` ni `docker-compose.yml`.

## Reintento solicitado — 2026-10-26

Entorno: Alpine Linux, usuario `vscode` sin privilegios de `root`.

| Comando | Resultado |
|---|---|
| `python3 -m ensurepip --user` | Falló con `externally-managed-environment` (PEP 668); no se forzó la instalación del Python del sistema. |
| `python3 -m venv "$HOME/.venvs/brasaland"` | Correcto; creó el entorno virtual fuera del repositorio. |
| `PATH="$HOME/.venvs/brasaland/bin:$PATH" bash .devcontainer/post-create.sh` | `pip` 26.2.2 y `uv` 0.13.5 se instalaron en el entorno virtual. `corepack` no existe, pero esos errores se ignoran por `|| true`. El comando terminó con `exit 1`: `uv sync` informó que no encontró `pyproject.toml`. |
| `PATH="$HOME/.venvs/brasaland/bin:$PATH" UV_PROJECT_ENVIRONMENT="$HOME/.venvs/brasaland-project" bash .devcontainer/post-create.sh` | Correcto: `uv sync` creó el entorno virtual fuera del repo y generó `uv.lock`; terminó con `Devcontainer setup complete.`. Los avisos de `corepack` permanecieron, pero no bloquearon el script. |

Con autorización del usuario se creó `pyproject.toml` con metadatos mínimos, `requires-python = ">=3.12"`, `dependencies = []` y `package = false`; no representa todavía las dependencias ni el empaquetado de la aplicación. `uv.lock` fue generado por el comando. No se instaló Node/Corepack: el script tolera que esos comandos fallen y el repo no define un workspace pnpm en la raíz. El setup tampoco configura Docker.
