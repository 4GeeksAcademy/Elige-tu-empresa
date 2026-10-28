# Encargo en curso: gestor de inventario (SDD)

## 1. El encargo

**Qué pide el CTO.** El equipo de operaciones necesita tres cosas:

- dar de alta artículos de inventario,
- registrar sus movimientos de entrada, salida y ajuste,
- saber en todo momento qué está por debajo del punto de reorden.

Los nombres de las entidades, las unidades de medida y los valores de dominio salen de `company-BRIEFING.md` (raíz del repo). No se inventan.

**Lo no negociable.** El stock disponible de un artículo **se calcula** a partir de sus movimientos. No existe ningún endpoint, campo de formulario ni operación que lo edite directamente. Esto tiene que quedar como criterio de aceptación explícito y verificado por tests.

**Cómo se trabaja: Spec Driven Development.**

1. **Primero el spec.** El CTO lo revisa y lo aprueba, y solo después se pasa al plan, a las tareas y al código.
2. **Criterios en formato EARS**, verificables y con un identificador único cada uno.
3. **Tareas pequeñas.** Cada tarea se puede verificar por separado.
4. **Trazabilidad completa.** Cada tarea y cada commit quedan conectados con el criterio de aceptación que verifican. Se tiene que poder ir de un requisito a su test y de un test a su commit.
5. **Cambios de requisito.** Llegará un cambio de requisito a mitad del trabajo:
   - se edita primero el spec,
   - después el plan, si le afecta,
   - y se regeneran solo las tareas afectadas.

   Nunca al revés: no se parchea código sin haber cambiado antes el spec.

**Proporción.** El spec es un contrato, no un tratado. El nivel de detalle se justifica en el invariante de stock y en los comportamientos no deseados. Los campos triviales del formulario de artículo se describen en una línea.

---

## 2. Las tres capas y dónde vive cada cosa

| Archivo | Capa | Contiene | No contiene |
|---|---|---|---|
| `specs/inventory-manager/spec.md` | El **qué** | Comportamiento, contratos de cada operación, invariantes, criterios EARS con ID, decisiones pendientes e historial de versiones | Tablas, módulos, rutas HTTP ni nombres de funciones |
| `specs/inventory-manager/plan.md` | El **cómo** | Decisiones de arquitectura justificadas: modelo de datos, cómo se calcula el stock, dónde vive esa lógica, API, backoffice, semilla y pruebas | Los criterios repetidos: los cita por ID |
| `specs/inventory-manager/tasks.md` | El **orden** | Tareas atómicas, cada una con los IDs de criterio que implementa, su verificación, su estado y su commit | Decisiones nuevas de arquitectura |
| `memory-bank/` | Memoria | Encargo, estado, bitácora y registros, igual que en el encargo anterior | Copias de las tres capas: las enlaza |

**IDs.**

- **Criterios:** `INV-001`, `INV-002`… **Tareas:** `T-01`, `T-02`…
- Los IDs **nunca se renumeran ni se reutilizan**.
  - Un criterio que deja de aplicar se marca `retirado`.
  - Una tarea que deja de aplicar se marca `sustituida por T-xx`.

**Tests.** Cada test incluye en su nombre el ID del criterio que verifica, en camelCase, igual que los tests existentes. Ejemplo: `testInv012RejectsOutboundBelowZero`.

---

## 3. Lo que ya existe (compruébalo antes de usarlo)

El repositorio ya tiene un servicio y un backoffice. Úsalos como precedente: no se añaden dependencias, frameworks ni patrones nuevos.

- **Servicio:** `services/api/`.
  - Python ≥ 3.12, solo biblioteca estándar.
  - API JSON con `http.server` (`server.py`).
  - SQLite con `sqlite3` (`database.py`): `CHECK` de catálogos y triggers que impiden `UPDATE` y `DELETE` en tablas de solo añadir (`historyEvents`).
  - Casos de uso en módulos por dominio (`incidents.py`), catálogos en `catalogs.py` y modelos en `models.py`.
- **Pruebas:** `unittest`, en `services/api/tests/`. Se ejecutan con:

  ```
  PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v
  ```
- **Backoffice:** `uis/backoffice/`, con HTML, CSS y JavaScript sin framework, servido desde el mismo origen que la API.
- **Reglas aplicables:**
  - `01` (componentes por responsabilidad),
  - `02` (guías bilingües),
  - `03` (paquetes y recursos compartidos),
  - `04` (camelCase).
