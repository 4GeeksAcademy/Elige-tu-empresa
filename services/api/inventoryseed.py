"""Inventory seed data, loaded only through the inventory use cases."""

import sqlite3
from datetime import datetime, timedelta, timezone

from services.api.inventory import createItem, formatQuantity, parseQuantity, registerMovement
from services.api.models import utcNow

seedLotLifeDays = 30
lotControlledSeedCategories = ("meat", "produce")
adjustmentReasonCycle = ("waste", "theft", "count_correction")
reorderSeedItems = (("laArepita", "Salsa de ajo de la casa"), ("theBigSauce", "Envases para llevar"))
expiredLotItem = ("queChille", "Cilantro")
expiredLotExpiryDate = "2026-10-01"

seedItems = (
    ("laArepita", "Punta de anca de res", "meat", "kg", "20"),
    ("laArepita", "Pechuga de pollo", "meat", "kg", "15"),
    ("laArepita", "Cebolla cabezona", "produce", "kg", "10"),
    ("laArepita", "Salsa de ajo de la casa", "sauces_condiments", "l", "5"),
    ("queChille", "Costilla de cerdo", "meat", "kg", "12"),
    ("queChille", "Cilantro", "produce", "kg", "2"),
    ("queChille", "Jugo de lulo", "beverages", "l", "10"),
    ("queChille", "Desengrasante", "cleaning_supplies", "l", "4"),
    ("theBigSauce", "Brisket de res", "meat", "kg", "25"),
    ("theBigSauce", "Salsa BBQ de la casa", "sauces_condiments", "l", "8"),
    ("theBigSauce", "Refresco de cola", "beverages", "unit", "48"),
    ("theBigSauce", "Envases para llevar", "packaging", "unit", "200"),
    ("chilliBeans", "Alitas de pollo", "meat", "kg", "18"),
    ("chilliBeans", "Jalapeños", "produce", "kg", "3"),
    ("chilliBeans", "Servilletas", "packaging", "unit", "500"),
    ("chilliBeans", "Desinfectante", "cleaning_supplies", "l", "5"),
)


def _movementPlan(
    position: int,
    locationId: str,
    name: str,
    category: str,
    reorderPointMilli: int,
) -> list[tuple[str, int, str, str | None]]:
    """Movements (type, signed thousandths, reason, lot) of one item, sized from its reorder point.

    The lot is "fresh", "expired" or None for items without lot control.
    """
    freshLot = "fresh" if category in lotControlledSeedCategories else None
    if (locationId, name) == expiredLotItem:
        return [
            ("inbound", 4 * reorderPointMilli, "Compra semanal", "expired"),
            ("adjustment", -(reorderPointMilli // 2), "waste", "expired"),
            ("inbound", 2 * reorderPointMilli, "Compra semanal", "fresh"),
            ("outbound", reorderPointMilli, "Consumo de cocina", "fresh"),
        ]
    if (locationId, name) in reorderSeedItems:
        return [
            ("inbound", 2 * reorderPointMilli, "Compra semanal", freshLot),
            ("outbound", reorderPointMilli, "Consumo de cocina", freshLot),
            ("adjustment", -(reorderPointMilli // 5), "waste", freshLot),
        ]
    reason = adjustmentReasonCycle[position % len(adjustmentReasonCycle)]
    adjustment = reorderPointMilli // 2
    return [
        ("inbound", 4 * reorderPointMilli, "Compra semanal", freshLot),
        ("outbound", reorderPointMilli, "Consumo de cocina", freshLot),
        ("adjustment", adjustment if reason == "count_correction" else -adjustment, reason, freshLot),
    ]


def loadInventorySeed(connection: sqlite3.Connection, now: datetime | None = None) -> dict:
    moment = now or utcNow()
    lotExpiryDate = (moment.astimezone(timezone.utc).date() + timedelta(days=seedLotLifeDays)).isoformat()
    movementCount = 0
    for position, (locationId, name, category, unitOfMeasure, reorderPoint) in enumerate(seedItems):
        item = createItem(
            connection,
            {
                "name": name,
                "locationId": locationId,
                "category": category,
                "unitOfMeasure": unitOfMeasure,
                "reorderPoint": reorderPoint,
            },
            now=moment,
        )
        reorderPointMilli = parseQuantity(reorderPoint, unitOfMeasure)
        lotBaseCode = f"{locationId}-{position + 1:02d}"
        lots = {
            "fresh": (lotBaseCode, lotExpiryDate),
            "expired": (f"{lotBaseCode}-expired", expiredLotExpiryDate),
        }
        openedLots = set()
        for movementType, quantityMilli, reason, lotRole in _movementPlan(
            position, locationId, name, category, reorderPointMilli
        ):
            fields = {
                "movementType": movementType,
                "quantity": formatQuantity(quantityMilli, unitOfMeasure),
                "reason": reason,
            }
            if lotRole is not None:
                fields["lotCode"], expiryDate = lots[lotRole]
                if lotRole not in openedLots:
                    fields["expiryDate"] = expiryDate
                    openedLots.add(lotRole)
            registerMovement(connection, item["id"], fields, now=moment)
            movementCount += 1
    return {"items": len(seedItems), "movements": movementCount}
