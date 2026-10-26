# Convenciones detectadas

> Fecha: 2026-10-26 · Evidencia contrastada con archivos versionados y guías del repo. Se distingue lo que la documentación recomienda de lo que el código realmente implementa.

## Convenciones

### NC-01 — Separar componentes por responsabilidad
- **Categoría:** carpetas y separación de responsabilidades.
- **Enunciado:** la guía asigna responsabilidades a carpetas de primer nivel y recomienda una subcarpeta documentada por aplicación, servicio, agente o pipeline.
- **Evidencia cuantificada:** `README.es.md` enumera 13 áreas de primer nivel; el inventario versionado tiene 20 pares de READMEs en español e inglés que documentan áreas o componentes.
- **Excepciones:** la mayor parte del contenido es guía, no implementación; `services/` no contiene un servicio ejecutable.
- **Se convertirá en regla:** sí; ubicar nuevos componentes en el área responsable y documentar su subcarpeta.

### NC-02 — Mantener guías de carpeta en español e inglés
- **Categoría:** documentación y nombres de archivo.
- **Enunciado:** las guías se nombran `README.es.md` y `README.md` para ofrecer contenido en ambos idiomas.
- **Evidencia cuantificada:** el inventario contiene 20 pares y 21 README en inglés; la única guía sin pareja es `memory-bank/README.md`.
- **Excepciones:** la memoria creada para este encargo tiene índice solo en inglés; no se considera motivo para traducirla retroactivamente.
- **Se convertirá en regla:** sí, para guías nuevas o modificadas en las carpetas del proyecto.

### NC-03 — Distinguir paquetes de recursos compartidos
- **Categoría:** carpetas y reutilización.
- **Enunciado:** `packages/` contiene código versionable reutilizado; `shared/` contiene recursos compartidos que no constituyen un paquete.
- **Evidencia cuantificada:** esta separación aparece en `README.es.md`, `packages/README.es.md` y `shared/README.es.md`; actualmente hay un único `package.json`, en `packages/shared/`.
- **Excepciones:** `packages/shared/` no tiene el README propio que `packages/README.es.md` recomienda para cada paquete; `shared/` contiene solo su guía.
- **Se convertirá en regla:** sí; ubicar código empaquetable en `packages/` y recursos no empaquetados en `shared/`.

### NC-04 — Organizar skills en carpetas
- **Categoría:** nombres y estructura de capacidades reutilizables.
- **Enunciado:** `skills/README.es.md` recomienda una carpeta por skill y una estructura clara para su descubrimiento.
- **Evidencia cuantificada:** hay cuatro carpetas bajo `skills/` (`_template`, `code-review`, `data-analysis`, `research`); solo `_template/` contiene `SKILL.md`, que mide cero bytes.
- **Excepciones:** `data-analysis/` contiene recursos y un script, `research/` contiene carpetas vacías y `code-review/` solo tiene `.gitkeep`; no hay una skill implementada que demuestre el formato de extremo a extremo.
- **Se convertirá en regla:** no; la guía y la implementación disponible no bastan para fijar estructura y contenido obligatorios.

### NC-05 — No hay un patrón de dependencias consolidado
- **Categoría:** dependencias y configuración.
- **Enunciado observado:** el repo combina un `package.json` bajo `packages/shared/` con un `pyproject.toml` raíz añadido en el Paso 03 para sincronizar un entorno Python vacío.
- **Evidencia cuantificada:** hay un `package.json`, cero `pnpm-workspace.yaml` y un `pyproject.toml`; el script de preparación usa `pnpm@latest` y `uv sync`.
- **Excepciones:** `pyproject.toml` y `uv.lock` se añadieron después del análisis inicial y no declaran dependencias de aplicación. No existe un runtime acordado para el gestor de incidencias.
- **Se convertirá en regla:** no; la evidencia refleja un setup parcial, no una convención uniforme de dependencias.

### NC-06 — El estilo y las pruebas no tienen base común suficiente
- **Categoría:** estilo y pruebas.
- **Enunciado observado:** hay ejemplos aislados de TypeScript, Python y Bash, pero no una configuración común de lint o tests.
- **Evidencia cuantificada:** `packages/shared/package.json` declara cero scripts; no hay configuración versionada de ESLint, Prettier, Ruff ni runner de tests; `agents/_template/agent.py` mide cero bytes.
- **Excepciones:** `.devcontainer` instala extensiones de editor y el script Bash usa `set -euo pipefail`; son señales aisladas, no una convención repetida entre implementaciones.
- **Se convertirá en regla:** no; faltan implementaciones y configuración suficientes para inferir un estilo o framework de pruebas.