- **Fechas:** marcas temporales en UTC, como en el gestor de incidencias.

---

## 4. Decisiones de dominio

El briefing deja huecos. Estas decisiones ya están **validadas por el usuario el 2026-10-28**; el spec las recoge en su sección "Decisiones de dominio" con origen `validada` y no las vuelve a preguntar. Si al escribir el spec aparece un hueco que no está aquí, añádelo como `pendiente` y pregunta.

### 4.1 Lo que el briefing fija (origen `literal`)

- **Catálogos:** unidades `kg`, `g`, `l`, `ml`, `unit`; categorías `meat`, `produce`, `sauces_condiments`, `beverages`, `packaging`, `cleaning_supplies`; tipos de movimiento `inbound`, `outbound`, `adjustment`.
- **Stock por local.** El stock se controla por local; el mismo ingrediente en dos locales son dos artículos distintos.
- **Reorden.** La señal salta cuando el stock es **igual o menor** que `reorder_point`. Se define por artículo, y por tanto por local.
- **Stock negativo.** Un `outbound` que dejaría el stock por debajo de cero se rechaza.
- **Referencias inexistentes.** Un `outbound` o `adjustment` con un artículo o un lote inexistente se rechaza.
- **Informe.** `waste` y `theft` se distinguen en cualquier informe de stock.

### 4.2 Decisiones validadas (origen `validada`)

1. **Nombres.**
   - Los **valores de catálogo** se usan literalmente, tal como aparecen en §4.1: el briefing prohíbe renombrarlos y la regla 04 conserva los nombres impuestos por un contrato externo.
   - Los **campos en código** van en camelCase (`locationId`, `unitOfMeasure`, `reorderPoint`, `lotCode`, `expiryDate`, `receivedAt`, `movementType`, `createdAt`…), con una tabla de correspondencia con los nombres del briefing en el glosario del spec.
   - Los **identificadores propios** (locales, artículos semilla) van en camelCase.
2. **Locales.** Hay exactamente cuatro:

   | ID | Nombre | País |
   |---|---|---|
   | `laArepita` | La Arepita | Colombia |
   | `queChille` | QueChille | Colombia |
   | `theBigSauce` | The BigSauce | Estados Unidos (Florida) |
   | `chilliBeans` | ChilliBeans | Estados Unidos (Florida) |

3. **Motivo.** Todo movimiento lleva un motivo obligatorio:
   - `adjustment`: catálogo cerrado `waste`, `theft`, `count_correction`;
   - `inbound` y `outbound`: texto libre no vacío.
4. **Signo de las cantidades.**
   - En `inbound` y `outbound`, la cantidad es positiva.
   - En `adjustment`, la cantidad lleva signo y no puede ser cero. `waste` y `theft` siempre son negativos; `count_correction` puede ser positivo o negativo.
   - **Ningún movimiento puede dejar el stock por debajo de cero.** En `outbound` es literal del briefing (§7); en `adjustment` se extiende la misma restricción. Los dos se rechazan.
5. **Lotes.**
   - **Control de lote** significa que la categoría es `meat` o `produce`. En esos artículos, todo movimiento lleva lote.
   - **En el resto de categorías** el lote es opcional en cada movimiento. Si se indica, tiene que existir.
   - **Un lote siempre pertenece a su artículo.** Si se referencia un lote de otro artículo, el movimiento se rechaza.
   - **El stock también se calcula por lote,** a partir de sus movimientos, y ningún movimiento puede dejar un lote en negativo.
6. **Stock caducado.** Un lote está caducado cuando su `expiryDate` es anterior a la fecha actual en UTC.
   - **El stock disponible no cambia.** Sigue siendo la suma de todos los movimientos, tal como dice el invariante del briefing (§4), y la señal de reorden usa ese mismo total.
   - **Las salidas se rechazan.** Un `outbound` que referencia un lote caducado se rechaza, aunque haya stock suficiente.
   - **La única forma de retirarlo** es un `adjustment` con motivo `waste`. Cualquier otro motivo sobre un lote caducado se rechaza.
   - **En el backoffice y en el informe**, el stock caducado se ve separado por lote: "X disponibles, de ellos Y caducados (lote …)".
7. **Baja de artículo.**
   - Solo se puede dar de baja un artículo sin movimientos.
   - Si tiene movimientos, la baja se rechaza.
   - No se añade ningún campo de activo/inactivo.
