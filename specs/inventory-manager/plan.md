# Plan — Gestor de inventario

- **Versión:** 1.0 · **Implementa:** spec v1.0 · **Fecha:** 2026-10-28

Este plan decide el cómo. Los criterios se citan por ID y no se repiten; su texto está en [spec.md](./spec.md). Los IDs de decisión de este plan llevan el prefijo `PD-` para no confundirse con las decisiones `D-xx` del spec.

## 1. Decisiones
| ID | Decisión | Por qué (evidencia del repo o razonamiento) | Criterios |
|---|---|---|---|
| PD-01 | El inventario comparte el servidor, el proceso y el archivo SQLite del gestor de incidencias (`data/incidents.sqlite`). Sus tablas se crean en `initializeDatabase`, sin claves foráneas hacia las tablas de incidencias | `IncidentHTTPServer` abre una sola base y llama a `initializeDatabase` al arrancar (`services/api/server.py`, `database.py`). Un segundo archivo obligaría a un segundo `databasePath` y a un segundo ciclo de arranque sin ganar aislamiento: los dominios no se referencian entre sí | INV-001, INV-036 |
| PD-02 | Las cantidades se guardan como enteros en milésimas (`quantityMilli`, `reorderPointMilli`) para todas las unidades. La precisión por unidad (3 decimales en `kg` y `l`, enteros en `g`, `ml` y `unit`) se valida en la aplicación. La API recibe y devuelve las cantidades como cadenas decimales (`"12.500"`), y rechaza números JSON | Evita la coma flotante (`Decimal` en Python, `INTEGER` en SQLite). Un número JSON se lee como `float` en `json.loads` y en JavaScript, así que solo se acepta texto. SQLite no puede validar la unidad desde un `CHECK` de otra tabla | INV-003, INV-017, INV-018, INV-020, INV-036 |
| PD-03 | Tres tablas: `inventoryItems`, `inventoryLots` y `stockMovements`. Ninguna tiene columna de stock, ni de artículo ni de lote | El stock es un valor derivado. Sin columna no existe nada que escribir, y las operaciones expuestas son solo alta, edición y baja de artículos y alta de movimientos | INV-036, INV-037, INV-038 |
| PD-04 | `stockMovements` es de solo añadir: triggers `BEFORE UPDATE` y `BEFORE DELETE` que abortan, igual que `historyEvents`. `inventoryLots` también es inmutable por triggers: la `expiryDate` de un lote no cambia nunca | Precedente exacto en `database.py` (`historyEvents_preventUpdate` y `historyEvents_preventDelete`). La API además no ofrece rutas que modifiquen movimientos | INV-011, INV-030, INV-031, INV-039 |
| PD-05 | Una única función `calculateStock` calcula el stock. La usan el listado, la consulta, el informe, la señal de reorden, la comprobación de stock al registrar un movimiento y la marca de reorden. Ninguna otra consulta suma cantidades | Un solo punto evita que dos pantallas muestren cifras distintas. El criterio del signo (`inbound` +, `outbound` −, `adjustment` con su signo) vive en un único fragmento SQL | INV-035, INV-036, INV-040, INV-041, INV-042, INV-043, INV-045, INV-049 |
| PD-06 | Registrar un movimiento abre `BEGIN IMMEDIATE`, comprueba el stock con `calculateStock`, inserta el movimiento y confirma, todo en la misma transacción. Un trigger `BEFORE INSERT` de `stockMovements` aborta si el movimiento dejaría el stock del artículo o del lote por debajo de cero | `BEGIN IMMEDIATE` toma el bloqueo de escritura antes de leer, de modo que dos escritores no pueden leer el mismo stock y escribir después: `busy_timeout = 5000` ya está configurado en `createConnection`. El trigger protege el invariante aunque otro código inserte movimientos sin pasar por el caso de uso | INV-023, INV-024, INV-025, INV-034 |
| PD-07 | Un lote tiene `lotCode` único en todo el sistema y pertenece a un artículo. `stockMovements` referencia el lote con una clave foránea compuesta `(itemId, lotCode)` hacia `inventoryLots(itemId, lotCode)` | La unicidad global y la clave compuesta hacen que el lote de otro artículo no se pueda referenciar ni desde SQL (P-02). Con `lotCode` nulo la clave compuesta no se evalúa, que es el caso de los artículos sin control de lote | INV-026, INV-027, INV-028, INV-032, INV-033 |
| PD-08 | La baja y la edición de campos estructurales se protegen en dos niveles: el caso de uso comprueba si hay movimientos dentro de su transacción, y la base lo impide (clave foránea sin `ON DELETE` y trigger `BEFORE UPDATE OF locationId, category, unitOfMeasure` que aborta si el artículo tiene movimientos) | Mismo criterio que PD-04: la regla vive en el caso de uso, que devuelve el rechazo correcto, y en SQLite, que no deja pasar un código futuro que la olvide | INV-005, INV-006, INV-007, INV-008 |
| PD-09 | Los tres rechazos del spec §4 se mapean a excepciones y a códigos HTTP: datos inválidos → `ValueError` → 400; recurso inexistente → `LookupError` → 404; regla de negocio → `BusinessRuleError` (clase nueva en `inventory.py`) → 409 | `server.py` ya traduce `ValueError` a 400 y `LookupError` a 404 en `_handleRequest`. Solo falta distinguir la regla de negocio, para que el backoffice muestre su motivo; el servidor añade una cláusula `except BusinessRuleError` con 409 | INV-002, INV-006, INV-009, INV-015, INV-016, INV-023, INV-031, INV-050 |
| PD-10 | Las fechas de caducidad se guardan como texto ISO `AAAA-MM-DD` y se validan con `date.fromisoformat`. Un lote está caducado si `expiryDate` es anterior a `utcNow().date()`. Cada caso de uso recibe un parámetro opcional `now` para fijar el instante en las pruebas | `models.py` ya concentra `utcNow`, `formatUtcTimestamp` y `parseUtcTimestamp`. La comparación entre textos ISO coincide con la cronológica. El parámetro `now` evita pruebas que dependan del reloj real | INV-028, INV-029, INV-048, INV-050, INV-055, INV-065 |
| PD-11 | Los casos de uso usan una función auxiliar de transacción que abre `BEGIN IMMEDIATE` si la conexión no tiene una abierta, y se une a la existente si la tiene | Permite que la semilla ejecute todos los casos de uso dentro de una sola transacción y sea atómica sin duplicar validaciones | INV-059, INV-060, INV-066 |
| PD-12 | Código en `services/api/`: `inventory.py` (casos de uso y `calculateStock`), `inventoryseed.py` (semilla), catálogos y modelos en los módulos existentes. Rutas en `server.py`, bajo `/api/inventory/`. Vista en `uis/backoffice/`. Sin carpetas de primer nivel nuevas | Regla `01`: el componente va en su carpeta responsable (`services/`, `uis/`). Regla `03`: nada se comparte entre paquetes, así que no se toca `packages/` ni `shared/`. Los módulos existentes llevan nombre de una palabra en minúsculas (`catalogs.py`, `incidents.py`), y se mantiene | INV-056 |
| PD-13 | Los catálogos del inventario van en `catalogs.py` en un diccionario aparte, `inventoryCatalogs`, y `catalogIds` busca en los dos diccionarios. `GET /api/catalogs` no cambia | `catalogs` se sirve entero en `/api/catalogs` y lo consumen el backoffice y los tests de incidencias; mezclar las claves cambiaría ese contrato | INV-002, INV-015, INV-022 |
| PD-14 | Los datos semilla viven en `inventoryseed.py` y se cargan con `python -m services.api.inventoryseed`. No se expone ninguna ruta HTTP de semilla | El spec §4.8 no pide una ruta. Una ruta de escritura masiva sin autenticación ampliaría la superficie sin necesidad. El arranque del servidor no carga semilla | INV-059, INV-066 |
| PD-15 | El backoffice añade una página, `uis/backoffice/inventory.html`, con su script `inventory.js`, y reutiliza `styles.css`. `index.html` e `inventory.html` se enlazan entre sí. HTML, CSS y JavaScript sin framework | Es el precedente de `index.html` y `app.js`. El servidor ya sirve cualquier archivo de `uis/backoffice/` (`_serveStaticFile`), así que no hace falta cambiar el servidor | INV-054, INV-056, INV-057, INV-058 |
| PD-16 | Las pruebas usan `unittest` y bases en memoria; la prueba de concurrencia usa un archivo temporal con hilos y una conexión por hilo. El backoffice no tiene pruebas automáticas de JavaScript: se comprueba con una prueba HTTP del contenido servido y con el recorrido manual del Paso 07 | `services/api/tests/` usa `unittest` y el repo no tiene ejecutor de JavaScript ni se pueden añadir dependencias (principio 3 de `AGENTS.md`) | INV-025, INV-037, INV-054, INV-056, INV-057, INV-058 |

