# Spec — Gestor de inventario

- **Versión:** 1.0 · **Estado:** aprobado · **Fecha:** 2026-10-28
- **Fuente de dominio:** `CONTEXT.md` (hace de `company-BRIEFING.md`, decisión del usuario del 2026-10-28) y las decisiones del §7, tomadas del encargo en `memory-bank/encargo.md` §4.

> **Aviso de fuente.** `CONTEXT.md` es el briefing de Brasaland y no define entidades, campos ni catálogos de inventario. Todo el dominio de este spec procede de `memory-bank/encargo.md` §4. Lo que ese texto atribuye al briefing (`literal`) no se puede contrastar con `CONTEXT.md`. Lo que ni el encargo ni `CONTEXT.md` fijan queda como `pendiente` en el §7.

## 1. Propósito y alcance
Permite a operaciones (Felipe Guerrero), a compras (Lucía Fernández) y a los encargados de local dar de alta artículos de inventario, registrar sus movimientos de entrada, salida y ajuste, y saber qué artículos de un local están en su punto de reorden o por debajo.
El stock disponible nunca se escribe: se calcula siempre a partir de los movimientos.

**Fuera de alcance:** costes y valoración del inventario, proveedores y pedidos de compra, transferencias entre locales, autenticación y permisos, historial de ediciones de artículos, importación masiva y los locales distintos de los cuatro del §3.

## 2. Glosario y correspondencia de nombres
| Concepto | Nombre en código | Origen |
|---|---|---|
| Local | `locationId` | encargo §4.2.1 |
| Artículo de inventario | artículo (`name`) | encargo §4.2.1 |
| Categoría | `category` | encargo §4.1 |
| Unidad de medida | `unitOfMeasure` | encargo §4.1 |
| Punto de reorden (`reorder_point` en el briefing) | `reorderPoint` | encargo §4.1 y §4.2.1 |
| Lote | lote (`lotCode`) | encargo §4.2.1 |
| Fecha de caducidad del lote | `expiryDate` | encargo §4.2.1 |
| Fecha de recepción del lote | `receivedAt` | encargo §4.2.1 |
| Movimiento | movimiento | encargo §4.1 |
| Tipo de movimiento | `movementType` | encargo §4.2.1 |
| Cantidad de un movimiento | `quantity` | validado (P-01) |
| Motivo de un movimiento | `reason` | validado (P-01) |
| Marca temporal de creación | `createdAt` | encargo §4.2.1 |
| Stock disponible | valor calculado, sin campo propio | encargo §1 |
| Artículo con control de lote | artículo de categoría `meat` o `produce` | encargo §4.2.5 |
| Lote caducado | lote con `expiryDate` anterior a la fecha actual en UTC | encargo §4.2.6 |

## 3. Catálogos
| Catálogo | Valores | Origen |
|---|---|---|
| Unidades (`unitOfMeasure`) | `kg`, `g`, `l`, `ml`, `unit` | literal |
| Categorías (`category`) | `meat`, `produce`, `sauces_condiments`, `beverages`, `packaging`, `cleaning_supplies` | literal |
| Tipos de movimiento (`movementType`) | `inbound`, `outbound`, `adjustment` | literal |
| Motivos de ajuste (`reason` de un `adjustment`) | `waste`, `theft`, `count_correction` | validada 2026-10-28 |
| Locales (`locationId`) | `laArepita` (La Arepita, Colombia), `queChille` (QueChille, Colombia), `theBigSauce` (The BigSauce, Estados Unidos, Florida), `chilliBeans` (ChilliBeans, Estados Unidos, Florida) | validada 2026-10-28 |
| Precisión de cantidad | `kg` y `l`: hasta 3 decimales; `g`, `ml` y `unit`: enteros | validada 2026-10-28 |

Los valores de catálogo se usan tal como están escritos aquí. Los nombres de campo van en camelCase.

## 4. Contratos
**Tipos de rechazo.** Toda operación que no se cumple termina en uno de tres rechazos y no cambia ningún dato: *datos inválidos* (el contenido de la petición no cumple el contrato), *recurso inexistente* (el artículo, el lote o el local no existe) y *regla de negocio* (los datos son válidos, pero la operación incumple una regla de stock, de lote, de caducidad o de estado).