8. **Edición de artículo.**
   - `name` y `reorderPoint` se pueden editar siempre.
   - `locationId`, `category` y `unitOfMeasure` solo se pueden editar si el artículo no tiene movimientos.
   - El stock nunca se edita.
9. **Cantidades.**
   - En `kg` y `l`, hasta 3 decimales; en `g`, `ml` y `unit`, enteros.
   - Ninguna cantidad se guarda ni se suma con coma flotante.
10. **Informe de stock de un artículo.** Muestra:
    - el stock disponible,
    - el total de `inbound` y el total de `outbound`,
    - los ajustes desglosados por motivo, con `waste`, `theft` y `count_correction` por separado,
    - el stock por lote, con su fecha de caducidad.

### 4.3 Datos semilla

Todo el stock semilla nace de movimientos, registrados con los mismos casos de uso que la API. No hay inserciones directas de stock.

Hay 16 artículos, 4 por local, y entre todos cubren las seis categorías:

| Local | Artículo | Categoría | Unidad | `reorderPoint` | Lote |
|---|---|---|---|---|---|
| laArepita | Punta de anca de res | meat | kg | 20 | sí |
| laArepita | Pechuga de pollo | meat | kg | 15 | sí |
| laArepita | Cebolla cabezona | produce | kg | 10 | sí |
| laArepita | Salsa de ajo de la casa | sauces_condiments | l | 5 | no |
| queChille | Costilla de cerdo | meat | kg | 12 | sí |
| queChille | Cilantro | produce | kg | 2 | sí |
| queChille | Jugo de lulo | beverages | l | 10 | no |
| queChille | Desengrasante | cleaning_supplies | l | 4 | no |
| theBigSauce | Brisket de res | meat | kg | 25 | sí |
| theBigSauce | Salsa BBQ de la casa | sauces_condiments | l | 8 | no |
| theBigSauce | Refresco de cola | beverages | unit | 48 | no |
| theBigSauce | Envases para llevar | packaging | unit | 200 | no |
| chilliBeans | Alitas de pollo | meat | kg | 18 | sí |
| chilliBeans | Jalapeños | produce | kg | 3 | sí |
| chilliBeans | Servilletas | packaging | unit | 500 | no |
| chilliBeans | Desinfectante | cleaning_supplies | l | 5 | no |

Las cantidades de los movimientos las eliges tú, con estas condiciones:

- **Historial por artículo:** cada artículo tiene al menos un `inbound`, un `outbound` y un `adjustment`.
- **Motivos de ajuste:** entre todos los artículos aparecen `waste`, `theft` y `count_correction`.
- **Reorden:** al terminar la semilla, *Salsa de ajo de la casa* (laArepita) y *Envases para llevar* (theBigSauce) quedan en su `reorderPoint` o por debajo. El resto queda por encima.
- **Lote caducado:** *Cilantro* (queChille) tiene un lote con `expiryDate` fija en el pasado (`2026-10-01`), que todavía conserva stock. El resto de lotes caduca en el futuro; el plan decide cómo se calculan sus fechas para que no caduquen con el paso del tiempo.

---

## 5. Commits en este encargo

Se aplica la regla 00 tal cual. En este encargo, la línea `Checklist:` lleva los IDs del propio spec:

| Tipo de paso | Línea `Checklist:` | Ámbito del asunto |
|---|---|---|
| Spec, plan o tareas | `spec vX.Y (INV-001–INV-0NN)`, `plan vX.Y` o `tasks vX.Y` | `specs` |
| Implementación de una tarea | `T-NN (INV-0AA, INV-0BB)` | `inventory` |
| Arranque, reglas y memoria | `—` | `memory-bank` o `rules` |

En la parada, "Checklist cubierto" son las tareas `T-xx` y "Criterios" son los `INV-xxx`.

Ejemplo de commit de implementación:

```
feat(inventory): rechazar salidas que dejan stock negativo

Paso: 06
Checklist: T-07 (INV-012)
- Prueba testInv012RejectsOutboundBelowZero
- Validación del stock y alta del movimiento en la misma transacción
```

---

## 6. Plan paso a paso