## 2. Modelo de datos
Se añaden a `initializeDatabase` con `CREATE ... IF NOT EXISTS`, como las tablas actuales. Los catálogos se aplican con `_catalogCheck`. Los `id` son UUID v4 con el mismo `CHECK` que `incidents.id`.

| Tabla | Columnas | Restricciones |
|---|---|---|
| `inventoryItems` | `id`, `name`, `locationId`, `category`, `unitOfMeasure`, `reorderPointMilli`, `createdAt` | `name` no vacío tras `trim`; `locationId`, `category` y `unitOfMeasure` con `CHECK` de catálogo; `reorderPointMilli >= 0` |
| `inventoryLots` | `lotCode` (clave primaria), `itemId`, `expiryDate`, `receivedAt` | `itemId` referencia `inventoryItems(id)`; `UNIQUE (itemId, lotCode)` para la clave compuesta; `lotCode` no vacío; `expiryDate` con forma `????-??-??`; triggers de inmutabilidad (PD-04) |
| `stockMovements` | `id`, `itemId`, `lotCode`, `movementType`, `quantityMilli`, `reason`, `createdAt` | `itemId` referencia `inventoryItems(id)` sin `ON DELETE`; `(itemId, lotCode)` referencia `inventoryLots(itemId, lotCode)`; `movementType` con `CHECK` de catálogo; `CHECK` de signo y motivo (abajo); triggers PD-04 y PD-06 |