### 4.1 Alta de artículo
- **Entradas:** `name`, `locationId`, `category`, `unitOfMeasure`, `reorderPoint`.
- **Validaciones:** `name` no vacío; `locationId`, `category` y `unitOfMeasure` pertenecen a su catálogo; `reorderPoint` no negativo y con la precisión de su unidad.
- **Resultado:** el artículo existe, con identificador único asignado por el sistema y stock 0.
- **Errores:** campo inválido → datos inválidos; cualquier campo de stock en la petición → datos inválidos.

### 4.2 Edición de artículo
- **Entradas:** artículo y cualquiera de `name`, `reorderPoint`, `locationId`, `category`, `unitOfMeasure`.
- **Validaciones:** las del alta; `locationId`, `category` y `unitOfMeasure` solo cambian si el artículo no tiene movimientos.
- **Resultado:** el artículo guarda los valores nuevos.
- **Errores:** artículo inexistente → recurso inexistente; cambio de `locationId`, `category` o `unitOfMeasure` con movimientos → regla de negocio; cualquier campo de stock → datos inválidos.

### 4.3 Baja de artículo
- **Entradas:** artículo.
- **Resultado:** el artículo deja de existir. No hay campo de activo/inactivo.
- **Errores:** artículo inexistente → recurso inexistente; artículo con movimientos → regla de negocio.

### 4.4 Listado y consulta de artículos
- **Entradas:** filtro opcional por `locationId`.
- **Resultado:** cada artículo con sus campos, su stock disponible y la marca de reorden.
- **Errores:** local inexistente → recurso inexistente; artículo inexistente en una consulta individual → recurso inexistente.

### 4.5 Registro de movimiento
- **Entradas:** artículo, `movementType`, `quantity`, `reason`, y el lote (`lotCode`) cuando corresponde; al abrir un lote nuevo con una entrada, también su `expiryDate`.
- **Validaciones:**
  - `movementType` del catálogo.
  - `quantity` con la precisión de la unidad del artículo; positiva en `inbound` y `outbound`; con signo y distinta de cero en `adjustment`.
  - `reason` obligatorio: texto no vacío en `inbound` y `outbound`; valor del catálogo de motivos en `adjustment`. `waste` y `theft` solo con cantidad negativa.
  - Lote obligatorio en artículos con control de lote; opcional en el resto, pero si se indica debe existir, salvo en una entrada que lo abre.
  - Un lote pertenece a un único artículo.
  - El movimiento no deja el stock del artículo ni el del lote por debajo de cero.
  - Un lote caducado no admite salidas ni ajustes que no sean `waste`.
- **Resultado:** el movimiento queda registrado con `createdAt` en UTC asignado por el sistema y no se puede modificar ni eliminar. El stock se obtiene de los movimientos.
- **Errores:** artículo, lote o local inexistente → recurso inexistente; formato, signo, precisión, motivo o tipo inválidos → datos inválidos; falta de lote, lote de otro artículo, stock o lote negativo, lote caducado, `expiryDate` distinta en un lote existente → regla de negocio.

### 4.6 Informe de stock de un artículo
- **Entradas:** artículo.
- **Resultado:** stock disponible; total de `inbound`; total de `outbound`; total de ajustes por cada motivo (`waste`, `theft`, `count_correction`); stock por lote con su `expiryDate` y su estado de caducado; stock caducado por lote.
- **Errores:** artículo inexistente → recurso inexistente.

### 4.7 Señal de reorden por local
- **Entradas:** `locationId`.
- **Resultado:** los artículos del local con stock disponible igual o menor que su `reorderPoint`. Un artículo sin movimientos tiene stock 0 y, por tanto, aparece.
- **Errores:** local inexistente → recurso inexistente.

### 4.8 Carga de datos semilla
- **Entradas:** ninguna.
- **Resultado:** los 16 artículos del §4.3 del encargo y sus movimientos, registrados con las mismas validaciones del §4.5.
- **Errores:** la base ya contiene artículos → regla de negocio y no se cambia nada.

## 5. Invariantes
- El stock disponible de un artículo se calcula a partir de sus movimientos → `INV-036`, `INV-040`, `INV-049`.
- Ninguna operación escribe el stock → `INV-037`, `INV-038`, `INV-039`.
- Ningún movimiento deja el stock de un artículo o de un lote por debajo de cero → `INV-023`, `INV-024`, `INV-025`, `INV-034`.
- Un lote pertenece a un único artículo → `INV-033`.
- El stock caducado cuenta como stock disponible y solo sale con un ajuste `waste` → `INV-049`, `INV-050`, `INV-051`, `INV-052`.

