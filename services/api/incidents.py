"""Incident registration use case."""

import sqlite3

from services.api.catalogs import catalogIds
from services.api.models import (
    HistoryEvent,
    Incident,
    IncidentDetails,
    formatUtcTimestamp,
    generateId,
    parseUtcTimestamp,
    utcNow,
)


allowedStatusTransitions = {
    "nueva": ("enCurso",),
    "enCurso": ("resuelta",),
    "resuelta": ("cerrada", "enCurso"),
    "cerrada": (),
}


def _requiredText(fieldName: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{fieldName} must not be blank")
    return value.strip()


def _requireCatalogValue(
    fieldName: str,
    value: str,
    catalogName: str,
    assignableOnly: bool = False,
) -> str:
    allowedIds = catalogIds(catalogName, assignableOnly=assignableOnly)
    if value not in allowedIds:
        raise ValueError(f"{fieldName} must be one of: {', '.join(allowedIds)}")
    return value


def registerIncident(
    connection: sqlite3.Connection,
    channelId: str,
    typeId: str,
    severityId: str,
    responsibleAreaId: str,
    title: str,
    description: str,
    createdBy: str,
) -> Incident:
    """Validate and persist an incident in the initial `nueva` status."""
    validatedChannelId = _requireCatalogValue("channelId", channelId, "channels")
    validatedTypeId = _requireCatalogValue("typeId", typeId, "incidentTypes")
    validatedSeverityId = _requireCatalogValue("severityId", severityId, "severities")
    validatedAreaId = _requireCatalogValue(
        "responsibleAreaId",
        responsibleAreaId,
        "responsibleAreas",
        assignableOnly=True,
    )
    validatedTitle = _requiredText("title", title)
    validatedAuthor = _requiredText("createdBy", createdBy)
    if not isinstance(description, str):
        raise ValueError("description must be text")

    timestamp = utcNow()
    storedTimestamp = formatUtcTimestamp(timestamp)
    incident = Incident(
        id=generateId(),
        channelId=validatedChannelId,
        typeId=validatedTypeId,
        severityId=validatedSeverityId,
        responsibleAreaId=validatedAreaId,
        statusId="nueva",
        title=validatedTitle,
        description=description,
        createdAt=timestamp,
        updatedAt=timestamp,
        createdBy=validatedAuthor,
    )

    with connection:
        connection.execute(
            """
            INSERT INTO incidents (
                id, channelId, typeId, severityId, responsibleAreaId, statusId,
                title, description, createdAt, updatedAt, createdBy
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                incident.id,
                incident.channelId,
                incident.typeId,
                incident.severityId,
                incident.responsibleAreaId,
                incident.statusId,
                incident.title,
                incident.description,
                storedTimestamp,
                storedTimestamp,
                incident.createdBy,
            ),
        )

    return incident


def _incidentFromRow(row: sqlite3.Row) -> Incident:
    return Incident(
        id=row["id"],
        channelId=row["channelId"],
        typeId=row["typeId"],
        severityId=row["severityId"],
        responsibleAreaId=row["responsibleAreaId"],
        statusId=row["statusId"],
        title=row["title"],
        description=row["description"],
        createdAt=parseUtcTimestamp(row["createdAt"]),
        updatedAt=parseUtcTimestamp(row["updatedAt"]),
        createdBy=row["createdBy"],
    )


def _recordIncidentChange(
    connection: sqlite3.Connection,
    incidentId: str,
    fieldName: str,
    changeType: str,
    newValue: str,
    author: str,
) -> None:
    validatedAuthor = _requiredText("author", author)
    if fieldName == "statusId":
        _requireCatalogValue("statusId", newValue, "statuses")
    elif fieldName == "responsibleAreaId":
        _requireCatalogValue(
            "responsibleAreaId",
            newValue,
            "responsibleAreas",
            assignableOnly=True,
        )
    else:
        raise ValueError("Unsupported incident field")

    with connection:
        row = connection.execute(
            f"SELECT {fieldName} FROM incidents WHERE id = ?",
            (incidentId,),
        ).fetchone()
        if row is None:
            raise LookupError("Incident not found")

        previousValue = row[fieldName]
        if previousValue == newValue:
            raise ValueError(f"{fieldName} is already set to {newValue}")
        if fieldName == "statusId" and newValue not in allowedStatusTransitions[previousValue]:
            raise ValueError(f"Status transition {previousValue} -> {newValue} is not allowed")

        storedTimestamp = formatUtcTimestamp(utcNow())
        updateResult = connection.execute(
            f"""
            UPDATE incidents
            SET {fieldName} = ?, updatedAt = ?
            WHERE id = ? AND {fieldName} = ?
            """,
            (newValue, storedTimestamp, incidentId, previousValue),
        )
        if updateResult.rowcount != 1:
            raise RuntimeError("Incident changed concurrently; retry the operation")

        connection.execute(
            """
            INSERT INTO historyEvents (
                id, incidentId, changeType, previousValue, newValue, author, createdAt
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                generateId(),
                incidentId,
                changeType,
                previousValue,
                newValue,
                validatedAuthor,
                storedTimestamp,
            ),
        )


def changeIncidentStatus(
    connection: sqlite3.Connection,
    incidentId: str,
    newStatusId: str,
    author: str,
) -> Incident:
    """Apply an allowed status transition and append its history event atomically."""
    _recordIncidentChange(
        connection,
        incidentId,
        "statusId",
        "estado",
        newStatusId,
        author,
    )
    row = connection.execute(
        "SELECT * FROM incidents WHERE id = ?",
        (incidentId,),
    ).fetchone()
    if row is None:
        raise LookupError("Incident not found")
    return _incidentFromRow(row)


def reassignIncidentArea(
    connection: sqlite3.Connection,
    incidentId: str,
    responsibleAreaId: str,
    author: str,
) -> Incident:
    """Reassign an incident to an assignable area and append history atomically."""
    _recordIncidentChange(
        connection,
        incidentId,
        "responsibleAreaId",
        "areaResponsable",
        responsibleAreaId,
        author,
    )
    row = connection.execute(
        "SELECT * FROM incidents WHERE id = ?",
        (incidentId,),
    ).fetchone()
    if row is None:
        raise LookupError("Incident not found")
    return _incidentFromRow(row)


def getIncidentDetails(
    connection: sqlite3.Connection,
    incidentId: str,
) -> IncidentDetails:
    """Return an incident and its append-only history in chronological order."""
    incidentRow = connection.execute(
        "SELECT * FROM incidents WHERE id = ?",
        (incidentId,),
    ).fetchone()
    if incidentRow is None:
        raise LookupError("Incident not found")

    eventRows = connection.execute(
        """
        SELECT * FROM historyEvents
        WHERE incidentId = ?
        ORDER BY createdAt ASC, rowid ASC
        """,
        (incidentId,),
    ).fetchall()
    historyEvents = tuple(
        HistoryEvent(
            id=row["id"],
            incidentId=row["incidentId"],
            changeType=row["changeType"],
            previousValue=row["previousValue"],
            newValue=row["newValue"],
            author=row["author"],
            createdAt=parseUtcTimestamp(row["createdAt"]),
        )
        for row in eventRows
    )
    return IncidentDetails(_incidentFromRow(incidentRow), historyEvents)
