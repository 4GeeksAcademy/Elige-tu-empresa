# Encargo en curso: gestor centralizado de incidencias

### B.1 El encargo

**La situación.** Hoy las incidencias del backoffice entran por canales distintos y cada equipo las registra a su manera. Se pierden entre hilos de correo y mensajes sueltos, y nadie sabe cuántas hay abiertas ni quién responde por cada una.

**Lo que pide el CTO:**

- **Primero, el repositorio.** Antes de añadir funcionalidad, el repositorio tiene que dejar de depender de la memoria de quien lo montó. Hay que reconocer el código base, entender las decisiones ya tomadas y dejarlas escritas como reglas que seguirá el agente. Esas decisiones no se cambian por gusto: si una parece incorrecta, se escribe como propuesta y se discute.
- **Después, el gestor.** Los stakeholders de operaciones necesitan:
  - registrar una incidencia venga del canal que venga,
  - clasificarla,
  - asignarla a un área responsable,
  - saber en todo momento en qué estado está.

  Los tipos, las severidades y los canales salen del BRIEFING (`CONTEXT.md`). No se inventan.
- **Lo no negociable: la trazabilidad.** Cuando una incidencia cambia de estado o de responsable, tiene que poder reconstruirse quién la movió y cuándo. Si no queda registrado, no ha pasado. Cada cambio genera un registro inmutable (solo se añade; nunca se edita ni se borra) con:
  - el valor anterior,
  - el valor nuevo,
  - el autor,
  - la marca temporal.

  El registro se escribe en la misma operación que el cambio.
- **Cómo revisa el CTO.** Da el visto bueno en el Pull Request y lee el historial de commits. Si ve un único commit con todo, devuelve el PR sin revisarlo.

### B.2 Trampas que hay que evitar

1. **Rellenar huecos.** No se eligen a gusto el gestor de dependencias, los nombres ni los patrones. Todo debe tener un precedente en el repositorio o la aprobación explícita del usuario.
2. **Dar por bueno el resumen inicial del agente.** Un resumen hecho sin contexto es una hipótesis, no un hecho. Se contrasta con el código.
3. **Escribir solo contexto técnico.** Sin el contexto de negocio de la empresa, el código resolverá el problema equivocado. Qué es una incidencia "crítica" depende de esta empresa y sale de `CONTEXT.md`.

### B.3 Checklist con IDs

Estos IDs se usan en los commits y en la bitácora.

#### Tareas

| ID | Tarea |
|---|---|
| E1 | Trabajar en la copia del monorepo, en la rama `feature/incident-manager` |
| E2 | Levantar el entorno según lo que indique el repo. Lo que haya que averiguar porque no está documentado es material para las reglas |
| E3 | Un commit por paso; el historial forma parte de la entrega |
| E4 | Usar el modo de agente adecuado en cada fase: Ask para explorar y resumir; Plan para definir reglas y el plan antes de tocar código; Agent para implementar |
| RC1 | Explorar la estructura del monorepo y pedir al agente un resumen |
| RC2 | Contrastar ese resumen con la estructura y el código reales |
| RC3 | Documentar las discrepancias entre el resumen y la realidad |
| RC4 | Identificar al menos 3 convenciones ya tomadas (nombrado, carpetas, dependencias, estilo, separación de responsabilidades) |
| RC5 | Identificar al menos 1 práctica mejorable y registrarla como propuesta, sin aplicarla |
| RG1 | Crear `.agents/rules` con reglas derivadas del código base |
| RG2 | Separar las reglas por ámbito: una regla por preocupación |
| RG3 | Definir para cada regla su forma de aplicación (siempre / patrón / solicitada por el agente / manual) y justificarla |
| RG4 | Escribir las reglas en términos verificables: qué se hace, qué no y a qué patrón de archivos aplica |
| RG5 | Iterar las reglas contra el flujo real: si una regla no cambia el comportamiento del agente, sobra o está mal escrita |
| BM1 | Crear `memory-bank/` con contexto de producto y negocio, stack tecnológico y estado actual |
| BM2 | El contexto de producto explica la empresa, quién usa el backoffice y qué significa una incidencia en su operación |
| BM3 | Incluir un plan de implementación construido con el agente antes de escribir código |
| BM4 | Actualizar la memoria al cerrar: el estado final no puede ser igual que el inicial |
| BM5 | Los nombres de entidades y los valores de dominio corresponden a `CONTEXT.md`; no vale una memoria genérica |
| V1 | Verificar registro, clasificación, asignación, recorrido completo de estados y trazabilidad |
| V2 | Revisar el código generado antes de commitear |
| V3 | Dejar constancia en el PR de qué reglas evitaron una desviación |
| EN1 | Subir la rama y abrir el PR contra la rama principal |
| EN2 | Incluir en el PR las discrepancias entre el resumen inicial y el repo |
| EN3 | Incluir en el PR las reglas definidas y la evidencia del código de la que sale cada una |
| EN4 | Incluir en el PR la propuesta de mejora registrada sin aplicar |

