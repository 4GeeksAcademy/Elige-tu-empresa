"""SQLite connection and schema management."""

import sqlite3
from os import PathLike

from services.api.catalogs import catalogIds


def _sqlValues(values: tuple[str, ...]) -> str:
    return ", ".join("'" + value.replace("'", "''") + "'" for value in values)


def _catalogCheck(columnName: str, values: tuple[str, ...]) -> str:
    return f"{columnName} TEXT NOT NULL CHECK ({columnName} IN ({_sqlValues(values)}))"


def createConnection(databasePath: str | PathLike[str]) -> sqlite3.Connection:
    connection = sqlite3.connect(str(databasePath))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def initializeDatabase(connection: sqlite3.Connection) -> None:
    schemaStatements = (
        f"""
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY NOT NULL
                CHECK (
                    length(id) = 36
                    AND id GLOB '????????-????-4???-[89ab]???-????????????'
                    AND id NOT GLOB '*[^0-9a-f-]*'
                ),
            {_catalogCheck("channelId", catalogIds("channels"))},
            {_catalogCheck("typeId", catalogIds("incidentTypes"))},
            {_catalogCheck("severityId", catalogIds("severities"))},
            {_catalogCheck("responsibleAreaId", catalogIds("responsibleAreas", assignableOnly=True))},
            {_catalogCheck("statusId", catalogIds("statuses"))},
            title TEXT NOT NULL CHECK (length(trim(title)) > 0),
            description TEXT NOT NULL,
            createdAt TEXT NOT NULL,
            updatedAt TEXT NOT NULL,
            createdBy TEXT NOT NULL CHECK (length(trim(createdBy)) > 0)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS historyEvents (
            id TEXT PRIMARY KEY NOT NULL
                CHECK (
                    length(id) = 36
                    AND id GLOB '????????-????-4???-[89ab]???-????????????'
                    AND id NOT GLOB '*[^0-9a-f-]*'
                ),
            incidentId TEXT NOT NULL REFERENCES incidents(id),
            changeType TEXT NOT NULL CHECK (changeType IN ('estado', 'areaResponsable')),
            previousValue TEXT NOT NULL,
            newValue TEXT NOT NULL,
            author TEXT NOT NULL CHECK (length(trim(author)) > 0),
            createdAt TEXT NOT NULL
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS historyEventsIncidentIdCreatedAt
        ON historyEvents (incidentId, createdAt)
        """,
        """
        CREATE TRIGGER IF NOT EXISTS historyEvents_preventUpdate
        BEFORE UPDATE ON historyEvents
        BEGIN
            SELECT RAISE(ABORT, 'History events are immutable');
        END
        """,
        """
        CREATE TRIGGER IF NOT EXISTS historyEvents_preventDelete
        BEFORE DELETE ON historyEvents
        BEGIN
            SELECT RAISE(ABORT, 'History events are immutable');
        END
        """,
    )

    for statement in schemaStatements:
        connection.execute(statement)
    connection.commit()