`CHECK` de signo y motivo en `stockMovements`: en `inbound` y `outbound`, `quantityMilli > 0` y `length(trim(reason)) > 0`; en `adjustment`, `quantityMilli <> 0`, `reason` en el catálogo de motivos y `quantityMilli < 0` si el motivo es `waste` o `theft`. Cubre INV-017, INV-018, INV-019, INV-021 y INV-022 también desde SQL.

La cantidad se guarda con el signo que escribe el solicitante: positiva en `outbound`. El signo con el que cuenta en el stock lo decide `calculateStock` (§3).

Índices: `stockMovements (itemId, createdAt)` y `stockMovements (itemId, lotCode)`.

Modelos en `models.py` (dataclasses congeladas, como `Incident`): `InventoryItem`, `InventoryLot` y `StockMovement`. Los catálogos de `inventoryCatalogs` son: `units`, `categories`, `movementTypes`, `adjustmentReasons` y `locations`; esta última lleva el país y el estado en la etiqueta (D-08 del spec).

## 3. Cálculo del stock disponible
- **Función:** `calculateStock(connection, *, itemId=None, locationId=None, groupByLot=False)` en `inventory.py`. Devuelve un diccionario de milésimas: clave `itemId`, o `(itemId, lotCode)` si `groupByLot` es verdadero. Un artículo sin movimientos devuelve 0, no falta (INV-001, INV-041).
- **SQL:** una sola expresión `SUM(CASE movementType WHEN 'outbound' THEN -quantityMilli ELSE quantityMilli END)` agrupada por artículo, o por artículo y lote. Filtra por `itemId` o por `locationId` (unión con `inventoryItems`), de modo que el mismo ingrediente en dos locales suma por separado (INV-040).
- **Quién la llama:** `registerMovement` (comprobación previa, PD-06), `listItems`, `getItem`, `getStockReport` y `getReorderSignal`. Los totales de `inbound`, `outbound` y ajustes por motivo del informe son agregaciones por tipo; no calculan stock y viven en una consulta aparte dentro de `getStockReport`.
- **Marca de reorden:** `needsReorder = stock <= reorderPointMilli`, calculada en `inventory.py` a partir del resultado de `calculateStock` (INV-041, INV-042, INV-043). El stock caducado cuenta (INV-049).
- **Caducados:** `getItem`, `listItems` y `getStockReport` completan el resultado con los lotes cuya `expiryDate` sea anterior a hoy en UTC y cuyo stock por lote sea mayor que cero (INV-048, INV-053). El texto «X disponibles, de ellos Y caducados» se compone en el backoffice (PD-15).
- **Formato:** `formatQuantity(milli, unitOfMeasure)` convierte a cadena decimal con la precisión de la unidad (`"12.500"` en `kg` y `l`; `"12"` en `g`, `ml` y `unit`). `parseQuantity(text, unitOfMeasure)` hace la conversión inversa y rechaza decimales de más, notación científica y números JSON (INV-020).