## 6. Criterios de aceptación (EARS)
### Artículos
| ID | Tipo | Criterio |
|---|---|---|
| INV-001 | Evento | Cuando se da de alta un artículo con `name`, `locationId`, `category`, `unitOfMeasure` y `reorderPoint` válidos, el sistema debe crearlo con identificador único y stock disponible 0. |
| INV-002 | No deseado | Si, al dar de alta o editar un artículo, `name` está vacío o `locationId`, `category` o `unitOfMeasure` no pertenecen a su catálogo, entonces el sistema debe rechazar la operación por datos inválidos y no cambiar el artículo. |
| INV-003 | No deseado | Si, al dar de alta o editar un artículo, `reorderPoint` es negativo o tiene más decimales de los que admite su unidad, entonces el sistema debe rechazar la operación por datos inválidos y no cambiar el artículo. |
| INV-004 | Evento | Cuando se edita `name` o `reorderPoint` de un artículo existente, el sistema debe guardar el valor nuevo aunque el artículo tenga movimientos. |
| INV-005 | Evento | Cuando se edita `locationId`, `category` o `unitOfMeasure` de un artículo sin movimientos, el sistema debe guardar el valor nuevo. |
| INV-006 | No deseado | Si se edita `locationId`, `category` o `unitOfMeasure` de un artículo con movimientos, entonces el sistema debe rechazar la edición por regla de negocio y conservar los valores anteriores. |
| INV-007 | Evento | Cuando se da de baja un artículo sin movimientos, el sistema debe eliminarlo. |
| INV-008 | No deseado | Si se da de baja un artículo con movimientos, entonces el sistema debe rechazar la baja por regla de negocio y conservar el artículo y sus movimientos. |
| INV-009 | No deseado | Si se consulta, edita, da de baja o se pide el informe de un artículo inexistente, entonces el sistema debe rechazar la operación por recurso inexistente. |
| INV-010 | Evento | Cuando se lista el inventario, el sistema debe devolver cada artículo con su stock disponible y su marca de reorden, y permitir filtrar por `locationId`. |

### Movimientos
| ID | Tipo | Criterio |
|---|---|---|
| INV-011 | Ubicuo | El sistema debe guardar en cada movimiento su artículo, `movementType`, `quantity`, `reason` y un `createdAt` en UTC que asigna el sistema y no el solicitante. |
| INV-012 | Evento | Cuando se registra un `inbound` válido, el sistema debe aumentar el stock disponible del artículo en su cantidad. |
| INV-013 | Evento | Cuando se registra un `outbound` válido con stock suficiente, el sistema debe disminuir el stock disponible del artículo en su cantidad. |
| INV-014 | Evento | Cuando se registra un `adjustment` válido, el sistema debe sumar su cantidad, con su signo, al stock disponible del artículo. |
| INV-015 | No deseado | Si el `movementType` de un movimiento no pertenece al catálogo, entonces el sistema debe rechazarlo por datos inválidos y no registrarlo. |
| INV-016 | No deseado | Si un movimiento referencia un artículo inexistente, entonces el sistema debe rechazarlo por recurso inexistente y no registrarlo. |
| INV-017 | No deseado | Si un `inbound` o un `outbound` tiene cantidad cero o negativa, entonces el sistema debe rechazarlo por datos inválidos y no registrarlo. |
| INV-018 | No deseado | Si un `adjustment` tiene cantidad cero, entonces el sistema debe rechazarlo por datos inválidos y no registrarlo. |
| INV-019 | No deseado | Si un `adjustment` con motivo `waste` o `theft` tiene cantidad positiva, entonces el sistema debe rechazarlo por datos inválidos y no registrarlo. |
| INV-020 | No deseado | Si la cantidad de un movimiento tiene más decimales de los que admite la unidad del artículo, entonces el sistema debe rechazarlo por datos inválidos y no registrarlo. |
| INV-021 | No deseado | Si un `inbound` o un `outbound` no tiene motivo o su motivo es solo espacios, entonces el sistema debe rechazarlo por datos inválidos y no registrarlo. |
| INV-022 | No deseado | Si un `adjustment` no tiene motivo o su motivo no pertenece al catálogo de motivos de ajuste, entonces el sistema debe rechazarlo por datos inválidos y no registrarlo. |
| INV-023 | No deseado | Si un `outbound` dejaría el stock disponible del artículo por debajo de cero, entonces el sistema debe rechazarlo por regla de negocio y no registrarlo. |
| INV-024 | No deseado | Si un `adjustment` dejaría el stock disponible del artículo por debajo de cero, entonces el sistema debe rechazarlo por regla de negocio y no registrarlo. |
| INV-025 | No deseado | Si se solicitan a la vez varios movimientos que reducen el stock de un mismo artículo y juntos lo dejarían por debajo de cero, entonces el sistema debe registrar solo los que mantienen el stock en cero o más y rechazar el resto. |