#### Criterios de evaluación

| ID | Criterio |
|---|---|
| C01 | `.agents/rules` existe y contiene al menos 3 reglas derivadas del código preexistente, no de preferencias personales |
| C02 | Cada regla declara explícitamente su forma de aplicación y su ámbito |
| C03 | Las reglas son verificables y no tienen ambigüedad |
| C04 | `memory-bank/` contiene contexto de producto y negocio, stack tecnológico y estado actual |
| C05 | El contexto de producto refleja la empresa asignada y su operación real, no una descripción genérica |
| C06 | Existe un plan de implementación versionado y el desarrollo entregado se corresponde con él |
| C07 | Existe un registro de discrepancias entre el resumen inicial y el código real |
| C08 | Se puede registrar una incidencia con canal, tipo y severidad, y asignarla a un área responsable |
| C09 | La incidencia recorre un ciclo de estados completo hasta su cierre |
| C10 | Los cambios de estado y de responsable se pueden consultar desde la ficha, con marca temporal y autor |
| C11 | El listado se puede filtrar por estado, severidad y área responsable |
| C12 | Hay una vista con el volumen de incidencias abiertas por severidad |
| C13 | Los catálogos de canales, tipos, severidades y áreas coinciden con `CONTEXT.md` |
| C14 | No se han introducido dependencias ni patrones ajenos a las convenciones del monorepo |
| C15 | El historial de commits separa los pasos; no hay un commit que agrupe todo |

### B.4 Plan paso a paso

| Paso | Modo | Qué se hace | IDs |
|---|---|---|---|
| 01 | Agent | Arranque: `AGENTS.md`, carpetas, encargo, índice de memoria, estado, regla 00 y bitácora | E1, E3, RG1, BM1 · C15 |
| 02 | Agent | Guardar el resumen inicial tal cual | RC1, E4 |
| 03 | Agent | Levantar el entorno y registrar hallazgos | E2 |
| 04 | Agent | Contraste y discrepancias | RC2, RC3 · C07 |
| 05 | Agent | Convenciones y propuestas de mejora | RC4, RC5 |
| 06 | Agent + chat nuevo | Pruebas de reglas: diseño y línea base | RG5 |
| 07 | Agent | Escribir las reglas | RG1–RG4 · C01–C03 |
| 08 | Agent + chat nuevo | Repetir las pruebas con las reglas y ajustarlas | RG5 |
| 09 | Agent | Contexto de producto y catálogos (🛑 validación) | BM1, BM2, BM5 · C05, C13 |
| 10 | Agent | Stack tecnológico y estado del proyecto | BM1 · C04 |
| 11 | Plan → Agent | Plan de implementación | BM3, E4 · C06 |
| 12–16 | Agent | Implementación por porciones | V2, V3 · C08–C14 |
| 17 | Agent | Verificación de principio a fin | V1 |
| 18 | Agent | Cierre de la memoria | BM4 |
| 19 | Agent | Auditoría y PR | EN1–EN4, V3 · C01–C15 |

#### Paso 01 — Arranque

Se hace en el chat inicial, con el prompt del encargo. El detalle de lo que se hizo queda en la entrada del Paso 01 de `historial-commits.md`.

#### Paso 02 — Resumen inicial (la hipótesis)

Se hace en el mismo chat del arranque, porque el resumen solo está en el Anexo A de aquel prompt.

1. Copia el Anexo A **literalmente** en `memory-bank/registro/resumen-inicial-agente.md`.
2. Añade una cabecera con:
   - la fecha,
   - el modo (Ask),
   - la nota: "Generado sin contexto previo. No editar: es la hipótesis de partida".