| Paso | Qué se hace | Commits |
|---|---|---|
| 01 | Arranque del encargo | 1 |
| 02 | Reglas para trabajar guiado por el spec | 1 |
| 03 | Spec v1.0 (🛑 aprobación) | 1 |
| 04 | Plan v1.0 (🛑 aprobación) | 1 |
| 05 | Tareas v1.0 (🛑 aprobación) | 1 |
| 06 | Implementación | 1 por tarea |
| 07 | Verificación y trazabilidad | 1 |
| 08 | Cambio de requisito (cuando llegue) | 1 por capa + 1 por tarea regenerada |
| 09 | Cierre de la memoria y PR | 1 |

### Paso 01 — Arranque del encargo

1. **Comprueba la rama.** Ya está creada en el Codespace. Comprueba que:
   - `git branch --show-current` devuelve `feature/inventory-manager`,
   - `git status` está limpio,
   - `git log --oneline -1 main` aparece en `git log --oneline -5`, es decir, la rama parte del `main` que contiene el merge del gestor de incidencias.

   Si algo no cuadra, para y avísame.
2. **Comprueba el briefing.** Verifica que existe `company-BRIEFING.md` en la raíz. Si no existe, para y pídemelo. Si existe y no está versionado, inclúyelo en este commit.
3. **Archiva el encargo anterior:** `git mv memory-bank/encargo.md memory-bank/registro/encargo-incidencias.md`.
4. **Crea el nuevo `memory-bank/encargo.md`.**
   - Título: `# Encargo en curso: gestor de inventario (SDD)`.
   - Debajo, copia literalmente las secciones 1 a 7 de este documento.
5. **Actualiza `AGENTS.md`** con solo estos cambios:
   - Rama de trabajo: `feature/inventory-manager`.
   - En "Dónde está cada cosa", añade:
     - una fila para `specs/<funcionalidad>/` (spec, plan y tareas),
     - una fila para `company-BRIEFING.md` (dominio del inventario).
   - En "Fuentes de verdad", añade:
     - dominio del inventario → `company-BRIEFING.md`,
     - comportamiento esperado → `specs/inventory-manager/spec.md`.
   - En "Al empezar una sesión", añade un paso: "si hay un encargo SDD en curso, lee su `spec.md`, `plan.md` y `tasks.md`".
6. **Actualiza `memory-bank/README.md`:**
   - el encargo nuevo,
   - `registro/encargo-incidencias.md` y `plan-implementacion.md` como históricos del gestor de incidencias, que se leen bajo demanda,
   - un enlace a `specs/inventory-manager/`,
   - los registros nuevos de este encargo: `registro/trazabilidad-inventario.md`, `registro/verificacion-inventario.md` y `registro/cambio-requisito-inventario.md`.
7. **Actualiza `memory-bank/estado-actual.md`.** "Hecho" queda como histórico y "En curso / Siguiente" pasan al Paso 02 de este encargo.
8. **Haz la parada** y, con el `OK commit`, commitea.

### Paso 02 — Reglas para trabajar guiado por el spec

1. **Crea `.agents/rules/05-desarrollo-guiado-por-spec.md`** con el formato de `AGENTS.md`:
   - `aplicacion: siempre`, `applyTo: "**"` y `origen: encargo`. Justificación: el orden spec → plan → tareas → código gobierna cada paso de este encargo.
   - **Se hace:**
     - todo cambio de código pertenece a una tarea de `tasks.md` que cita al menos un `INV`,
     - el commit de implementación lleva `Checklist: T-NN (INV-…)`,
     - un cambio de requisito sigue este orden, con cada capa en su propio commit: primero el spec (con nueva versión y una entrada en su historial), después el plan si le afecta, después solo las tareas afectadas y al final el código.
   - **No se hace:**
     - código sin tarea,
     - editar el spec para que cuadre con un código ya escrito,
     - una tarea que agrupe criterios no relacionados,
     - reescribir el spec o la lista de tareas completos por un cambio puntual,
     - renumerar o reutilizar IDs.
   - **Cómo comprobarlo:** con comandos `git log` y `grep`. Ejemplos:
     - los commits `feat(inventory)` y `test(inventory)` contienen `Checklist: T-` y `INV-`,
     - el commit que cambia el spec es anterior a los commits de código del mismo cambio.
2. **Amplía la regla `04-nombres-camel-case`** con una línea en "Se hace": los valores de catálogo que fija `company-BRIEFING.md` se conservan literalmente, porque son un contrato externo. Añade la evidencia: §2 del briefing, "No inventes otros ni los renombres".
3. **Haz la parada** y, con el `OK commit`, commitea.

### Paso 03 — Spec v1.0