### Lotes
| ID | Tipo | Criterio |
|---|---|---|
| INV-026 | No deseado | Si un movimiento sobre un artículo de categoría `meat` o `produce` no indica lote, entonces el sistema debe rechazarlo por regla de negocio y no registrarlo. |
| INV-027 | Opcional | Donde el artículo no es de categoría `meat` ni `produce`, el sistema debe aceptar movimientos sin lote. |
| INV-028 | Evento | Cuando un `inbound` indica un `lotCode` que no existe y una `expiryDate` válida, el sistema debe crear el lote del artículo con `receivedAt` igual al instante UTC del registro y registrar el movimiento en ese lote. |
| INV-029 | No deseado | Si un `inbound` indica un `lotCode` que no existe y no indica una `expiryDate` válida, entonces el sistema debe rechazarlo por datos inválidos y no crear el lote. |
| INV-030 | Evento | Cuando un `inbound` indica un lote existente del mismo artículo, el sistema debe sumar la cantidad al stock de ese lote sin cambiar su `expiryDate`. |
| INV-031 | No deseado | Si un `inbound` indica un lote existente junto con una `expiryDate` distinta de la del lote, entonces el sistema debe rechazarlo por regla de negocio y no registrarlo. |
| INV-032 | No deseado | Si un `outbound` o un `adjustment` referencia un lote inexistente, entonces el sistema debe rechazarlo por recurso inexistente y no registrarlo. |
| INV-033 | No deseado | Si un movimiento referencia un lote que pertenece a otro artículo, entonces el sistema debe rechazarlo por regla de negocio y no registrarlo. |
| INV-034 | No deseado | Si un movimiento dejaría el stock de su lote por debajo de cero, entonces el sistema debe rechazarlo por regla de negocio y no registrarlo. |
| INV-035 | Ubicuo | El sistema debe calcular el stock de cada lote a partir de los movimientos de ese lote. |
| INV-055 | Evento | Cuando un `inbound` abre un lote con una `expiryDate` anterior a la fecha actual en UTC, el sistema debe crear el lote y registrar el movimiento. |

### Invariante de stock
| ID | Tipo | Criterio |
|---|---|---|
| INV-036 | Ubicuo | El sistema debe calcular el stock disponible de un artículo en su local como la suma de las cantidades de sus movimientos, con signo positivo en `inbound`, negativo en `outbound` y el propio signo en `adjustment`. |
| INV-037 | Ubicuo | El sistema no debe ofrecer ninguna operación, ni en la API ni en el backoffice, que modifique directamente el stock disponible de un artículo o de un lote. |
| INV-038 | No deseado | Si una petición de alta o de edición de artículo incluye un campo de stock, entonces el sistema debe rechazarla por datos inválidos y no cambiar el artículo. |
| INV-039 | Ubicuo | El sistema no debe ofrecer ninguna operación que modifique o elimine un movimiento ya registrado. |
| INV-040 | Ubicuo | El sistema debe calcular el stock de cada artículo solo con los movimientos de ese artículo, de modo que el mismo ingrediente en dos locales tenga dos stocks independientes. |

### Reorden
| ID | Tipo | Criterio |
|---|---|---|
| INV-041 | Evento | Cuando se consulta la señal de reorden de un local, el sistema debe devolver sus artículos con stock disponible igual o menor que su `reorderPoint`, con ese stock y ese `reorderPoint`. |
| INV-042 | No deseado | Si el stock disponible de un artículo es mayor que su `reorderPoint`, entonces el sistema no debe incluirlo en la señal de reorden. |
| INV-043 | Estado | Mientras el stock disponible de un artículo sea igual o menor que su `reorderPoint`, el sistema debe indicarlo en el listado de artículos y en su informe de stock. |
| INV-044 | No deseado | Si se consulta la señal de reorden de un local inexistente, entonces el sistema debe rechazar la consulta por recurso inexistente. |

### Informe de stock
| ID | Tipo | Criterio |
|---|---|---|
| INV-045 | Evento | Cuando se pide el informe de stock de un artículo, el sistema debe devolver su stock disponible, el total de sus `inbound` y el total de sus `outbound`. |
| INV-046 | Evento | Cuando se pide el informe de stock de un artículo, el sistema debe devolver el total de ajustes de `waste`, de `theft` y de `count_correction` como tres valores separados. |
| INV-047 | Evento | Cuando se pide el informe de stock de un artículo con lotes, el sistema debe devolver el stock de cada lote con su `expiryDate`. |