3. No lo corrijas ni lo comentes aquí. El contraste es el Paso 04.

#### Paso 03 — Levantar el entorno

1. Sigue **solo** lo que indique el repo: README, devcontainer, scripts y manifiestos.
2. Ejecuta la instalación, el lint, los tests y el arranque.
3. En `memory-bank/registro/hallazgos-entorno.md`, anota:
   - cada comando que ejecutes,
   - su resultado real,
   - todo lo que tuviste que averiguar porque no estaba documentado. Márcalo como candidato a regla.
4. **No modifiques configuración** para que algo funcione sin preguntar antes.

#### Paso 04 — Contraste y discrepancias

1. Divide el resumen inicial en afirmaciones sueltas, cada una comprobable por separado.
2. Para cada afirmación, anota:
   - la evidencia real (ruta, línea o comando),
   - el veredicto: ✅ correcta, ⚠️ imprecisa, ❌ falsa o ❓ no verificable.
3. Añade las **➕ omisiones**: cosas relevantes del repo que el resumen no mencionó.
4. Cierra con 3 a 5 conclusiones: qué tipo de error comete un agente sin contexto y, por tanto, qué tiene que quedar escrito en reglas o en memoria.
5. Guárdalo todo en `memory-bank/registro/discrepancias.md`.

#### Paso 05 — Convenciones y propuestas de mejora

**Convenciones**, en `registro/convenciones.md`:

- Identifica al menos 3, y lo ideal son 5 o 6, repartidas entre las distintas categorías del RC4.
- Para cada una, anota:
  - el enunciado,
  - la evidencia cuantificada,
  - las excepciones que hayas encontrado,
  - si se convertirá en regla o no.

**Propuestas de mejora**, en `registro/propuestas-mejora.md`:

- Al menos una práctica mejorable.
- Para cada una, anota:
  - la situación actual, con evidencia,
  - la propuesta,
  - el beneficio,
  - el riesgo o coste,
  - `Estado: propuesta, no aplicada`.

#### Paso 06 — Pruebas de reglas: diseño y línea base

1. **Diseña una prueba** por cada convención que vaya a convertirse en regla. Si es natural, una misma prueba puede cubrir dos. Cada prueba tiene dos partes:
   - un prompt corto que tiente al agente a desviarse de esa convención,
   - el comportamiento que esperamos cuando la regla exista.
2. **Escríbelas** en `registro/pruebas-reglas.md`.
3. **Dame el texto exacto de cada prueba.** Yo las ejecuto en un chat nuevo en modo Agent. En este momento `.agents/rules/` solo contiene la regla 00, así que el resultado es la línea base: cómo se comporta el agente sin reglas de código.
4. **Si una prueba crea archivos**, los descarto yo después; no se commitean.
5. **Cuando te pegue los resultados**, anota el "comportamiento sin reglas" de cada prueba.

#### Paso 07 — Escribir las reglas

1. **Escribe una regla por preocupación** en `.agents/rules/`, siguiendo el formato del apartado 5 de `AGENTS.md`.
2. **Mínimo 3 reglas con `origen: codigo`**, además de la `00`. Salen de `convenciones.md` y de `hallazgos-entorno.md`.
3. **Opcionalmente, reglas de dominio**: valores de catálogo solo desde `contexto-producto.md`, y trazabilidad de los cambios de incidencias. Llevan `origen: briefing` o `encargo` y **no cuentan** para el mínimo de 3.
4. **Elige la forma de aplicación que pida cada regla** y justifícala. No las pongas todas en `siempre`.
5. **Revisa cada regla** contra la lista de palabras vetadas.
6. **Indica en cada regla** qué prueba del Paso 06 la comprueba.

#### Paso 08 — Repetir las pruebas con las reglas

1. **Dame de nuevo el texto de las pruebas del Paso 06.** Yo las ejecuto en un chat nuevo en modo Agent. `AGENTS.md` se carga solo y hace que el agente lea las reglas.
2. **Pídeme que compruebe en *References*** que aparece `AGENTS.md`, y que te pegue los resultados.
3. **Anota el "comportamiento con reglas"** de cada prueba y compáralo con la línea base.
4. **Ajusta o elimina las reglas que no cambien nada**: o sobran o están mal escritas.

