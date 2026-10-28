"""Inventory use cases and stock helpers."""

import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from services.api.catalogs import catalogIds
from services.api.database import stockDeltaSql
from services.api.models import formatUtcTimestamp, generateId, utcNow

quantityScale = 1000
unitDecimals = {"kg": 3, "l": 3, "g": 0, "ml": 0, "unit": 0}
quantityPattern = re.compile(r"-?(\d+)(?:\.(\d+))?")
itemFieldNames = frozenset({"name", "locationId", "category", "unitOfMeasure", "reorderPoint"})
movementFieldNames = frozenset({"movementType", "quantity", "reason"})
reducingAdjustmentReasons = ("waste", "theft")


class BusinessRuleError(Exception):
    """The data is valid, but the operation breaks a stock, lot, expiry or state rule."""


@contextmanager
def _transaction(connection: sqlite3.Connection):
    """Open an immediate transaction, or join the one the caller already opened."""
    if connection.in_transaction:
        yield
        return
    connection.execute("BEGIN IMMEDIATE")
    try:
        yield
    except BaseException:
        connection.rollback()
        raise
    connection.commit()


def _decimalsFor(unitOfMeasure: str) -> int:
    try:
        return unitDecimals[unitOfMeasure]
    except (KeyError, TypeError) as error:
        raise ValueError(f"Unknown unit: {unitOfMeasure}") from error


def parseQuantity(text: object, unitOfMeasure: str) -> int:
    """Convert a decimal string to integer thousandths using the unit precision."""
    allowedDecimals = _decimalsFor(unitOfMeasure)
    if not isinstance(text, str):
        raise ValueError("Quantity must be a decimal string")
    match = quantityPattern.fullmatch(text)
    if match is None:
        raise ValueError("Quantity must be a decimal string such as 12.500")
    wholePart, decimalPart = match.group(1), match.group(2) or ""
    if len(decimalPart) > allowedDecimals:
        raise ValueError(f"Quantity admits at most {allowedDecimals} decimal places for {unitOfMeasure}")
    thousandths = int(wholePart) * quantityScale + int(decimalPart.ljust(3, "0") or "0")
    return -thousandths if text.startswith("-") else thousandths


def formatQuantity(thousandths: int, unitOfMeasure: str) -> str:
    """Convert integer thousandths to a decimal string with the unit precision."""
    allowedDecimals = _decimalsFor(unitOfMeasure)
    sign = "-" if thousandths < 0 else ""
    whole, fraction = divmod(abs(thousandths), quantityScale)
    if allowedDecimals == 0:
        if fraction:
            raise ValueError(f"Quantity admits no decimal places for {unitOfMeasure}")
        return f"{sign}{whole}"
    return f"{sign}{whole}.{fraction:03d}"


def calculateStock(
    connection: sqlite3.Connection,
    *,
    itemId: str | None = None,
    locationId: str | None = None,
    groupByLot: bool = False,
) -> dict:
    """Stock in thousandths keyed by item id, or by (item id, lot code) with groupByLot."""
    delta = stockDeltaSql("m.")
    if groupByLot:
        query = f"""
            SELECT l.itemId AS itemId, l.lotCode AS lotCode, COALESCE(SUM({delta}), 0) AS stock
            FROM inventoryLots l
            JOIN inventoryItems i ON i.id = l.itemId
            LEFT JOIN stockMovements m ON m.itemId = l.itemId AND m.lotCode = l.lotCode
            WHERE (:itemId IS NULL OR i.id = :itemId) AND (:locationId IS NULL OR i.locationId = :locationId)
            GROUP BY l.itemId, l.lotCode
        """
    else:
        query = f"""
            SELECT i.id AS itemId, NULL AS lotCode, COALESCE(SUM({delta}), 0) AS stock
            FROM inventoryItems i
            LEFT JOIN stockMovements m ON m.itemId = i.id
            WHERE (:itemId IS NULL OR i.id = :itemId) AND (:locationId IS NULL OR i.locationId = :locationId)
            GROUP BY i.id
        """
    rows = connection.execute(query, {"itemId": itemId, "locationId": locationId})
    if groupByLot:
        return {(row["itemId"], row["lotCode"]): row["stock"] for row in rows}
    return {row["itemId"]: row["stock"] for row in rows}