### Caducados
| ID | Tipo | Criterio |
|---|---|---|
| INV-048 | Ubicuo | El sistema debe considerar caducado un lote cuando su `expiryDate` es anterior a la fecha actual en UTC. |
| INV-049 | Ubicuo | El sistema debe incluir el stock de los lotes caducados en el stock disponible del artículo y en la señal de reorden. |
| INV-050 | No deseado | Si un `outbound` referencia un lote caducado, entonces el sistema debe rechazarlo por regla de negocio aunque el lote tenga stock suficiente. |
| INV-051 | No deseado | Si un `adjustment` con un motivo distinto de `waste` referencia un lote caducado, entonces el sistema debe rechazarlo por regla de negocio y no registrarlo. |
| INV-052 | Evento | Cuando se registra un `adjustment` con motivo `waste` y cantidad negativa válida sobre un lote caducado, el sistema debe registrarlo y reducir el stock del lote. |
| INV-053 | Evento | Cuando se pide el informe de stock de un artículo con lotes caducados, el sistema debe devolver por separado el stock caducado de cada lote. |
| INV-054 | Evento | Cuando el backoffice muestra el stock de un artículo con lotes caducados, debe mostrar el texto «X disponibles, de ellos Y caducados (lote …)», con el lote de cada stock caducado. |

### Backoffice
| ID | Tipo | Criterio |
|---|---|---|
| INV-056 | Evento | Cuando se abre la vista de inventario del backoffice, debe permitir dar de alta, editar y dar de baja artículos y listar los de cada local con su stock disponible y su marca de reorden. |
| INV-057 | Evento | Cuando se registra un movimiento desde el backoffice, el backoffice debe ofrecer los tres tipos de movimiento, no ofrecer ningún campo de stock y mostrar el motivo del rechazo si el sistema lo rechaza. |
| INV-058 | Evento | Cuando se abre el informe de un artículo o la señal de reorden de un local en el backoffice, debe mostrar los valores del informe y de la señal del §4.6 y del §4.7, con `waste` y `theft` por separado. |

### Datos semilla
| ID | Tipo | Criterio |
|---|---|---|
| INV-059 | Evento | Cuando se ejecuta la carga semilla sobre una base sin artículos, el sistema debe crear los 16 artículos del §4.3 del encargo con su local, categoría, unidad y `reorderPoint`. |
| INV-060 | Ubicuo | El sistema debe crear todo el stock semilla solo mediante movimientos `inbound`, `outbound` y `adjustment` registrados con las validaciones del §4.5. |
| INV-061 | Estado | Mientras la carga semilla esté completa, cada artículo semilla debe tener al menos un `inbound`, un `outbound` y un `adjustment`. |
| INV-062 | Estado | Mientras la carga semilla esté completa, los ajustes semilla deben incluir los motivos `waste`, `theft` y `count_correction`. |
| INV-063 | Estado | Mientras la carga semilla esté completa, *Salsa de ajo de la casa* (laArepita) y *Envases para llevar* (theBigSauce) deben tener stock igual o menor que su `reorderPoint` y los otros 14 artículos, mayor. |
| INV-064 | Estado | Mientras la carga semilla esté completa, *Cilantro* (queChille) debe tener un lote con `expiryDate` `2026-10-01` y stock mayor que cero. |
| INV-065 | Estado | Mientras la carga semilla esté completa, todos los lotes semilla distintos del de *Cilantro* (queChille) deben tener una `expiryDate` posterior a la fecha actual en UTC del día en que se ejecutó la carga. |
| INV-066 | No deseado | Si se ejecuta la carga semilla sobre una base que ya contiene artículos, entonces el sistema debe rechazarla por regla de negocio y no añadir ni cambiar ningún dato. |

## 7. Decisiones de dominio
Las filas `literal` están tomadas del §4.1 del encargo, que las atribuye al briefing; `CONTEXT.md` no las contiene y no se pueden contrastar.