Si hace falta más de una ronda, cada ronda es un commit (`Paso 08b`, `08c`, …).

#### Paso 09 — Contexto de producto y catálogos

1. **Lee `CONTEXT.md` completo.**
2. **Escribe `memory-bank/contexto-producto.md`** con estas secciones:
   - **La empresa:** qué es, dónde opera, su tamaño y cómo se organiza. Como máximo 15 líneas.
   - **El problema:** qué problema resuelve el gestor en esta empresa en concreto.
   - **Quién usa el backoffice:** los roles concretos que aparecen en `CONTEXT.md` y qué necesita cada uno del gestor.
   - **Qué es una incidencia en esta operación:** con ejemplos ligados a lo que describe `CONTEXT.md`.
   - **Qué significa "crítica" aquí:** un criterio operativo concreto, no genérico.
   - **Catálogos:** canales, tipos, severidades, áreas responsables y estados. Para cada valor, indica:
     - la etiqueta exacta,
     - el identificador en código, según la convención del repo,
     - el origen: `literal` (cita la sección), `derivado` (sección más el razonamiento en una línea) o `pendiente` (no tiene base en `CONTEXT.md`).
   - **Glosario de entidades:** nombre de dominio frente a identificador en código.
   - **Fuera de alcance.**
3. **Comprueba qué catálogos define `CONTEXT.md` de forma explícita y cuáles no.** No rellenes los huecos con valores genéricos de una herramienta de *ticketing*, ni inventes datos que `CONTEXT.md` no da (por ejemplo, nombres de locales).
4. 🛑 **Parada de validación.** No se escribe código hasta que yo valide los catálogos.

#### Paso 10 — Stack tecnológico y estado del proyecto

1. **Escribe `memory-bank/stack-tecnologico.md`.** Recoge solo lo que un agente necesita y no deduce rápido leyendo el repo:
   - las piezas del monorepo,
   - el gestor de dependencias,
   - los comandos clave: instalar, lint, test y arrancar,
   - la persistencia,
   - dónde vive cada tipo de código.

   Enlaza las reglas de `.agents/rules/` en lugar de repetirlas.
2. **Completa `memory-bank/estado-actual.md`:**
   - en "Estado del proyecto", qué existe hoy en el repo,
   - en "Decisiones cerradas", las tomadas hasta ahora.
3. **Actualiza `memory-bank/README.md`** si hace falta.

#### Paso 11 — Plan de implementación (modo Plan → modo Agent)

1. **Pídeme que cambie a modo Plan.** En ese modo construimos juntos el plan y no se escribe código. El plan debe cubrir:
   1. Dónde vive el gestor dentro del monorepo, y qué regla lo justifica.
   2. El modelo de datos:
      - **Incidencia**: canal, tipo, severidad, área responsable, estado, título, descripción, fechas y autor de creación.
      - **Evento de historial**: incidencia, tipo de cambio, valor anterior, valor nuevo, autor y marca temporal.
   3. El ciclo de estados: qué transiciones están permitidas, cuáles están prohibidas y cómo se cierra una incidencia.
   4. De dónde sale el autor. Si el repo ya tiene un mecanismo de identidad, se usa ese. Si no, cómo se registra el autor sin crear un sistema nuevo. Esta decisión la valido yo.
   5. Cómo se guardan y se muestran las marcas temporales, teniendo en cuenta dónde opera la empresa según `CONTEXT.md`.
   6. La persistencia, usando lo que ya use el repo.
   7. La interfaz o API:
      - registro de incidencias,
      - ficha con su historial,
      - cambio de estado y de área,
      - listado con filtros por estado, severidad y área,
      - vista de volumen de incidencias abiertas por severidad.
   8. Las pruebas, siguiendo la convención del repo y sin añadir frameworks.
   9. Los pasos de implementación, que serán los commits, cada uno con sus IDs.
   10. Las decisiones abiertas y lo que queda fuera de alcance.
2. **Cuando vuelva a modo Agent** y te diga "guarda el plan":
   - escribe `memory-bank/plan-implementacion.md` como versión 1,
   - actualiza `estado-actual.md`.
3. **Si el plan cambia durante la implementación**, actualízalo en el mismo commit que el cambio y anótalo en la bitácora, en "Cambios respecto al plan".

