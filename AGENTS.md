# AGENTS.md — Manual de trabajo del agente

> Léelo entero al empezar cualquier sesión. Responde siempre en español.

## 1. Dónde está cada cosa

| Qué | Dónde | Para qué |
|---|---|---|
| Este manual | `AGENTS.md` (raíz) | Cómo trabajas siempre |
| Reglas del proyecto | `.agents/rules/` (raíz) | **Restringen** cómo se trabaja: qué se hace y qué no. Una regla por archivo |
| Banco de memoria | `memory-bank/` (raíz) | **Describe** el proyecto, el encargo y en qué punto está |
| Índice de la memoria | `memory-bank/README.md` | Qué contiene cada archivo de memoria, cuándo leerlo y cuándo actualizarlo |
| Encargo en curso | `memory-bank/encargo.md` | El ticket, el checklist con IDs y el plan paso a paso |
| Dominio de la empresa | `CONTEXT.md` (raíz) | El BRIEFING: única fuente de nombres de entidades y valores de dominio |

- **Ramas.** Rama de trabajo: `feature/incident-manager`. Rama principal: `main`.
- **Carpetas separadas.** `memory-bank/` es una carpeta aparte; no está dentro de `.agents/`.
- **Las reglas solo viven en `.agents/rules/`** y la memoria solo en `memory-bank/`.
  - No crees reglas ni memoria en ningún otro sitio: ni en `.github/instructions/`, ni en `.github/copilot-instructions.md`, ni en `.cursor/`.
  - Si el repo ya tenía alguno de esos archivos, forma parte del código base que se analiza.
- **Este manual no copia** el contenido de las reglas ni de la memoria: los enlaza.

## 2. Al empezar una sesión

1. Lee `memory-bank/README.md` y, en el orden que indica, los archivos núcleo que ya existan.
2. Aplica el protocolo de lectura de reglas (§4).
3. Lee la última entrada de `memory-bank/historial-commits.md` y la salida de `git log --oneline -15`.
4. Después, según lo que te pida el usuario:
   - **Si pide una tarea concreta**, hazla siguiendo este manual.
   - **Si solo dice "continúa"**, resume en 5 líneas como máximo dónde estamos y propón el siguiente paso de `memory-bank/encargo.md`. No repitas pasos que ya estén commiteados.

## 3. Fuentes de verdad

| Tema | Fuente | Si no está ahí |
|---|---|---|
| Dominio: empresa, áreas, canales, tipos, severidades, entidades | `CONTEXT.md` | Márcalo como `pendiente` y pregunta |
| Convenciones técnicas | Código, configuración, manifiestos y `git log` | Pregunta; no decidas tú |
| Método de trabajo | Este manual y `.agents/rules/` | — |
| Qué hay que hacer y en qué punto estamos | `memory-bank/` | — |

## 4. Reglas: protocolo de lectura

Nadie te carga las reglas automáticamente: las lees tú desde `.agents/rules/`. Hazlo al empezar la sesión y al empezar cada paso.

1. **Lista la carpeta:** `ls .agents/rules/`.
2. **Lee el frontmatter** de todas las reglas.
3. **`aplicacion: siempre`** → léelas completas y aplícalas en todo.
4. **`aplicacion: patron`** → antes de crear o modificar un archivo, lee completas las reglas cuyo `applyTo` case con la ruta de ese archivo.
5. **`aplicacion: agente`** → cuando la tarea coincida con su `description`, léela completa antes de hacer la tarea.
6. **`aplicacion: manual`** → solo la lees si el usuario la nombra.
7. **En cada parada**, indica por su `id` qué reglas has leído y cuáles has aplicado.

Si una regla contradice este manual, para y pregunta.

## 5. Reglas: formato obligatorio

Cada regla es un archivo `.agents/rules/NN-<preocupacion>.md` con esta estructura:

```markdown
---
id: "NN-<preocupacion>"
aplicacion: "<siempre | patron | agente | manual>"
alcance: "<qué tareas o qué archivos cubre, en una frase>"
justificacion_aplicacion: "<por qué esta forma de aplicación y no otra>"
applyTo: "<glob>"                  # solo si aplicacion = patron ("**" si aplicacion = siempre)
description: "<cuándo cargarla>"   # solo si aplicacion = agente
origen: "<codigo | encargo | briefing>"
evidencia:
  - "<ruta o comando>: <qué demuestra>"
---

# <Título en imperativo>

## Se hace
- <instrucción verificable>

## No se hace
- <prohibición verificable>

## Cómo comprobarlo
- <comando o inspección que demuestra que se cumple>

## Ejemplo
- ✅ <correcto, tomado del repo cuando sea posible>
- ❌ <incorrecto>
```

### Formas de aplicación

El frontmatter no lo interpreta ninguna herramienta: lo interpretas tú, con el protocolo del §4.

| Forma | Cuándo usarla | Frontmatter | Cuándo la lees y la aplicas |
|---|---|---|---|
| `siempre` | Afecta a cualquier tarea | `applyTo: "**"` | Al empezar la sesión y en cada paso |
| `patron` | Depende de qué archivo o carpeta se toque | `applyTo: "<glob>"` | Antes de crear o modificar un archivo que case con el glob |
| `agente` | Afecta a un tipo de tarea, no a unos archivos concretos | `description` clara, sin `applyTo` | Cuando la tarea coincide con la `description` |
| `manual` | Procedimiento ocasional | Sin `applyTo` ni `description` | Solo cuando el usuario la nombra |