| # | Decisión | Origen |
|---|---|---|
| D-01 | Catálogos de unidades, categorías y tipos de movimiento con los valores del §3 | literal (encargo §4.1) |
| D-02 | El stock se controla por local; el mismo ingrediente en dos locales son dos artículos distintos | literal (encargo §4.1) |
| D-03 | La señal de reorden salta cuando el stock es igual o menor que `reorderPoint`, definido por artículo | literal (encargo §4.1) |
| D-04 | Un `outbound` que dejaría el stock por debajo de cero se rechaza | literal (encargo §4.1) |
| D-05 | Un `outbound` o `adjustment` con artículo o lote inexistente se rechaza | literal (encargo §4.1) |
| D-06 | `waste` y `theft` se distinguen en cualquier informe de stock | literal (encargo §4.1) |
| D-07 | Los valores de catálogo se usan literalmente; los campos van en camelCase; los identificadores propios, en camelCase | validada 2026-10-28 |
| D-08 | Hay exactamente cuatro locales, los del §3 | validada 2026-10-28 |
| D-09 | Todo movimiento lleva motivo: catálogo cerrado en `adjustment`, texto libre no vacío en `inbound` y `outbound` | validada 2026-10-28 |
| D-10 | Signo de las cantidades: positivo en `inbound` y `outbound`; con signo y distinto de cero en `adjustment`; `waste` y `theft` negativos; ningún movimiento deja el stock por debajo de cero | validada 2026-10-28 |
| D-11 | Control de lote = categoría `meat` o `produce`; en el resto el lote es opcional y, si se indica, debe existir; un lote pertenece a su artículo; el stock se calcula también por lote y ningún lote queda en negativo | validada 2026-10-28 |
| D-12 | Lote caducado: `expiryDate` anterior a la fecha actual en UTC; el stock disponible y el reorden no cambian; las salidas se rechazan; solo un ajuste `waste` lo retira; el stock caducado se ve separado por lote | validada 2026-10-28 |
| D-13 | Solo se da de baja un artículo sin movimientos; no hay campo de activo/inactivo | validada 2026-10-28 |
| D-14 | `name` y `reorderPoint` se editan siempre; `locationId`, `category` y `unitOfMeasure`, solo sin movimientos; el stock nunca se edita | validada 2026-10-28 |
| D-15 | Cantidades: hasta 3 decimales en `kg` y `l`, enteros en `g`, `ml` y `unit`; sin coma flotante | validada 2026-10-28 |
| D-16 | El informe de un artículo muestra stock, totales de `inbound` y `outbound`, ajustes por motivo y stock por lote con caducidad | validada 2026-10-28 |
| D-17 | Datos semilla: 16 artículos, sus condiciones de movimientos, reorden y lote caducado del §4.3 del encargo | validada 2026-10-28 |
| P-01 | Campos del artículo y del movimiento: `CONTEXT.md` no define el §3.1 que cita el encargo. El spec usa solo `name`, `locationId`, `category`, `unitOfMeasure` y `reorderPoint` en el artículo, y `quantity` y `reason` como nombres de cantidad y motivo del movimiento. ¿Falta algún campo, o hay otros nombres? | validada 2026-10-28 (sin cambios) |
| P-02 | Cómo nace un lote: un `inbound` con un `lotCode` nuevo y una `expiryDate` lo crea (`receivedAt` = instante del registro) y el `lotCode` es único en todo el sistema, de modo que referenciar el lote de otro artículo es siempre un rechazo (INV-028–INV-031, INV-033) | validada 2026-10-28 |
| P-03 | Un `inbound` no se restringe por caducidad: puede abrir un lote ya caducado o sumar a uno caducado. La semilla lo necesita para el lote de *Cilantro* (INV-055) | validada 2026-10-28 |
| P-04 | El movimiento no registra autor, porque no hay autenticación y el encargo no lo pide | validada 2026-10-28 |
| P-05 | No hay restricción de unicidad del `name` de un artículo dentro de un local | validada 2026-10-28 |
| P-06 | `reorderPoint` admite 0 y se rige por la precisión de la unidad del artículo (INV-003) | validada 2026-10-28 |
| P-07 | Ejecutar la semilla sobre una base con artículos se rechaza sin cambiar nada (INV-066) | validada 2026-10-28 |
| P-08 | `CONTEXT.md` habla de 14 locales y el encargo fija 4 (D-08). Se aplican los 4 y el resto queda fuera de alcance | validada 2026-10-28 |

## 8. Historial de cambios
| Versión | Fecha | Secciones / INV cambiados | Motivo |
|---|---|---|---|
| 1.0 | 2026-10-28 | Todas · INV-001–INV-066 | Versión inicial del Paso 03; aprobada por el usuario con P-01–P-08 validadas |
