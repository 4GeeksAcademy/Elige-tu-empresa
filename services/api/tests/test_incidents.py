import unittest

from services.api.database import createConnection, initializeDatabase
from services.api.incidents import registerIncident
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


if __name__ == "__main__":
    unittest.main()