### Cómo se escribe una regla verificable

- **Una regla, una preocupación.** Si toca dos temas, divídela en dos.
- **Palabras vetadas:** "intenta", "cuando sea posible", "si procede", "adecuado", "buenas prácticas", "limpio", "evita en lo posible".
- **Todo se puede comprobar.** Cada línea de "Se hace" y de "No se hace" se comprueba mirando un archivo o ejecutando un comando.
- **Con evidencia.** Cada regla con `origen: codigo` cita evidencia real del repo: rutas, archivos de configuración o recuentos del tipo "N de M archivos siguen…".

## 6. Cómo se trabaja cada paso

### 6.1 Modos

| Modo | Para qué | Puede escribir archivos y commitear |
|---|---|---|
| Ask | Explorar y preguntar | No |
| Plan | Construir planes | No |
| Agent | Escribir archivos, ejecutar comandos y commitear | Sí |

Si un paso necesita otro modo, dilo en la parada y espera a que el usuario lo cambie.

### 6.2 Disciplina

- **Un paso cada vez.** No adelantes trabajo de pasos posteriores.
- **Relee antes de empezar.** Antes de cada paso, relee su apartado en `memory-bank/encargo.md` y sus IDs.
- **Comprueba, no supongas.** Usa comandos (`ls`, `cat`, `git status`, `git log`) en lugar de suponer qué contiene un archivo.
- **Divide lo grande.** Si un paso es grande, pártelo en subpasos (`NNa`, `NNb`…), cada uno con su parada y su commit.
- **Paradas cortas.** Lo justo para que el usuario pueda revisar y decidir.

### 6.3 Ciclo de cada paso

1. **Prepárate:**
   - aplica el protocolo de lectura de reglas (§4),
   - lee el apartado del paso en `memory-bank/encargo.md`,
   - mira `memory-bank/estado-actual.md`.
2. **Haz el trabajo del paso.** Solo ese paso.
3. **Autoverifícate:**
   - ejecuta lo que aplique: lint, tests, build o arranque,
   - repasa las reglas que afecten a los archivos que has tocado.
4. **Registra.** Añade la entrada a la bitácora y actualiza `estado-actual.md`, como indica la regla 00.
5. **Para.** Muestra la parada (§6.4) y espera.
6. **Commitea con el `OK commit`.** Hazlo como indica la regla 00 y enseña la salida de `git log --oneline -1` y de `git status --short`.
7. **Sigue con el siguiente paso**, salvo que necesite uno de estos:
   - un cambio de modo,
   - una validación del usuario,
   - una acción del usuario en otro chat.

   En ese caso, para y dilo.

Si en la parada te piden cambios: aplícalos, actualiza la bitácora y el estado, y vuelve a mostrar la parada.

### 6.4 Formato de la parada

```markdown
### ✋ Parada — Paso NN: <título>
**Checklist cubierto:** <IDs de tarea> · **Criterios:** <IDs C..>
**Qué he hecho:**
- …
**Archivos (`git diff --stat`) y propósito de cada uno:**
- `ruta` — propósito
**Comprobaciones ejecutadas:** <comando → resultado real> | no aplica
**Reglas leídas (por `id`):** … · **Reglas aplicadas / desviaciones evitadas:** …
**Dudas o decisiones para ti:** …
**Commit propuesto:**
<mensaje completo: asunto y cuerpo>

👉 Responde `OK commit` o dime qué cambiar. Siguiente: Paso NN+1 (modo <Agent|Plan>).
```

En los pasos de código, añade también una lista de qué revisar en cada archivo.

## 7. Principios no negociables

1. **No cambies convenciones existentes.** Si una te parece mejorable, regístrala como propuesta en `memory-bank/registro/propuestas-mejora.md` y sigue aplicando la actual.
2. **No inventes valores de dominio.** Cada valor sale de `CONTEXT.md` y cita de dónde.
3. **No añadas nada nuevo sin permiso:** ni dependencias, ni herramientas, ni frameworks, ni patrones. Si crees que hace falta, para, justifícalo y espera el OK. La respuesta por defecto es no.
4. **No inventes resultados.** Si no has ejecutado un comando, no digas que funciona. Si no ha habido una desviación, no la registres.
5. **No toques el remoto ni reescribas historia** sin que te lo pidan: ni push, ni PR, ni `amend`, ni `rebase`, ni `force-push`.
6. **Ante la duda, pregunta.** Una pregunta corta sale más barata que revertir código.
7. **Nada de secretos en los commits:** ni `.env`, ni tokens, ni credenciales.
8. **Cada cosa en su sitio:** las reglas en `.agents/rules/`, la memoria en `memory-bank/` y el método en este manual.

## 8. Cómo se mantiene este manual

- **Si cambia dónde vive algo o cómo se trabaja,** actualiza este manual en el mismo commit y anótalo en la bitácora.
- **Si añades o renombras un archivo de memoria,** actualiza `memory-bank/README.md` en el mismo commit.
