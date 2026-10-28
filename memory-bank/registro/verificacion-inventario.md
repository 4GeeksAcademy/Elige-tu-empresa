# Verificación integrada — gestor de inventario

- **Fecha:** 2026-10-28
- **Base:** SQLite temporal `/tmp/brasaland-inventory-t29-20261028.sqlite`; no se utilizó ni alteró la base persistente del proyecto.
- **Datos de partida:** semilla existente comprobada en solo lectura antes del recorrido: 16 artículos y 49 movimientos. La semilla define cuatro artículos por local.
- **Servidor:** `services.api.server` en `127.0.0.1:8000`; los cambios de movimientos descritos abajo afectaron solo a la base temporal.
- **Alcance visual:** no se afirma una inspección visual del navegador. Se comprobó la página por HTTP y comportamiento mediante API; no se encontró navegador instalado en el entorno.

## Suite automatizada

`PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v` → **188 pruebas, OK** (`Ran 188 tests`, `OK`). Incluye los tests del backoffice para estructura y contenido servido; no equivale a una comprobación visual en navegador.

## Recorrido HTTP con semilla real

| Escenario | Pasos | Esperado | Obtenido | ✅/❌ |
|---|---|---|---|---|
| Página de inventario | `GET /inventory.html` | HTTP 200 | HTTP 200 | ✅ |
| Stock por local | `GET /api/inventory/items?locationId=…` para `laArepita`, `queChille`, `theBigSauce`, `chilliBeans` | HTTP 200 y cuatro artículos en cada local | HTTP 200 y cuatro artículos en cada local | ✅ |
| Señal de reorden | `GET /api/inventory/locations/{locationId}/reorder` en los cuatro locales | `Salsa de ajo de la casa` para `laArepita`, `Envases para llevar` para `theBigSauce`; lista vacía para `queChille` y `chilliBeans` | Resultados exactamente iguales a los esperados | ✅ |
| Informe y ajustes | Consultar el informe de Cilantro, `queChille` | Informe HTTP 200 y motivos `waste`, `theft` y `count_correction` distinguibles | HTTP 200; `adjustments` contenía esos tres motivos separados | ✅ |
| Stock caducado inicial | Consultar lotes de Cilantro antes del ajuste | Lote caducado identificable y stock incluido en el disponible, presentado separadamente | `queChille-06-expired`, 7.000; visible en los datos del informe | ✅ |
| Rechazo de stock negativo | `POST /api/inventory/items/{id}/movements`, salida de 999.000 de Salsa de ajo | HTTP 409, sin aceptar movimiento que deja stock negativo | HTTP 409, `Not enough stock for this movement` | ✅ |
| Rechazo de lote inexistente | `POST` de salida para Cilantro con `lotCode=lote-inexistente` | Recurso inexistente: HTTP 404; no se registra el movimiento | HTTP 404, `Lot not found` | ✅ |
| Rechazo de salida de lote caducado | `POST` de salida de 0.001 para el lote `queChille-06-expired` | HTTP 409 por regla de lote caducado | HTTP 409, `An expired lot does not admit outbound movements` | ✅ |
| Retirada de caducado | `POST` de ajuste negativo con motivo `waste` sobre `queChille-06-expired` | HTTP 201 y stock caducado reducido | HTTP 201 | ✅ |
| Informe después de retirada | Consultar de nuevo el informe de Cilantro | El lote debe mostrar `expiredStock=0.000` | HTTP 200; `expiredStock=0.000` | ✅ |

### Nota sobre la clasificación HTTP

El primer guion de comprobación esperaba equivocadamente `409` para un lote inexistente y terminó con código 1 al recibir `404`. Según el spec, el lote inexistente es un **recurso inexistente** (404); el rechazo de negocio, como salida de lote caducado o stock insuficiente, es 409. El recorrido repetido registró el 404 esperado como aprobado. No hubo fallo de la aplicación.

### Nota sobre el estado temporal

El recorrido retiró expresamente las 7.000 unidades del lote caducado de Cilantro mediante un ajuste `waste`; el informe posterior confirmó saldo caducado cero. Por tanto, la base temporal usada en esta sesión ya no conserva el estado inicial de la semilla. La base persistente no se tocó. Para reproducir desde cero, usar una ruta nueva:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m services.api.inventoryseed --database /tmp/inventory-verification.sqlite
PYTHONDONTWRITEBYTECODE=1 python -c "from services.api.server import createServer; server = createServer('/tmp/inventory-verification.sqlite'); print('http://127.0.0.1:8000'); server.serve_forever()"
```

Ejecuta primero la semilla y después inicia el servidor en otra terminal con `createServer` apuntando a la misma ruta temporal. El comando de módulo `python -m services.api.server` usa la base persistente `data/incidents.sqlite` y no ofrece un argumento CLI para cambiarla. El servidor del recorrido registrado usó explícitamente la base temporal indicada arriba.
