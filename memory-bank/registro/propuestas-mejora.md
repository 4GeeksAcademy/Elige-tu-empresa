# Propuestas de mejora

> Fecha: 2026-10-26 · No se aplica ninguna propuesta en este paso.

## PM-01 — Definir exclusiones locales en `.gitignore`

- **Situación actual y evidencia:** `.gitignore` existe y mide cero bytes (`wc -c .gitignore`); el entorno genera archivos y directorios locales que Git no excluye por reglas del repo.
- **Propuesta:** acordar y añadir patrones concretos para secretos locales y artefactos de herramientas (por ejemplo `.env`, `__pycache__/`, `.venv/` y `node_modules/`), comprobando antes que no se oculten archivos que deban versionarse.
- **Beneficio:** reduce el riesgo de añadir credenciales o salidas locales por accidente y hace más legible `git status`.
- **Riesgo o coste:** patrones demasiado amplios pueden ocultar archivos legítimos; el equipo debe mantenerlos al incorporar herramientas.
- **Estado:** propuesta, no aplicada.