1. **Lee `company-BRIEFING.md` completo.**
2. **Escribe `specs/inventory-manager/spec.md`** con la plantilla del §7.1.
3. **Escribe los criterios EARS.** Como mínimo deben cubrir:
   - **Alta, edición, listado y baja de artículos**, con los campos del §3.1 del briefing.
   - **Movimientos `inbound`, `outbound` y `adjustment`**, con motivo, marca temporal y reglas de lote.
   - **El invariante, en dos criterios ubicuos explícitos:**
     - el stock disponible de un artículo en un local se calcula a partir de sus movimientos,
     - no existe ninguna operación que edite el stock directamente.
   - **Comportamientos no deseados** (plantilla "Si … entonces …"):
     - un `outbound` que dejaría el stock negativo,
     - un `outbound` o `adjustment` con un artículo inexistente,
     - un `outbound` o `adjustment` con un lote inexistente,
     - un artículo con control de lote sin lote,
     - un ajuste sin motivo.
   - **Reorden:** la señal por local cuando el stock es igual o menor que `reorder_point`.
   - **Informe de stock:** `waste` y `theft` aparecen por separado.
   - **Caducados:** el comportamiento del §4.2.
   - **Datos semilla:** lo que fija el §4.3.
4. **Recoge el §4 en la sección "Decisiones de dominio" del spec**, con su origen (`literal` o `validada`). Si encuentras un hueco que el §4 no cubre, añádelo como `pendiente` y pregúntame en la parada.
5. 🛑 **Parada de aprobación.** El spec queda en `Estado: borrador` hasta que yo lo apruebe. Si te pido cambios, edítalo y vuelve a parar. Cuando lo apruebe, pásalo a `Estado: aprobado`, versión 1.0, y commitea.

### Paso 04 — Plan v1.0

1. **Escribe `specs/inventory-manager/plan.md`** con la plantilla del §7.2. Debe cubrir:
   - **El modelo de datos**, sin columna de stock.
   - **Los movimientos como tabla de solo añadir**, protegida con triggers como `historyEvents`.
   - **El cálculo del stock:** una única función que lo calcula, y que usan la API, el backoffice, la señal de reorden y el informe.
   - **Concurrencia:** la comprobación del stock y la inserción del movimiento van en la misma transacción.
   - **Cantidades:** cómo se guardan sin coma flotante.
   - **Ubicación:** dónde viven el módulo, las rutas HTTP y la vista del backoffice, y cómo se aplican las reglas 01 y 03.
   - **Base de datos:** si se comparte con la de incidencias.
   - **Datos semilla:**
     - dónde viven y cómo se ejecutan,
     - todo el stock semilla nace de movimientos, insertados con los mismos casos de uso.
   - **La estrategia de pruebas.**
2. **Justifica cada decisión** con evidencia del repo o con un razonamiento. Cita los criterios por su ID y no los repitas.
3. 🛑 **Parada de aprobación.** Con mi OK, versión 1.0 y commit.

### Paso 05 — Tareas v1.0

1. **Escribe `specs/inventory-manager/tasks.md`** con la plantilla del §7.3.
2. **Tamaño de cada tarea:**
   - un criterio, o un grupo pequeño de criterios estrechamente relacionados,
   - verificable de forma aislada con sus propios tests,
   - si una tarea es difícil de verificar sola, es demasiado grande: divídela.
3. **Orden por dependencias.** Un orden orientativo:
   1. esquema y catálogos,
   2. artículos (alta, edición, listado y baja),
   3. lotes,
   4. movimientos de entrada,
   5. salidas con su rechazo por stock negativo,
   6. ajustes con motivo,
   7. referencias inexistentes,
   8. cálculo del stock e informe,
   9. señal de reorden,
   10. semilla,
   11. rutas HTTP,
   12. vista del backoffice.
4. **Cobertura.** Todos los `INV` del spec quedan cubiertos por al menos una tarea; ninguno se queda huérfano.
5. 🛑 **Parada de aprobación.** Con mi OK, versión 1.0 y commit.

### Paso 06 — Implementación (un commit por tarea)

Para cada tarea, en el orden de `tasks.md`:

1. **Lee la tarea, sus criterios en el spec y las decisiones del plan que la afectan.**
2. **Escribe primero los tests** que verifican sus `INV`, con el ID en el nombre del test. Ejecútalos y comprueba que fallan.
3. **Implementa lo mínimo** para que pasen, sin adelantar trabajo de otras tareas.
4. **Ejecuta la suite completa.** Todo debe estar en verde.
5. **Actualiza `tasks.md`:** estado `hecha` y el asunto del commit.
6. **Haz la parada**, con la guía de revisión de cada archivo y el resultado real de los tests. Con el `OK commit`, commitea test y código juntos.

