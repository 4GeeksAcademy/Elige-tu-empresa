import sqlite3
import unittest

from services.api.database import createConnection, initializeDatabase
from services.api.incidents import (
    changeIncidentStatus,
    getIncidentDetails,
    getOpenIncidentCountsBySeverity,
    listIncidents,
    reassignIncidentArea,
    registerIncident,
)
from services.api.models import isUuid4, parseUtcTimestamp


class RegisterIncidentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = createConnection(":memory:")
        initializeDatabase(self.connection)

    def tearDown(self) -> None:
        self.connection.close()

    def _registerIncident(self, **overrides: str):
        values = {
            "channelId": "email",
            "typeId": "tecnologia",
            "severityId": "media",
            "responsibleAreaId": "tecnologia",
            "title": "Fallo del punto de venta",
            "description": "El sistema no inicia.",
            "createdBy": "Operadora de prueba",
        }
        values.update(overrides)
        return registerIncident(self.connection, **values)

    def testRegistersIncidentWithApprovedValuesAndInitialStatus(self) -> None:
        incident = self._registerIncident(
            channelId="whatsapp",
            typeId="operacionRestaurante",
            severityId="alta",
            responsibleAreaId="operacionesRestaurante",
        )
        storedIncident = self.connection.execute(
            "SELECT * FROM incidents WHERE id = ?",
            (incident.id,),
        ).fetchone()

        self.assertIsNotNone(storedIncident)
        self.assertTrue(isUuid4(incident.id))
        self.assertEqual(storedIncident["channelId"], "whatsapp")
        self.assertEqual(storedIncident["typeId"], "operacionRestaurante")
        self.assertEqual(storedIncident["severityId"], "alta")
        self.assertEqual(storedIncident["responsibleAreaId"], "operacionesRestaurante")
        self.assertEqual(storedIncident["statusId"], "nueva")
        self.assertEqual(storedIncident["createdBy"], "Operadora de prueba")
        self.assertEqual(
            parseUtcTimestamp(storedIncident["createdAt"]),
            incident.createdAt,
        )
        self.assertEqual(storedIncident["createdAt"], storedIncident["updatedAt"])

    def testEveryApprovedChannelCanBeRegistered(self) -> None:
        for channelId in ("whatsapp", "telefono", "email"):
            with self.subTest(channelId=channelId):
                incident = self._registerIncident(channelId=channelId)
                self.assertEqual(incident.channelId, channelId)

    def testEveryAssignableAreaCanBeAssigned(self) -> None:
        areaIds = (
            "operacionesRestaurante",
            "comprasProveedores",
            "marketingExperienciaDigital",
            "personasCultura",
            "formacionEstandaresCalidad",
            "tecnologia",
        )
        for responsibleAreaId in areaIds:
            with self.subTest(responsibleAreaId=responsibleAreaId):
                incident = self._registerIncident(
                    responsibleAreaId=responsibleAreaId
                )
                self.assertEqual(incident.responsibleAreaId, responsibleAreaId)

    def testRegistrationRejectsValuesOutsideCatalogs(self) -> None:
        invalidValues = (
            ("channelId", "fax"),
            ("typeId", "otro"),
            ("severityId", "urgente"),
            ("responsibleAreaId", "direccionEjecutiva"),
            ("responsibleAreaId", "areaDesconocida"),
        )
        for fieldName, value in invalidValues:
            with self.subTest(fieldName=fieldName, value=value):
                with self.assertRaisesRegex(ValueError, fieldName):
                    self._registerIncident(**{fieldName: value})

        incidentCount = self.connection.execute(
            "SELECT COUNT(*) FROM incidents"
        ).fetchone()[0]
        self.assertEqual(incidentCount, 0)

    def testRegistrationRequiresTitleAndAuthor(self) -> None:
        with self.assertRaisesRegex(ValueError, "title"):
            self._registerIncident(title="  ")
        with self.assertRaisesRegex(ValueError, "createdBy"):
            self._registerIncident(createdBy=" ")

        incidentCount = self.connection.execute(
            "SELECT COUNT(*) FROM incidents"
        ).fetchone()[0]
        self.assertEqual(incidentCount, 0)

    def testRegistrationRequiresTextDescription(self) -> None:
        with self.assertRaisesRegex(ValueError, "description"):
            self._registerIncident(description=123)

    def testRegistrationPersistsBeforeReturning(self) -> None:
        incident = self._registerIncident()

        self.assertIsNotNone(
            self.connection.execute(
                "SELECT id FROM incidents WHERE id = ?",
                (incident.id,),
            ).fetchone()
        )

    def testCreationDoesNotCreateChangeHistoryEvents(self) -> None:
        incident = self._registerIncident()
        historyCount = self.connection.execute(
            "SELECT COUNT(*) FROM historyEvents WHERE incidentId = ?",
            (incident.id,),
        ).fetchone()[0]

        self.assertEqual(historyCount, 0)

    def testStatusTransitionsFollowTheApprovedLifecycle(self) -> None:
        incident = self._registerIncident()
        incident = changeIncidentStatus(
            self.connection, incident.id, "enCurso", "Operadora"
        )
        self.assertEqual(incident.statusId, "enCurso")

        incident = changeIncidentStatus(
            self.connection, incident.id, "resuelta", "Operadora"
        )
        self.assertEqual(incident.statusId, "resuelta")

        incident = changeIncidentStatus(
            self.connection, incident.id, "enCurso", "Operadora"
        )
        self.assertEqual(incident.statusId, "enCurso")

        incident = changeIncidentStatus(
            self.connection, incident.id, "resuelta", "Operadora"
        )
        incident = changeIncidentStatus(
            self.connection, incident.id, "cerrada", "Operadora"
        )
        self.assertEqual(incident.statusId, "cerrada")

    def testInvalidStatusTransitionsAreRejectedWithoutHistory(self) -> None:
        incident = self._registerIncident()

        with self.assertRaisesRegex(ValueError, "not allowed"):
            changeIncidentStatus(
                self.connection, incident.id, "resuelta", "Operadora"
            )

        incident = changeIncidentStatus(
            self.connection, incident.id, "enCurso", "Operadora"
        )
        incident = changeIncidentStatus(
            self.connection, incident.id, "resuelta", "Operadora"
        )
        incident = changeIncidentStatus(
            self.connection, incident.id, "cerrada", "Operadora"
        )
        with self.assertRaisesRegex(ValueError, "not allowed"):
            changeIncidentStatus(
                self.connection, incident.id, "enCurso", "Operadora"
            )

        details = getIncidentDetails(self.connection, incident.id)
        self.assertEqual(details.incident.statusId, "cerrada")
        self.assertEqual(
            tuple(event.newValue for event in details.historyEvents),
            ("enCurso", "resuelta", "cerrada"),
        )

    def testStatusAndAreaChangesRollbackWhenHistoryInsertFails(self) -> None:
        incident = self._registerIncident()
        self.connection.execute(
            """
            CREATE TRIGGER rejectHistoryInsert
            BEFORE INSERT ON historyEvents
            BEGIN
                SELECT RAISE(ABORT, 'history insert rejected');
            END
            """
        )

        with self.assertRaisesRegex(sqlite3.IntegrityError, "history insert rejected"):
            changeIncidentStatus(
                self.connection, incident.id, "enCurso", "Operadora"
            )

        self.connection.execute("DROP TRIGGER rejectHistoryInsert")
        changeIncidentStatus(
            self.connection, incident.id, "enCurso", "Operadora"
        )
        self.connection.execute(
            """
            CREATE TRIGGER rejectHistoryInsert
            BEFORE INSERT ON historyEvents
            BEGIN
                SELECT RAISE(ABORT, 'history insert rejected');
            END
            """
        )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "history insert rejected"):
            reassignIncidentArea(
                self.connection,
                incident.id,
                "comprasProveedores",
                "Supervisora",
            )

        storedIncident = self.connection.execute(
            "SELECT statusId, responsibleAreaId FROM incidents WHERE id = ?",
            (incident.id,),
        ).fetchone()
        eventRows = self.connection.execute(
            "SELECT changeType FROM historyEvents WHERE incidentId = ?",
            (incident.id,),
        ).fetchall()
        self.assertEqual(storedIncident["statusId"], "enCurso")
        self.assertEqual(storedIncident["responsibleAreaId"], "tecnologia")
        self.assertEqual(tuple(row["changeType"] for row in eventRows), ("estado",))

    def testAreaReassignmentAndStatusChangesAppearInIncidentDetails(self) -> None:
        incident = self._registerIncident()
        changeIncidentStatus(self.connection, incident.id, "enCurso", "Operadora")
        reassignedIncident = reassignIncidentArea(
            self.connection,
            incident.id,
            "comprasProveedores",
            "Supervisora",
        )
        details = getIncidentDetails(self.connection, incident.id)

        self.assertEqual(reassignedIncident.responsibleAreaId, "comprasProveedores")
        self.assertEqual(details.incident.responsibleAreaId, "comprasProveedores")
        self.assertEqual(
            tuple(event.changeType for event in details.historyEvents),
            ("estado", "areaResponsable"),
        )
        self.assertEqual(
            tuple(
                (event.previousValue, event.newValue)
                for event in details.historyEvents
            ),
            (("nueva", "enCurso"), ("tecnologia", "comprasProveedores")),
        )
        self.assertEqual(
            tuple(event.author for event in details.historyEvents),
            ("Operadora", "Supervisora"),
        )
        self.assertTrue(
            all(
                event.createdAt.tzinfo is not None
                and event.createdAt.utcoffset().total_seconds() == 0
                for event in details.historyEvents
            )
        )

    def testAreaReassignmentRejectsInvalidAreaAndBlankAuthor(self) -> None:
        incident = self._registerIncident()

        with self.assertRaisesRegex(ValueError, "responsibleAreaId"):
            reassignIncidentArea(
                self.connection,
                incident.id,
                "direccionEjecutiva",
                "Operadora",
            )
        with self.assertRaisesRegex(ValueError, "author"):
            reassignIncidentArea(
                self.connection,
                incident.id,
                "comprasProveedores",
                " ",
            )

        details = getIncidentDetails(self.connection, incident.id)
        self.assertEqual(details.incident.responsibleAreaId, "tecnologia")
        self.assertEqual(details.historyEvents, ())

    def testChangesRejectMissingIncidentAndNoOpValues(self) -> None:
        incident = self._registerIncident()

        with self.assertRaisesRegex(LookupError, "Incident not found"):
            changeIncidentStatus(
                self.connection,
                "00000000-0000-4000-8000-000000000000",
                "enCurso",
                "Operadora",
            )
        with self.assertRaisesRegex(ValueError, "already set"):
            reassignIncidentArea(
                self.connection,
                incident.id,
                "tecnologia",
                "Operadora",
            )

    def testIncidentDetailsRejectUnknownIncident(self) -> None:
        with self.assertRaisesRegex(LookupError, "Incident not found"):
            getIncidentDetails(
                self.connection,
                "00000000-0000-4000-8000-000000000000",
            )

    def testListsIncidentsWithEachFilterAndCombinedFilters(self) -> None:
        defaultIncident = self._registerIncident()
        highSeverityIncident = self._registerIncident(
            severityId="alta",
            responsibleAreaId="comprasProveedores",
        )
        criticalIncident = self._registerIncident(
            severityId="critica",
            responsibleAreaId="operacionesRestaurante",
        )
        changeIncidentStatus(
            self.connection,
            highSeverityIncident.id,
            "enCurso",
            "Operadora",
        )
        changeIncidentStatus(
            self.connection,
            criticalIncident.id,
            "enCurso",
            "Operadora",
        )

        self.assertEqual(
            tuple(incident.id for incident in listIncidents(self.connection)),
            (criticalIncident.id, highSeverityIncident.id, defaultIncident.id),
        )
        self.assertEqual(
            tuple(
                incident.id
                for incident in listIncidents(self.connection, statusId="enCurso")
            ),
            (criticalIncident.id, highSeverityIncident.id),
        )
        self.assertEqual(
            tuple(
                incident.id
                for incident in listIncidents(self.connection, severityId="alta")
            ),
            (highSeverityIncident.id,),
        )
        self.assertEqual(
            tuple(
                incident.id
                for incident in listIncidents(
                    self.connection,
                    responsibleAreaId="operacionesRestaurante",
                )
            ),
            (criticalIncident.id,),
        )
        self.assertEqual(
            tuple(
                incident.id
                for incident in listIncidents(
                    self.connection,
                    statusId="enCurso",
                    severityId="alta",
                    responsibleAreaId="comprasProveedores",
                )
            ),
            (highSeverityIncident.id,),
        )

    def testIncidentListRejectsFiltersOutsideApprovedCatalogs(self) -> None:
        invalidFilters = (
            ("statusId", "unknown"),
            ("severityId", "urgente"),
            ("responsibleAreaId", "direccionEjecutiva"),
            ("responsibleAreaId", "unknown"),
        )

        for fieldName, value in invalidFilters:
            with self.subTest(fieldName=fieldName, value=value):
                with self.assertRaisesRegex(ValueError, fieldName):
                    listIncidents(self.connection, **{fieldName: value})

    def testOpenIncidentCountsIncludeEverySeverityAndExcludeClosedIncidents(self) -> None:
        self.assertEqual(
            getOpenIncidentCountsBySeverity(self.connection),
            {"critica": 0, "alta": 0, "media": 0, "baja": 0},
        )

        criticalIncident = self._registerIncident(severityId="critica")
        highIncident = self._registerIncident(severityId="alta")
        mediumIncident = self._registerIncident(severityId="media")
        lowIncident = self._registerIncident(severityId="baja")
        closedIncident = self._registerIncident(severityId="critica")

        for incident in (highIncident, mediumIncident, lowIncident, closedIncident):
            changeIncidentStatus(
                self.connection,
                incident.id,
                "enCurso",
                "Operadora",
            )
        changeIncidentStatus(
            self.connection,
            mediumIncident.id,
            "resuelta",
            "Operadora",
        )
        for incident in (lowIncident, closedIncident):
            changeIncidentStatus(
                self.connection,
                incident.id,
                "resuelta",
                "Operadora",
            )
            changeIncidentStatus(
                self.connection,
                incident.id,
                "cerrada",
                "Operadora",
            )

        self.assertEqual(
            getOpenIncidentCountsBySeverity(self.connection),
            {"critica": 1, "alta": 1, "media": 1, "baja": 0},
        )


if __name__ == "__main__":
    unittest.main()