def _requireSupportedFields(fields: dict) -> None:
    if not isinstance(fields, dict):
        raise ValueError("Item fields must be an object")
    unsupported = fields.keys() - itemFieldNames
    if unsupported:
        raise ValueError(f"Unsupported fields: {', '.join(sorted(unsupported))}")


def _validatedItemFields(fields: dict) -> dict:
    _requireSupportedFields(fields)
    missing = itemFieldNames - fields.keys()
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(sorted(missing))}")

    name = fields["name"]
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")
    validated = {"name": name.strip()}
    for fieldName, catalogName in (
        ("locationId", "locations"),
        ("category", "categories"),
        ("unitOfMeasure", "units"),
    ):
        value = fields[fieldName]
        if not isinstance(value, str) or value not in catalogIds(catalogName):
            raise ValueError(f"{fieldName} is not in the {catalogName} catalog")
        validated[fieldName] = value

    reorderPointMilli = parseQuantity(fields["reorderPoint"], validated["unitOfMeasure"])
    if reorderPointMilli < 0:
        raise ValueError("reorderPoint must not be negative")
    validated["reorderPointMilli"] = reorderPointMilli
    return validated


def _itemView(connection: sqlite3.Connection, row: sqlite3.Row, stockMilli: int | None = None) -> dict:
    if stockMilli is None:
        stockMilli = calculateStock(connection, itemId=row["id"])[row["id"]]
    unitOfMeasure = row["unitOfMeasure"]
    return {
        "id": row["id"],
        "name": row["name"],
        "locationId": row["locationId"],
        "category": row["category"],
        "unitOfMeasure": unitOfMeasure,
        "reorderPoint": formatQuantity(row["reorderPointMilli"], unitOfMeasure),
        "stock": formatQuantity(stockMilli, unitOfMeasure),
        "needsReorder": stockMilli <= row["reorderPointMilli"],
        "createdAt": row["createdAt"],
    }


