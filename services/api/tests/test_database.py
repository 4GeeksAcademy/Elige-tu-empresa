import sqlite3
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from services.api.catalogs import catalogIds, catalogs
from services.api.database import createConnection, initializeDatabase
from services.api.models import (
    formatUtcTimestamp,
    generateId,
    isUuid4,
    parseUtcTimestamp,
    utcNow,
)


class CatalogTests(unittest.TestCase):
    def testCatalogsMatchValidatedDomainValues(self) -> None:
        self.assertEqual(catalogIds("channels"), ("whatsapp", "telefono", "email"))
        self.assertEqual(
            catalogIds("incidentTypes"),
            (
                "operacionRestaurante",
                "comprasProveedores",
                "marketingExperienciaDigital",
                "personasCultura",
                "formacionCalidad",
                "tecnologia",
            ),
        )
        self.assertEqual(catalogIds("severities"), ("critica", "alta", "media", "baja"))
        self.assertEqual(
            tuple(entry.label for entry in catalogs["channels"]),
            ("WhatsApp", "teléfono", "email"),
        )
        self.assertEqual(
            tuple(entry.label for entry in catalogs["incidentTypes"]),
            (
                "Operación de Restaurante",
                "Compras y Proveedores",
                "Marketing y Experiencia Digital",
                "Personas y Cultura",
                "Formación y Calidad",
                "Tecnología",
            ),
        )
        self.assertEqual(
            tuple(entry.label for entry in catalogs["severities"]),
            ("Crítica", "Alta", "Media", "Baja"),
        )
        self.assertEqual(
            catalogIds("responsibleAreas", assignableOnly=True),
            (
                "operacionesRestaurante",
                "comprasProveedores",
                "marketingExperienciaDigital",
                "personasCultura",
                "formacionEstandaresCalidad",
                "tecnologia",
            ),
        )
        self.assertEqual(catalogIds("statuses"), ("nueva", "enCurso", "resuelta", "cerrada"))
        self.assertEqual(
            tuple(entry.label for entry in catalogs["statuses"]),
            ("Nueva", "En curso", "Resuelta", "Cerrada"),
        )
        self.assertFalse(catalogs["responsibleAreas"][-1].assignable)
        self.assertEqual(
            tuple(entry.label for entry in catalogs["responsibleAreas"]),
            (
                "Operaciones de Restaurante",
                "Compras y Proveedores",
                "Marketing y Experiencia Digital",
                "Personas y Cultura",
                "Formación y Estándares de Calidad",
                "Tecnología",
                "Dirección Ejecutiva",
            ),
        )

    def testUnknownCatalogRaisesValueError(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown catalog"):
            catalogIds("unknown")


class ModelTests(unittest.TestCase):
    def testGenerateIdReturnsUuid4(self) -> None:
        self.assertTrue(isUuid4(generateId()))

    def testTimestampRoundTripsAsUtc(self) -> None:
        timestamp = utcNow()
        storedValue = formatUtcTimestamp(timestamp)
        parsedValue = parseUtcTimestamp(storedValue)

        self.assertTrue(storedValue.endswith("Z"))
        self.assertEqual(parsedValue.utcoffset().total_seconds(), 0)
        self.assertEqual(parsedValue, timestamp)

    def testTimestampMustBeTimezoneAware(self) -> None:
        with self.assertRaisesRegex(ValueError, "must include a timezone"):
            formatUtcTimestamp(datetime(2026, 1, 1))
        with self.assertRaisesRegex(ValueError, "must include a timezone"):
            parseUtcTimestamp("2026-01-01T00:00:00")


class DatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = createConnection(":memory:")
        initializeDatabase(self.connection)

    def tearDown(self) -> None:
        self.connection.close()

    def _insertIncident(
        self,
        connection: sqlite3.Connection | None = None,
        responsibleAreaId: str = "tecnologia",
        title: str = "Fallo de prueba",
        createdBy: str = "Operador",
    ) -> str:
        targetConnection = connection or self.connection
        incidentId = generateId()
        timestamp = formatUtcTimestamp(utcNow())
        targetConnection.execute(
            """
            INSERT INTO incidents (
                id, channelId, typeId, severityId, responsibleAreaId, statusId,
                title, description, createdAt, updatedAt, createdBy
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                incidentId,
                "email",
                "tecnologia",
                "media",
                responsibleAreaId,
                "nueva",
                title,
                "Descripción de prueba",
                timestamp,
                timestamp,
                createdBy,
            ),
        )
        return incidentId

    def testSchemaRejectsValuesOutsideValidatedCatalogs(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self._insertIncident(responsibleAreaId="direccionEjecutiva")

        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                """
                INSERT INTO incidents (
                    id, channelId, typeId, severityId, responsibleAreaId, statusId,
                    title, description, createdAt, updatedAt, createdBy
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    generateId(),
                    "fax",
                    "tecnologia",
                    "media",
                    "tecnologia",
                    "nueva",
                    "Canal inválido",
                    "",
                    formatUtcTimestamp(utcNow()),
                    formatUtcTimestamp(utcNow()),
                    "Operador",
                ),
            )

    def testSchemaRequiresUuid4Identifiers(self) -> None:
        timestamp = formatUtcTimestamp(utcNow())
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                """
                INSERT INTO incidents (
                    id, channelId, typeId, severityId, responsibleAreaId, statusId,
                    title, description, createdAt, updatedAt, createdBy
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "not-a-uuid",
                    "email",
                    "tecnologia",
                    "media",
                    "tecnologia",
                    "nueva",
                    "ID inválido",
                    "",
                    timestamp,
                    timestamp,
                    "Operador",
                ),
            )

    def testSchemaRejectsBlankTitle(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self._insertIncident(title=" ")

    def testSchemaRejectsBlankAuthor(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self._insertIncident(createdBy=" ")

    def testHistoryRequiresAnIncident(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                """
                INSERT INTO historyEvents (
                    id, incidentId, changeType, previousValue, newValue, author, createdAt
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    generateId(),
                    generateId(),
                    "estado",
                    "nueva",
                    "enCurso",
                    "Operador",
                    formatUtcTimestamp(utcNow()),
                ),
            )

    def testDatabasePersistsIncidentsAcrossConnections(self) -> None:
        with tempfile.TemporaryDirectory() as tempDirectory:
            databasePath = Path(tempDirectory) / "incidents.sqlite"
            connection = createConnection(databasePath)
            try:
                initializeDatabase(connection)
                incidentId = self._insertIncident(connection=connection)
                connection.commit()
            finally:
                connection.close()

            reopenedConnection = createConnection(databasePath)
            try:
                row = reopenedConnection.execute(
                    "SELECT id FROM incidents WHERE id = ?",
                    (incidentId,),
                ).fetchone()
                self.assertIsNotNone(row)
            finally:
                reopenedConnection.close()

    def testHistoryEventsCannotBeUpdatedOrDeleted(self) -> None:
        incidentId = self._insertIncident()
        eventId = generateId()
        self.connection.execute(
            """
            INSERT INTO historyEvents (
                id, incidentId, changeType, previousValue, newValue, author, createdAt
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                eventId,
                incidentId,
                "estado",
                "nueva",
                "enCurso",
                "Operador",
                formatUtcTimestamp(utcNow()),
            ),
        )

        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable"):
            self.connection.execute(
                "UPDATE historyEvents SET newValue = 'resuelta' WHERE id = ?",
                (eventId,),
            )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable"):
            self.connection.execute("DELETE FROM historyEvents WHERE id = ?", (eventId,))


if __name__ == "__main__":
    unittest.main()
