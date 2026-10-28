"""Domain models and UTC timestamp helpers."""

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class Incident:
    id: str
    channelId: str
    typeId: str
    severityId: str
    responsibleAreaId: str
    statusId: str
    title: str
    description: str
    createdAt: datetime
    updatedAt: datetime
    createdBy: str


@dataclass(frozen=True, slots=True)
class HistoryEvent:
    id: str
    incidentId: str
    changeType: str
    previousValue: str
    newValue: str
    author: str
    createdAt: datetime


@dataclass(frozen=True, slots=True)
class IncidentDetails:
    incident: Incident
    historyEvents: tuple[HistoryEvent, ...]


@dataclass(frozen=True, slots=True)
class InventoryItem:
    id: str
    name: str
    locationId: str
    category: str
    unitOfMeasure: str
    reorderPointMilli: int
    createdAt: datetime


@dataclass(frozen=True, slots=True)
class InventoryLot:
    lotCode: str
    itemId: str
    expiryDate: str
    receivedAt: datetime


@dataclass(frozen=True, slots=True)
class StockMovement:
    id: str
    itemId: str
    lotCode: str | None
    movementType: str
    quantityMilli: int
    reason: str
    createdAt: datetime


def generateId() -> str:
    return str(uuid4())


def utcNow() -> datetime:
    return datetime.now(timezone.utc)


def formatUtcTimestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Timestamp must include a timezone")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parseUtcTimestamp(value: str) -> datetime:
    normalizedValue = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsedValue = datetime.fromisoformat(normalizedValue)
    if parsedValue.tzinfo is None or parsedValue.utcoffset() is None:
        raise ValueError("Timestamp must include a timezone")
    return parsedValue.astimezone(timezone.utc)


def isUuid4(value: str) -> bool:
    try:
        parsedId = UUID(value)
        return str(parsedId) == value and parsedId.version == 4
    except ValueError:
        return False