**Si durante la implementación:**

- **Una tarea necesita algo que no está en el plan**, para y pregunta.
- **El spec resulta incompleto o incorrecto**, para. Se corrige primero el spec (con nueva versión y su historial), después el plan y las tareas, y solo entonces el código, cada uno en su commit.
- **Una regla te frena**, anótalo en la entrada de la bitácora, en "Desviaciones evitadas".

### Paso 07 — Verificación y trazabilidad

1. **Ejecuta la suite completa** y guarda el resultado real.
2. **Crea `memory-bank/registro/trazabilidad-inventario.md`** con esta tabla y una fila por cada `INV`:

   | INV | Tipo EARS | Tarea | Test(s) | Commit |
   |---|---|---|---|---|

   No puede haber ningún `INV` sin test. Comprueba que hay tests de los comportamientos no deseados, no solo del camino feliz. Si falta alguno, crea su tarea y sigue el ciclo del Paso 06.
3. **Haz el recorrido real con los datos semilla:** arranca el servidor, ejecuta la semilla y comprueba lo siguiente con peticiones HTTP y en el backoffice:
   - el stock por local,
   - el rechazo de un `outbound` que deja stock negativo,
   - el rechazo de un lote inexistente,
   - la señal de reorden en los artículos semilla que están en su punto o por debajo,
   - el informe con `waste` y `theft` por separado,
   - el lote caducado de Cilantro (queChille): el stock caducado se ve separado, un `outbound` de ese lote se rechaza y un `adjustment` con motivo `waste` lo retira y aparece en el informe.
4. **Anota el recorrido en `memory-bank/registro/verificacion-inventario.md`** con esta tabla:

   | Escenario | Pasos | Esperado | Obtenido | ✅/❌ |
   |---|---|---|---|---|

5. **Haz la parada** y commitea.

### Paso 08 — Cambio de requisito (cuando yo te lo pegue)

No empieces este paso hasta que te pegue el cambio. Si llega antes de terminar el Paso 06, termina la tarea en curso y atiende el cambio.

- **08 — Análisis.** Sin tocar ningún archivo del spec ni del código:
  1. Guarda el texto literal del cambio en `memory-bank/registro/cambio-requisito-inventario.md`.
  2. Añade el análisis de impacto:
     - qué secciones y qué `INV` del spec cambian, se añaden o se retiran,
     - si el plan cambia,
     - qué tareas quedan afectadas: las pendientes se rehacen; las ya hechas se marcan `sustituida por T-xx` y tienen tarea nueva.
  3. 🛑 Parada de validación y commit.
- **08a — Spec.**
  1. Edita solo las secciones afectadas.
  2. Sube la versión menor (por ejemplo, 1.1).
  3. Añade una entrada al historial con las secciones cambiadas.
  4. 🛑 Parada de aprobación y commit.
- **08b — Plan.** Solo si le afecta: edita las decisiones afectadas y añade su entrada al historial. Si no le afecta, anota "sin cambios en el plan" en el registro del cambio. Parada y commit.
- **08c — Tareas.**
  1. Regenera solo las tareas afectadas, con IDs nuevos (por ejemplo, `T-20`). Las tareas no afectadas no se tocan.
  2. Parada y commit.
- **08d, 08e… — Implementación.** Un commit por cada tarea regenerada, con el mismo ciclo del Paso 06.
- **Cierre del cambio.**
  1. Completa `cambio-requisito-inventario.md` con:
     - las secciones del spec que cambiaron,
     - las tareas regeneradas, con su correspondencia antigua → nueva,
     - los commits de cada capa.
  2. Actualiza la tabla de trazabilidad.
  3. Parada y commit.

### Paso 09 — Cierre de la memoria y PR

1. **Actualiza la memoria:**
   - **`memory-bank/estado-actual.md`:** el estado final.
   - **`memory-bank/stack-tecnologico.md`:** el módulo nuevo, los comandos de la semilla y de los tests, y la base de datos.
   - **`memory-bank/contexto-producto.md`:** una sección breve sobre inventario que enlace al spec, sin copiarlo.
   - **`memory-bank/README.md`.**