## 4. Dónde vive cada cosa
| Pieza | Ubicación | Qué contiene |
|---|---|---|
| Catálogos | `services/api/catalogs.py` | `inventoryCatalogs`; `catalogIds` ampliado (PD-13) |
| Modelos | `services/api/models.py` | `InventoryItem`, `InventoryLot`, `StockMovement` |
| Esquema | `services/api/database.py` | Tablas, índices y triggers del §2 en `initializeDatabase` |
| Casos de uso | `services/api/inventory.py` | `BusinessRuleError`, `calculateStock`, `parseQuantity`, `formatQuantity`, `createItem`, `updateItem`, `deleteItem`, `listItems`, `getItem`, `registerMovement`, `getStockReport`, `getReorderSignal` |
| Semilla | `services/api/inventoryseed.py` | Los 16 artículos, sus movimientos y `loadInventorySeed` |
| Rutas HTTP | `services/api/server.py` | Método `_dispatchInventoryAPI` para las rutas `/api/inventory/`; cláusula 409; `do_DELETE` deja de rechazar todo y delega |
| Backoffice | `uis/backoffice/inventory.html`, `inventory.js` | Vista de inventario (§6) |
| Pruebas | `services/api/tests/test_inventory.py`, `test_inventoryseed.py`, `test_inventoryapi.py` | §8 |
| Guías | `services/api/README.md` y `README.es.md`; `uis/backoffice/README.md` y `README.es.md` | Los módulos y la página nuevos, con el comando de la semilla. Ambos idiomas equivalentes (regla `02`) |

Los casos de uso reciben la conexión y los campos como un diccionario (`createItem(connection, fields, now=None)`). Cada función comprueba que las claves del diccionario sean exactamente las permitidas, así que un campo de stock se rechaza por datos inválidos en cualquier llamada, no solo por la capa HTTP (INV-038).

Orden de validación en `registerMovement`: datos inválidos (tipo, cantidad, signo, precisión, motivo, `expiryDate`), después recurso inexistente (artículo, lote) y después reglas de negocio (lote obligatorio, lote ajeno, `expiryDate` distinta, caducado, stock). Así cada entrada tiene un único rechazo posible.

## 5. API HTTP
Bajo `/api/inventory/`, JSON, mismas cabeceras y límites que las rutas de incidencias (`_readJsonObject`, `_requirePayloadFields`). Los identificadores de artículo se validan con el patrón UUID v4 de `incidentIdPattern`; si no cuadra, 404.

