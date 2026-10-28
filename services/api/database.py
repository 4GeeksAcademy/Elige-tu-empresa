"""SQLite connection and schema management."""

import sqlite3
from os import PathLike

from services.api.catalogs import catalogIds


def _sqlValues(values: tuple[str, ...]) -> str:
    return ", ".join("'" + value.replace("'", "''") + "'" for value in values)


def _catalogCheck(columnName: str, values: tuple[str, ...]) -> str:
    return f"{columnName} TEXT NOT NULL CHECK ({columnName} IN ({_sqlValues(values)}))"


def stockDeltaSql(columnPrefix: str = "") -> str:
    """SQL expression for the signed effect of one movement on stock."""
    return (
        f"CASE {columnPrefix}movementType WHEN 'outbound' "
        f"THEN -{columnPrefix}quantityMilli ELSE {columnPrefix}quantityMilli END"
    )


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
        f"""
        CREATE TABLE IF NOT EXISTS inventoryItems (
            id TEXT PRIMARY KEY NOT NULL
                CHECK (
                    length(id) = 36
                    AND id GLOB '????????-????-4???-[89ab]???-????????????'
                    AND id NOT GLOB '*[^0-9a-f-]*'
                ),
            name TEXT NOT NULL CHECK (length(trim(name)) > 0),
            {_catalogCheck("locationId", catalogIds("locations"))},
            {_catalogCheck("category", catalogIds("categories"))},
            {_catalogCheck("unitOfMeasure", catalogIds("units"))},
            reorderPointMilli INTEGER NOT NULL CHECK (reorderPointMilli >= 0),
            createdAt TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS inventoryLots (
            lotCode TEXT PRIMARY KEY NOT NULL CHECK (length(trim(lotCode)) > 0),
            itemId TEXT NOT NULL REFERENCES inventoryItems(id),
            expiryDate TEXT NOT NULL
                CHECK (expiryDate GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
            receivedAt TEXT NOT NULL,
            UNIQUE (itemId, lotCode)
        )
        """,
        """
        CREATE TRIGGER IF NOT EXISTS inventoryLots_preventUpdate
        BEFORE UPDATE ON inventoryLots
        BEGIN
            SELECT RAISE(ABORT, 'Inventory lots are immutable');
        END
        """,
        """
        CREATE TRIGGER IF NOT EXISTS inventoryLots_preventDelete
        BEFORE DELETE ON inventoryLots
        BEGIN
            SELECT RAISE(ABORT, 'Inventory lots are immutable');
        END
        """,
        f"""
        CREATE TABLE IF NOT EXISTS stockMovements (
            id TEXT PRIMARY KEY NOT NULL
                CHECK (
                    length(id) = 36
                    AND id GLOB '????????-????-4???-[89ab]???-????????????'
                    AND id NOT GLOB '*[^0-9a-f-]*'
                ),
            itemId TEXT NOT NULL REFERENCES inventoryItems(id),
            lotCode TEXT,
            {_catalogCheck("movementType", catalogIds("movementTypes"))},
            quantityMilli INTEGER NOT NULL,
            reason TEXT NOT NULL,
            createdAt TEXT NOT NULL,
            FOREIGN KEY (itemId, lotCode) REFERENCES inventoryLots(itemId, lotCode),
            CHECK (
                (
                    movementType IN ('inbound', 'outbound')
                    AND quantityMilli > 0
                    AND length(trim(reason)) > 0
                )
                OR (
                    movementType = 'adjustment'
                    AND quantityMilli <> 0
                    AND reason IN ({_sqlValues(catalogIds("adjustmentReasons"))})
                    AND (reason = 'count_correction' OR quantityMilli < 0)
                )
            )
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS stockMovementsItemIdCreatedAt
        ON stockMovements (itemId, createdAt)
        """,
        """
        CREATE INDEX IF NOT EXISTS stockMovementsItemIdLotCode
        ON stockMovements (itemId, lotCode)
        """,
        f"""
        CREATE TRIGGER IF NOT EXISTS stockMovements_preventNegativeStock
        BEFORE INSERT ON stockMovements
        BEGIN
            SELECT RAISE(ABORT, 'Item stock cannot be negative')
            WHERE COALESCE(
                (
                    SELECT SUM({stockDeltaSql()}) FROM stockMovements
                    WHERE itemId = NEW.itemId
                ),
                0
            ) + {stockDeltaSql("NEW.")} < 0;
            SELECT RAISE(ABORT, 'Lot stock cannot be negative')
            WHERE NEW.lotCode IS NOT NULL AND COALESCE(
                (
                    SELECT SUM({stockDeltaSql()}) FROM stockMovements
                    WHERE itemId = NEW.itemId AND lotCode = NEW.lotCode
                ),
                0
            ) + {stockDeltaSql("NEW.")} < 0;
        END
        """,
        """
        CREATE TRIGGER IF NOT EXISTS stockMovements_preventUpdate
        BEFORE UPDATE ON stockMovements
        BEGIN
            SELECT RAISE(ABORT, 'Stock movements are immutable');
        END
        """,
        """
        CREATE TRIGGER IF NOT EXISTS stockMovements_preventDelete
        BEFORE DELETE ON stockMovements
        BEGIN
            SELECT RAISE(ABORT, 'Stock movements are immutable');
        END
        """,
    )

    for statement in schemaStatements:
        connection.execute(statement)
    connection.commit()
