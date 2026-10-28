"""Inventory use cases and stock helpers."""

import re
import sqlite3

from services.api.database import stockDeltaSql

quantityScale = 1000
unitDecimals = {"kg": 3, "l": 3, "g": 0, "ml": 0, "unit": 0}
quantityPattern = re.compile(r"-?(\d+)(?:\.(\d+))?")


def _decimalsFor(unitOfMeasure: str) -> int:
    try:
        return unitDecimals[unitOfMeasure]
    except KeyError as error:
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