| Método y ruta | Operación del spec | Éxito | Cuerpo de la petición |
|---|---|---|---|
| `GET /api/inventory/catalogs` | — | 200 | — |
| `GET /api/inventory/items?locationId=` | §4.4 | 200 | — |
| `POST /api/inventory/items` | §4.1 | 201 | `name`, `locationId`, `category`, `unitOfMeasure`, `reorderPoint` |
| `GET /api/inventory/items/{id}` | §4.4 | 200 | — |
| `PATCH /api/inventory/items/{id}` | §4.2 | 200 | Cualquiera de los cinco campos anteriores |
| `DELETE /api/inventory/items/{id}` | §4.3 | 200, `{"deleted": id}` | — |
| `POST /api/inventory/items/{id}/movements` | §4.5 | 201 | `movementType`, `quantity`, `reason`, y opcionales `lotCode`, `expiryDate` |
| `GET /api/inventory/items/{id}/report` | §4.6 | 200 | — |
| `GET /api/inventory/locations/{locationId}/reorder` | §4.7 | 200 | — |

Rechazos: 400 datos inválidos, 404 recurso inexistente, 409 regla de negocio (PD-09). Los cuerpos de error mantienen la forma `{"error": "..."}` de las rutas actuales. No hay ruta para modificar o eliminar un movimiento ni campo de stock en ninguna petición (INV-037, INV-039).

Formas de respuesta (cantidades siempre como cadenas, PD-02):
- **Artículo:** `id`, `name`, `locationId`, `category`, `unitOfMeasure`, `reorderPoint`, `stock`, `needsReorder`, `expiredLots` (lista de `lotCode`, `expiryDate`, `stock`), `createdAt`.
- **Movimiento:** `id`, `itemId`, `movementType`, `quantity`, `reason`, `lotCode`, `createdAt`, y `stock` con el stock del artículo tras registrarlo.
- **Informe:** `itemId`, `unitOfMeasure`, `stock`, `reorderPoint`, `needsReorder`, `totalInbound`, `totalOutbound`, `adjustments` (lista de `reason` y `total` para `waste`, `theft` y `count_correction`, siempre las tres), `lots` (lista de `lotCode`, `expiryDate`, `expired`, `stock`, `expiredStock`).
- **Señal de reorden:** lista de `itemId`, `name`, `unitOfMeasure`, `stock`, `reorderPoint`.

## 6. Backoffice
- **Página:** `inventory.html` con `inventory.js`; enlace a `index.html` y viceversa (PD-15).
- **Inventario por local:** selector de local, tabla con artículo, categoría, unidad, stock, punto de reorden y marca de reorden, y acciones de editar y dar de baja. Formulario de alta de artículo (INV-056).
- **Movimientos:** formulario con los tres tipos, cantidad, motivo (lista cerrada en `adjustment`, texto libre en los otros dos), lote y, solo en una entrada con lote nuevo, `expiryDate`. No existe ningún campo de stock. El mensaje del servidor se muestra tal cual si hay rechazo (INV-057).
- **Informe y reorden:** el panel de un artículo muestra los valores del informe, con `waste` y `theft` en dos líneas; el panel de reorden lista la señal del local (INV-058).
- **Caducados:** el stock se muestra como «X disponibles, de ellos Y caducados (lote …)» cuando `expiredLots` no está vacío; si no, solo la cifra de stock (INV-054).
- **Seguridad de la vista:** el texto de la API se inserta con `textContent`, como `app.js`, nunca con `innerHTML`.

## 7. Datos semilla
- **Dónde y cómo:** `inventoryseed.py` define los 16 artículos del §4.3 del encargo como constantes y `loadInventorySeed(connection, now=None)`. Se ejecuta con `python -m services.api.inventoryseed`, sobre `data/incidents.sqlite` por defecto, la misma ruta que usa `server.main`.
- **Cómo se carga:** una sola transacción (PD-11). Primero comprueba que `inventoryItems` está vacía; si no, lanza `BusinessRuleError` y no cambia nada (INV-066). Después llama a `createItem` y `registerMovement`, de modo que todo el stock nace de movimientos validados (INV-059, INV-060). Si falla cualquier llamada, no queda nada cargado.
- **Esquema de movimientos** por artículo, con `rp` como su punto de reorden, para cumplir INV-061 a INV-063:
  - Artículo normal: `inbound` de 4·rp, `outbound` de 1·rp y un `adjustment` de ±0,5·rp. Stock final entre 2,5·rp y 3,5·rp, mayor que `rp`.
  - *Salsa de ajo de la casa* y *Envases para llevar*: `inbound` de 2·rp, `outbound` de 1·rp y `adjustment` `waste` de −0,2·rp. Stock final 0,8·rp, menor o igual que `rp`.
  - Motivos: se reparten por orden de artículo (`waste`, `theft`, `count_correction`, y vuelta a empezar), `waste` y `theft` con cantidad negativa y `count_correction` con cantidad positiva. Aparecen los tres (INV-062).
  - Todas las cantidades se expresan con la precisión de la unidad: en `unit` salen enteros porque su `rp` es par.