2. **Comprueba el historial** con `git log --oneline main..HEAD`:
   - cada paso y cada tarea van en su propio commit,
   - todos los commits de implementación tienen `T-` e `INV-`,
   - los commits del cambio de requisito van en orden spec → plan → tareas → código.
3. **Comprueba las dependencias.** `git diff main -- pyproject.toml` no añade dependencias.
4. **Redacta `memory-bank/registro/descripcion-pr-inventario.md`** con estas secciones:
   1. Resumen.
   2. Spec, plan y tareas: enlaces y versiones finales.
   3. Trazabilidad requisito → test → commit, enlazando el registro.
   4. Cambio de requisito: qué secciones del spec cambiaron y qué tareas se regeneraron.
   5. Cómo verificar: comandos de los tests, de la semilla y del servidor.
   6. Reglas que evitaron desviaciones.
5. **Haz la parada.** Con mi OK:
   - commitea,
   - `git push -u origin feature/inventory-manager`,
   - `gh pr create --base main --head feature/inventory-manager --title "<título>" --body-file memory-bank/registro/descripcion-pr-inventario.md`.

   Si `gh` falla, dame el texto y abro yo el PR.
6. **No hagas merge.** Lo hago yo cuando se apruebe el PR.

---

## 7. Plantillas

### 7.1 `spec.md`

```markdown
# Spec — Gestor de inventario

- **Versión:** 1.0 · **Estado:** borrador | aprobado · **Fecha:** AAAA-MM-DD
- **Fuente de dominio:** `company-BRIEFING.md`

## 1. Propósito y alcance
<2–4 líneas: qué resuelve y para quién (Felipe Guerrero, Lucía Fernández, encargados de local)>
**Fuera de alcance:** …

## 2. Glosario y correspondencia de nombres
| Concepto (briefing) | Nombre en código | Origen (§ del briefing) |
|---|---|---|

## 3. Catálogos
| Catálogo | Valores | Origen: literal / derivado / pendiente |
|---|---|---|

## 4. Contratos
### 4.N <Operación>
- **Entradas:** …
- **Validaciones:** …
- **Resultado:** …
- **Errores:** <caso → respuesta>

## 5. Invariantes
- <enunciado> → criterios `INV-0xx`

## 6. Criterios de aceptación (EARS)
| ID | Tipo | Criterio |
|---|---|---|
| INV-001 | Ubicuo | El sistema debe … |
| INV-0xx | Evento | Cuando …, el sistema debe … |
| INV-0xx | Estado | Mientras …, el sistema debe … |
| INV-0xx | No deseado | Si …, entonces el sistema debe … |
| INV-0xx | Opcional | Donde …, el sistema debe … |

## 7. Decisiones de dominio
| # | Decisión | Origen: literal (§ del briefing) / validada AAAA-MM-DD / pendiente |
|---|---|---|

## 8. Historial de cambios
| Versión | Fecha | Secciones / INV cambiados | Motivo |
|---|---|---|---|
```

Cada criterio es **una sola frase**, comprobable con un test y sin palabras vagas como "rápido", "adecuado", "correctamente" o "etc.".

### 7.2 `plan.md`

```markdown
# Plan — Gestor de inventario

- **Versión:** 1.0 · **Implementa:** spec vX.Y · **Fecha:** AAAA-MM-DD

## 1. Decisiones
| ID | Decisión | Por qué (evidencia del repo o razonamiento) | Criterios |
|---|---|---|---|
| D-01 | … | … | INV-0xx |

## 2. Modelo de datos
## 3. Cálculo del stock disponible
## 4. Dónde vive cada cosa
## 5. API HTTP
## 6. Backoffice
## 7. Datos semilla
## 8. Estrategia de pruebas
## 9. Historial de cambios
| Versión | Fecha | Decisiones cambiadas | Motivo |
|---|---|---|---|
```

### 7.3 `tasks.md`

```markdown
# Tareas — Gestor de inventario

- **Versión:** 1.0 · **Deriva de:** spec vX.Y y plan vX.Y

| ID | Tarea | Criterios | Depende de | Verificación (tests) | Estado | Commit |
|---|---|---|---|---|---|---|
| T-01 | … | INV-0xx | — | `testInv0xx…` | pendiente | — |

**Estados:** pendiente · hecha · sustituida por T-xx

## Historial de cambios
| Versión | Fecha | Tareas regeneradas | Motivo |
|---|---|---|---|
```
