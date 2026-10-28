"""Inventory use cases and stock helpers."""

import re

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
