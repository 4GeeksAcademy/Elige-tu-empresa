---
id: "00-commits-y-bitacora"
aplicacion: "siempre"
alcance: "Todo commit del repositorio, la bitácora `memory-bank/historial-commits.md` y la sección 'Hecho / En curso / Siguiente' de `memory-bank/estado-actual.md`"
justificacion_aplicacion: "Cualquier tarea termina en un commit, así que la regla afecta a todas"
applyTo: "**"
origen: "encargo"
evidencia:
  - "git log --format=%s: solo hay 1 commit ('1.Eleccion de empresa e idea de agente'), sin prefijo ni cuerpo; no hay convención de commits que derivar del código"
  - "memory-bank/encargo.md (E3, C15): un commit por paso; el historial forma parte de la entrega"
  - "Formato del asunto: propuesto por el encargo (Conventional Commits en español); pendiente de validación del usuario en la parada del Paso 01"
---

# Commitea un paso por commit y registra la bitácora

## Se hace
- Escribe el asunto del commit con el formato `<tipo>(<ámbito>): <asunto>`:
  - `<tipo>` es uno de `feat`, `fix`, `docs`, `test`, `chore`, `refactor`.
  - `<ámbito>` es una palabra en minúsculas (por ejemplo `memory-bank`, `rules`, `incidents`).
  - `<asunto>` va en español, en infinitivo, en minúsculas, sin punto final.
  - El asunto completo mide 72 caracteres como máximo.
- Escribe un cuerpo con estas líneas:
  - `Paso: NN`
  - `Checklist: <IDs de tarea> (<IDs de criterio>)`
  - Si el paso agrupa varios IDs, una línea que empieza por `- ` por cada cosa hecha.
- Haz un commit por paso. Si el paso se divide, un commit por subpaso (`NNa`, `NNb`…).
- Antes de commitear, y dentro del mismo commit:
  - añade la entrada del paso al final de `memory-bank/historial-commits.md`,
  - actualiza "Hecho", "En curso" y "Siguiente" en `memory-bank/estado-actual.md`.
- Commitea solo tras recibir el `OK commit` del usuario.
- Añade los archivos con `git add <ruta>`, uno por uno, y solo los del paso.
- Después del commit, muestra la salida de `git log --oneline -1` y de `git status --short`.

## No se hace
- Un commit con el trabajo de varios pasos.
- `git add .` ni `git add -A`.
- `git commit --amend`, `git rebase`, `git push --force` ni `git push` sin que lo pida el usuario.
- Commitear secretos: ni `.env`, ni tokens, ni credenciales.
- Commitear archivos que no sean del paso (por ejemplo, `resumen.md` antes del Paso 02).

## Cómo comprobarlo
- `git log --format=%B origin/main..HEAD | grep -c "^Paso:"` es igual a `git rev-list --count origin/main..HEAD`.
- `git show --stat HEAD` incluye `memory-bank/historial-commits.md` y `memory-bank/estado-actual.md`.
- `git log -1 --format=%s | grep -E "^(feat|fix|docs|test|chore|refactor)\([a-z-]+\): .{1,60}[^.]$"` devuelve el asunto.
- `git log -1 --format=%B | grep -E "^(Paso|Checklist):"` devuelve 2 líneas.

## Formato de cada entrada de la bitácora

```markdown
## Paso NN — <título>
- **Fecha:** AAAA-MM-DD
- **Modo:** Ask | Plan | Agent
- **Checklist:** <IDs de tarea> · **Criterios:** <IDs C..>
- **Qué se hizo:**
  - …
- **Archivos:** `ruta` — propósito
- **Reglas aplicadas:** <ids>
- **Decisiones y pendientes:** …
- **Desviaciones evitadas:** <regla → qué se evitó> | ninguna
- **Cambios respecto al plan:** <qué y por qué> | ninguno
- **Commit:** `<asunto exacto del commit>`
```

La entrada va en el mismo commit que describe. Se identifica por el número de paso porque el hash no se conoce hasta después de commitear.

## Ejemplo
- ✅ `docs(memory-bank): registrar discrepancias del resumen inicial`, con cuerpo:
  ```
  Paso: 04
  Checklist: RC2, RC3 (C07)
  - Contraste afirmación por afirmación del resumen inicial con el repositorio
  - Registro de discrepancias y omisiones con su evidencia
  ```
- ❌ `Cambios varios` (sin tipo, sin ámbito y sin cuerpo con `Paso:` ni `Checklist:`)
- ❌ `git add . && git commit -m "pasos 02 a 05"` (añade todo y agrupa cuatro pasos)