def createItem(connection: sqlite3.Connection, fields: dict, now: datetime | None = None) -> dict:
    validated = _validatedItemFields(fields)
    itemId = generateId()
    with _transaction(connection):
        connection.execute(
            """
            INSERT INTO inventoryItems (
                id, name, locationId, category, unitOfMeasure, reorderPointMilli, createdAt
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                itemId,
                validated["name"],
                validated["locationId"],
                validated["category"],
                validated["unitOfMeasure"],
                validated["reorderPointMilli"],
                formatUtcTimestamp(now or utcNow()),
            ),
        )
        row = connection.execute("SELECT * FROM inventoryItems WHERE id = ?", (itemId,)).fetchone()
        return _itemView(connection, row)


def _fetchItemRow(connection: sqlite3.Connection, itemId: str) -> sqlite3.Row:
    row = connection.execute("SELECT * FROM inventoryItems WHERE id = ?", (itemId,)).fetchone()
    if row is None:
        raise LookupError("Item not found")
    return row


def _hasMovements(connection: sqlite3.Connection, itemId: str) -> bool:
    return connection.execute("SELECT 1 FROM stockMovements WHERE itemId = ? LIMIT 1", (itemId,)).fetchone() is not None


def updateItem(connection: sqlite3.Connection, itemId: str, changes: dict) -> dict:
    _requireSupportedFields(changes)
    if not changes:
        raise ValueError("No fields to update")
    with _transaction(connection):
        row = _fetchItemRow(connection, itemId)
        merged = {
            "name": row["name"],
            "locationId": row["locationId"],
            "category": row["category"],
            "unitOfMeasure": row["unitOfMeasure"],
            **changes,
        }
        if "reorderPoint" not in changes:
            merged["reorderPoint"] = formatQuantity(row["reorderPointMilli"], merged["unitOfMeasure"])
        validated = _validatedItemFields(merged)
        structuralChange = any(
            validated[fieldName] != row[fieldName] for fieldName in ("locationId", "category", "unitOfMeasure")
        )
        if structuralChange and _hasMovements(connection, itemId):
            raise BusinessRuleError("locationId, category and unitOfMeasure cannot change once the item has movements")
        connection.execute(
            """
            UPDATE inventoryItems
            SET name = ?, locationId = ?, category = ?, unitOfMeasure = ?, reorderPointMilli = ?
            WHERE id = ?
            """,
            (
                validated["name"],
                validated["locationId"],
                validated["category"],
                validated["unitOfMeasure"],
                validated["reorderPointMilli"],
                itemId,
            ),
        )
        return _itemView(connection, _fetchItemRow(connection, itemId))


def deleteItem(connection: sqlite3.Connection, itemId: str) -> dict:
    with _transaction(connection):
        _fetchItemRow(connection, itemId)
        if _hasMovements(connection, itemId):
            raise BusinessRuleError("An item with movements cannot be deleted")
        connection.execute("DELETE FROM inventoryItems WHERE id = ?", (itemId,))
    return {"deleted": itemId}


def getItem(connection: sqlite3.Connection, itemId: str) -> dict:
    return _itemView(connection, _fetchItemRow(connection, itemId))


def listItems(connection: sqlite3.Connection, locationId: str | None = None) -> list[dict]:
    if locationId is not None and (not isinstance(locationId, str) or locationId not in catalogIds("locations")):
        raise LookupError("Location not found")
    stockByItem = calculateStock(connection, locationId=locationId)
    rows = connection.execute(
        """
        SELECT * FROM inventoryItems
        WHERE (:locationId IS NULL OR locationId = :locationId)
        ORDER BY locationId, name, id
        """,
        {"locationId": locationId},
    ).fetchall()
    return [_itemView(connection, row, stockByItem[row["id"]]) for row in rows]


def registerMovement(
    connection: sqlite3.Connection,
    itemId: str,
    fields: dict,
    now: datetime | None = None,
) -> dict:
    if not isinstance(fields, dict):
        raise ValueError("Movement fields must be an object")
    unsupported = fields.keys() - movementFieldNames
    if unsupported:
        raise ValueError(f"Unsupported fields: {', '.join(sorted(unsupported))}")
    missing = movementFieldNames - fields.keys()
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(sorted(missing))}")
    movementType = fields["movementType"]
    if not isinstance(movementType, str) or movementType not in catalogIds("movementTypes"):
        raise ValueError("movementType is not in the movementTypes catalog")

    with _transaction(connection):
        itemRow = _fetchItemRow(connection, itemId)
        unitOfMeasure = itemRow["unitOfMeasure"]
        quantityMilli = parseQuantity(fields["quantity"], unitOfMeasure)
        reason = fields["reason"]
        if movementType == "adjustment":
            if quantityMilli == 0:
                raise ValueError("quantity must not be zero")
            if not isinstance(reason, str) or reason not in catalogIds("adjustmentReasons"):
                raise ValueError("reason is not in the adjustmentReasons catalog")
            if reason in reducingAdjustmentReasons and quantityMilli > 0:
                raise ValueError(f"quantity must be negative for {reason}")
            stockChangeMilli = quantityMilli
        else:
            if quantityMilli <= 0:
                raise ValueError("quantity must be positive")
            if not isinstance(reason, str) or not reason.strip():
                raise ValueError("reason must be a non-empty string")
            reason = reason.strip()
            stockChangeMilli = -quantityMilli if movementType == "outbound" else quantityMilli
        if stockChangeMilli < 0 and calculateStock(connection, itemId=itemId)[itemId] + stockChangeMilli < 0:
            raise BusinessRuleError("Not enough stock for this movement")

        movementId = generateId()
        createdAt = formatUtcTimestamp(now or utcNow())
        connection.execute(
            """
            INSERT INTO stockMovements (id, itemId, lotCode, movementType, quantityMilli, reason, createdAt)
            VALUES (?, ?, NULL, ?, ?, ?, ?)
            """,
            (movementId, itemId, movementType, quantityMilli, reason, createdAt),
        )
        stockMilli = calculateStock(connection, itemId=itemId)[itemId]
        return {
            "id": movementId,
            "itemId": itemId,
            "movementType": movementType,
            "quantity": formatQuantity(quantityMilli, unitOfMeasure),
            "reason": reason,
            "lotCode": None,
            "createdAt": createdAt,
            "stock": formatQuantity(stockMilli, unitOfMeasure),
        }
