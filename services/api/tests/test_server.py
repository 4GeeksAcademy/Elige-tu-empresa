import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from services.api.server import createServer


class IncidentHTTPServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporaryDirectory = tempfile.TemporaryDirectory()
        databasePath = Path(self.temporaryDirectory.name) / "incidents.sqlite"
        self.server = createServer(databasePath, port=0)
        self.serverThread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True,
        )
        self.serverThread.start()
        host, port = self.server.server_address
        self.baseUrl = f"http://{host}:{port}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.serverThread.join(timeout=2)
        self.temporaryDirectory.cleanup()

    def _request(
        self,
        method: str,
        requestPath: str,
        payload: dict | None = None,
        headers: dict | None = None,
        rawBody: bytes | None = None,
    ) -> tuple[int, dict[str, str], bytes]:
        requestHeaders = headers or {}
        if payload is not None:
            requestHeaders = {
                **requestHeaders,
                "Content-Type": "application/json",
            }
            rawBody = json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.baseUrl}{requestPath}",
            data=rawBody,
            headers=requestHeaders,
            method=method,
        )
        try:
            with urlopen(request, timeout=3) as response:
                return response.status, dict(response.headers.items()), response.read()
        except HTTPError as error:
            return error.code, dict(error.headers.items()), error.read()

    def _requestJson(
        self,
        method: str,
        requestPath: str,
        payload: dict | None = None,
        headers: dict | None = None,
        rawBody: bytes | None = None,
    ) -> tuple[int, dict]:
        statusCode, _, responseBody = self._request(
            method,
            requestPath,
            payload,
            headers=headers,
            rawBody=rawBody,
        )
        return statusCode, json.loads(responseBody) if responseBody else {}

    def testServesBackofficeAndStaticAssets(self) -> None:
        statusCode, headers, page = self._request("GET", "/")
        self.assertEqual(statusCode, 200)
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn(b"Registrar incidencia", page)

        statusCode, headers, script = self._request("GET", "/app.js")
        self.assertEqual(statusCode, 200)
        self.assertIn("javascript", headers["Content-Type"])
        self.assertIn(b"/incidents/summary/by-severity", script)

        statusCode, _, style = self._request("GET", "/styles.css")
        self.assertEqual(statusCode, 200)
        self.assertIn(b"summaryGrid", style)

    def testIncidentHTTPWorkflowAndSummary(self) -> None:
        statusCode, catalogValues = self._requestJson("GET", "/api/catalogs")
        self.assertEqual(statusCode, 200)
        self.assertEqual(catalogValues["channels"][0]["id"], "whatsapp")
        self.assertEqual(catalogValues["responsibleAreas"][-1]["assignable"], False)

        statusCode, incident = self._requestJson(
            "POST",
            "/api/incidents",
            {
                "channelId": "whatsapp",
                "typeId": "operacionRestaurante",
                "severityId": "critica",
                "responsibleAreaId": "tecnologia",
                "title": "Incidencia desde HTTP",
                "description": "Prueba del contrato HTTP.",
                "createdBy": "Operadora HTTP",
            },
        )
        self.assertEqual(statusCode, 201)
        incidentId = incident["id"]
        self.assertEqual(incident["statusId"], "nueva")
        self.assertTrue(incident["createdAt"].endswith("Z"))

        statusCode, filteredIncidents = self._requestJson(
            "GET",
            "/api/incidents?severityId=critica&responsibleAreaId=tecnologia",
        )
        self.assertEqual(statusCode, 200)
        self.assertEqual(tuple(item["id"] for item in filteredIncidents), (incidentId,))

        statusCode, error = self._requestJson(
            "PATCH",
            f"/api/incidents/{incidentId}/status",
            {"statusId": "cerrada", "author": "Operadora HTTP"},
        )
        self.assertEqual(statusCode, 400)
        self.assertIn("not allowed", error["error"])

        statusCode, incident = self._requestJson(
            "PATCH",
            f"/api/incidents/{incidentId}/area",
            {
                "responsibleAreaId": "comprasProveedores",
                "author": "Supervisora HTTP",
            },
        )
        self.assertEqual(statusCode, 200)
        self.assertEqual(incident["responsibleAreaId"], "comprasProveedores")

        for statusId in ("enCurso", "resuelta"):
            statusCode, incident = self._requestJson(
                "PATCH",
                f"/api/incidents/{incidentId}/status",
                {"statusId": statusId, "author": "Operadora HTTP"},
            )
            self.assertEqual(statusCode, 200)
            self.assertEqual(incident["statusId"], statusId)

        statusCode, summary = self._requestJson(
            "GET",
            "/api/incidents/summary/by-severity",
        )
        self.assertEqual(statusCode, 200)
        self.assertEqual(
            summary,
            {"critica": 1, "alta": 0, "media": 0, "baja": 0},
        )

        statusCode, details = self._requestJson(
            "GET",
            f"/api/incidents/{incidentId}",
        )
        self.assertEqual(statusCode, 200)
        self.assertEqual(details["incident"]["statusId"], "resuelta")
        self.assertEqual(
            tuple(event["changeType"] for event in details["historyEvents"]),
            ("areaResponsable", "estado", "estado"),
        )
        self.assertEqual(details["historyEvents"][0]["author"], "Supervisora HTTP")
        self.assertTrue(details["historyEvents"][0]["createdAt"].endswith("Z"))

        statusCode, incident = self._requestJson(
            "PATCH",
            f"/api/incidents/{incidentId}/status",
            {"statusId": "cerrada", "author": "Operadora HTTP"},
        )
        self.assertEqual(statusCode, 200)
        self.assertEqual(incident["statusId"], "cerrada")

        statusCode, summary = self._requestJson(
            "GET",
            "/api/incidents/summary/by-severity",
        )
        self.assertEqual(statusCode, 200)
        self.assertEqual(summary["critica"], 0)

    def testRejectsInvalidFiltersPayloadsAndUnknownIncidents(self) -> None:
        statusCode, error = self._requestJson(
            "GET",
            "/api/incidents?severityId=unknown",
        )
        self.assertEqual(statusCode, 400)
        self.assertIn("severityId", error["error"])

        statusCode, error = self._requestJson(
            "POST",
            "/api/incidents",
            {"channelId": "email"},
        )
        self.assertEqual(statusCode, 400)
        self.assertIn("Missing required fields", error["error"])

        statusCode, error = self._requestJson(
            "GET",
            "/api/incidents/invalid-id",
        )
        self.assertEqual(statusCode, 404)
        self.assertIn("not found", error["error"].lower())

        statusCode, error = self._requestJson("GET", "/api/unknown")
        self.assertEqual(statusCode, 404)
        self.assertEqual(error["error"], "API route not found")

    def testRejectsMalformedJsonAndUnsupportedContentType(self) -> None:
        statusCode, error = self._requestJson(
            "POST",
            "/api/incidents",
            headers={"Content-Type": "text/plain"},
            rawBody=b"{}",
        )
        self.assertEqual(statusCode, 415)
        self.assertIn("Content-Type", error["error"])

        statusCode, error = self._requestJson(
            "POST",
            "/api/incidents",
            headers={"Content-Type": "application/json"},
            rawBody=b"{",
        )
        self.assertEqual(statusCode, 400)
        self.assertTrue(error["error"])

    def testStaticFilesCannotEscapeTheirRoot(self) -> None:
        statusCode, error = self._requestJson("GET", "/%2e%2e/pyproject.toml")
        self.assertEqual(statusCode, 404)
        self.assertEqual(error["error"], "File not found")


if __name__ == "__main__":
    unittest.main()