#### Pasos 12–16 — Implementación por porciones

Estas son las porciones por defecto. El plan aprobado manda: si las reordena, sigue el plan.

| Paso | Porción | Criterios |
|---|---|---|
| 12 | Catálogos, modelo de datos y persistencia | C13, C14 |
| 13 | Registro con canal, tipo y severidad, y asignación a un área | C08 |
| 14 | Ciclo de estados, historial trazable y ficha | C09, C10 |
| 15 | Listado con filtros por estado, severidad y área | C11 |
| 16 | Vista de volumen de incidencias abiertas por severidad | C12 |

En cada porción:

1. **Implementa solo esa porción.**
2. **Cumple las reglas** y la trazabilidad de B.1. Si una regla te frena, anótalo en `registro/desviaciones-evitadas.md`:
   - qué ibas a hacer,
   - qué regla lo impidió,
   - qué hiciste en su lugar.

   Anota también las desviaciones que yo detecte al revisar.
3. **Ejecuta las comprobaciones del stack**: lint, tests y arranque.
4. **Haz la parada** con la guía de revisión de cada archivo y espera el OK.

#### Paso 17 — Verificación de principio a fin

1. **Haz el recorrido completo con evidencia real:**
   - crea incidencias, al menos una por canal,
   - clasifícalas y asígnalas,
   - reasigna alguna de área,
   - recorre todos los estados hasta el cierre,
   - intenta una transición prohibida,
   - consulta la ficha y comprueba que el historial muestra autor y marca temporal,
   - filtra el listado por cada filtro,
   - mira la vista de volumen antes y después de cerrar una incidencia.
2. **Anótalo en `registro/verificacion.md`** con esta tabla:

   | Escenario | Pasos | Esperado | Obtenido | ✅/❌ |
   |---|---|---|---|---|

3. **Si algo falla**, se arregla en un paso aparte (17b, 17c…) antes de seguir.

#### Paso 18 — Cierre de la memoria

Actualiza:

- **`estado-actual.md`**: el estado final tiene que ser distinto del inicial.
- **`stack-tecnologico.md`**: si ha cambiado algo.
- **`plan-implementacion.md`**: marca lo entregado y las desviaciones respecto al plan.
- **`memory-bank/README.md`**: que refleje todos los archivos que existen.
- **`AGENTS.md`**: comprueba que sigue describiendo bien dónde está cada cosa y cómo se trabaja.

#### Paso 19 — Auditoría y PR

1. **Auditoría.** Construye esta tabla con los criterios C01–C15:

   | Criterio | Evidencia (archivo o commit) | ✅/❌ |
   |---|---|---|

   Si hay algún ❌, para.
2. **Comprueba el historial.** En `git log --oneline <rama-principal>..HEAD`, cada paso debe ir en su propio commit.
3. **Comprueba las dependencias.** El diff de los manifiestos de dependencias contra la rama principal no debe añadir nada que no se haya aprobado.
4. **Comprueba las ubicaciones:**
   - las reglas solo están en `.agents/rules/`,
   - la memoria solo está en `memory-bank/`,
   - todos los enlaces de `AGENTS.md` y de `memory-bank/README.md` apuntan a archivos que existen.
5. **Redacta la descripción del PR** en `registro/descripcion-pr.md`, con estas secciones:
   1. Resumen.
   2. Cómo trabaja el agente: `AGENTS.md`, `.agents/rules/` y `memory-bank/`.
   3. Discrepancias entre el resumen inicial y el repo.
   4. Reglas definidas: una tabla con regla, forma de aplicación, alcance y evidencia en el código.
   5. Propuesta(s) de mejora, sin aplicar.
   6. Reglas que evitaron desviaciones, con evidencia de `desviaciones-evitadas.md` y `pruebas-reglas.md`.
   7. Cómo verificar el gestor.
   8. Mapa del checklist a los commits.
6. **Haz la parada.** Con mi OK:
   - haz el commit,
   - `git push -u origin feature/incident-manager`,
   - `gh pr create --base <rama-principal> --head feature/incident-manager --title "<título>" --body-file memory-bank/registro/descripcion-pr.md`.

   Si `gh` no está disponible o falla, dame el texto y abro yo el PR.
7. **No hagas merge.**
