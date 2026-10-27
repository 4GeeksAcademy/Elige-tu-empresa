"""Incident registration use case."""

import sqlite3

from services.api.catalogs import catalogIds
from services.api.models import Incident, formatUtcTimestamp, generateId, utcNow


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