- **Lotes** (artículos `meat` y `produce`; `lotCode` determinista, derivado del local y del artículo):
  - Cada lote nuevo lo abre su `inbound`, con una `expiryDate` calculada como el día UTC de la carga más 30 días, así que siempre es posterior al día de la carga (INV-065).
  - *Cilantro* (queChille) abre un primer lote con `expiryDate` fija `2026-10-01` (INV-055) con un `inbound` de 4·rp y un `adjustment` `waste` de −0,5·rp sobre ese lote (INV-052), de modo que conserva 3,5·rp (INV-064). Un segundo lote, con la fecha relativa, recibe un `inbound` de 2·rp y el `outbound` de 1·rp. El `outbound` no usa el lote caducado (INV-050).
- **Cantidades concretas:** las calcula `inventoryseed.py` con el esquema anterior; la tarea de la semilla las fija y su prueba comprueba INV-061 a INV-065 sobre el resultado.

## 8. Estrategia de pruebas
- **Herramienta y comando:** `unittest`, con el comando del §3 del encargo. Sin dependencias nuevas.
- **Nombre de cada test:** `testInvNNN<Comportamiento>`, con el ID del criterio en camelCase (por ejemplo, `testInv023RejectsOutboundBelowZero`). Cada criterio de INV-001 a INV-066 tiene al menos un test, salvo los de interfaz (abajo).
- **Casos de uso** (`test_inventory.py`): base `:memory:` con `initializeDatabase` y `now` fijo. Cubre artículos (INV-001 a INV-010), movimientos (INV-011 a INV-024), lotes (INV-026 a INV-035, INV-055), invariantes de stock (INV-036 a INV-040), reorden (INV-041 a INV-044), informe y caducados (INV-045 a INV-053). Una prueba directa sobre SQL comprueba que los triggers y las claves foráneas rechazan los movimientos que el caso de uso ya prohíbe (PD-04, PD-06, PD-07, PD-08).
- **Concurrencia (INV-025):** archivo temporal, dos o más hilos, cada uno con su conexión, que registran a la vez salidas que juntas dejarían el stock en negativo. Se comprueba que solo se registran las que caben y que el stock final no es negativo.
- **Semilla** (`test_inventoryseed.py`): INV-059 a INV-066 con el resultado de `loadInventorySeed` y un `now` fijo; también que una segunda carga se rechaza y no cambia los recuentos.
- **API** (`test_inventoryapi.py`): servidor real en un puerto efímero, como `test_server.py`: rutas, códigos 400/404/409/415 y la forma de las respuestas, incluida la ausencia de cualquier ruta para modificar un movimiento o el stock (INV-037, INV-039).
- **Backoffice (INV-054, INV-056, INV-057, INV-058):** `test_inventoryapi.py` comprueba que el servidor entrega `inventory.html` y `inventory.js`, que el formulario de movimientos no contiene ningún campo de stock y que los datos que la vista necesita (`expiredLots`, `adjustments`) llegan de la API. El comportamiento visual se verifica en el recorrido manual del Paso 07 y queda en `memory-bank/registro/verificacion-inventario.md`.
- **Regresión:** las 35 pruebas existentes de incidencias se ejecutan en cada tarea y deben seguir pasando.

## 9. Historial de cambios
| Versión | Fecha | Decisiones cambiadas | Motivo |
|---|---|---|---|
| 1.0 | 2026-10-28 | PD-01–PD-16 | Versión inicial del Paso 04, aprobada por el usuario |
