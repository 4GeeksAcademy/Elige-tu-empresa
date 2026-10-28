import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from services.api.database import createConnection
from services.api.inventory import registerMovement
from services.api.models import isUuid4
from services.api.server import createServer


class InventoryAPITestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporaryDirectory = tempfile.TemporaryDirectory()
        self.databasePath = Path(self.temporaryDirectory.name) / "incidents.sqlite"
        self.server = createServer(self.databasePath, port=0)
        self.serverThread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.serverThread.start()
        host, port = self.server.server_address
        self.baseUrl = f"http://{host}:{port}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.serverThread.join(timeout=2)
        self.temporaryDirectory.cleanup()

    def request(self, method: str, requestPath: str, payload: object | None = None) -> tuple[int, dict | list]:
        headers = {}
        rawBody = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            rawBody = json.dumps(payload).encode("utf-8")
        request = Request(f"{self.baseUrl}{requestPath}", data=rawBody, headers=headers, method=method)
        try:
            with urlopen(request, timeout=3) as response:
                body = response.read()
                return response.status, json.loads(body) if body else {}
        except HTTPError as error:
            body = error.read()
            return error.code, json.loads(body) if body else {}

    def itemFields(self, **overrides: object) -> dict:
        fields = {
            "name": "Jugo de lulo",
            "locationId": "queChille",
            "category": "beverages",
            "unitOfMeasure": "l",
            "reorderPoint": "10",
        }
        fields.update(overrides)
        return fields

    def createItem(self, **overrides: object) -> dict:
        statusCode, item = self.request("POST", "/api/inventory/items", self.itemFields(**overrides))
        self.assertEqual(statusCode, 201, item)
        return item

    def addMovement(self, itemId: str, quantity: str = "5") -> None:
        connection = createConnection(self.databasePath)
        try:
            registerMovement(
                connection, itemId, {"movementType": "inbound", "quantity": quantity, "reason": "delivery"}
            )
        finally:
            connection.close()


class InventoryItemRoutesTests(InventoryAPITestCase):
    def testInv010InventoryCatalogsEndpointReturnsCatalogs(self) -> None:
        statusCode, catalogValues = self.request("GET", "/api/inventory/catalogs")
        self.assertEqual(statusCode, 200)
        self.assertEqual(
            set(catalogValues), {"units", "categories", "movementTypes", "adjustmentReasons", "locations"}
        )
        self.assertEqual([entry["id"] for entry in catalogValues["locations"]], ["laArepita", "queChille", "theBigSauce", "chilliBeans"])
        self.assertEqual([entry["id"] for entry in catalogValues["movementTypes"]], ["inbound", "outbound", "adjustment"])
        _, incidentCatalogs = self.request("GET", "/api/catalogs")
        self.assertEqual(set(incidentCatalogs), {"channels", "incidentTypes", "severities", "responsibleAreas", "statuses"})

    def testInv001PostItemReturns201WithZeroStock(self) -> None:
        statusCode, item = self.request("POST", "/api/inventory/items", self.itemFields())
        self.assertEqual(statusCode, 201)
        self.assertTrue(isUuid4(item["id"]))
        self.assertEqual(
            (item["name"], item["locationId"], item["unitOfMeasure"], item["reorderPoint"], item["stock"]),
            ("Jugo de lulo", "queChille", "l", "10.000", "0.000"),
        )
        self.assertEqual(item["needsReorder"], True)
        self.assertEqual(item["expiredLots"], [])
        statusCode, fetched = self.request("GET", f"/api/inventory/items/{item['id']}")
        self.assertEqual((statusCode, fetched), (200, item))

    def testInv002PostItemWithInvalidValuesReturns400(self) -> None:
        for overrides in (
            {"name": "  "},
            {"locationId": "unknown"},
            {"category": "unknown"},
            {"unitOfMeasure": "lb"},
            {"reorderPoint": "-1"},
            {"reorderPoint": 10},
        ):
            with self.subTest(overrides=overrides):
                statusCode, body = self.request("POST", "/api/inventory/items", self.itemFields(**overrides))
                self.assertEqual(statusCode, 400)
                self.assertIn("error", body)
        fields = self.itemFields()
        del fields["name"]
        self.assertEqual(self.request("POST", "/api/inventory/items", fields)[0], 400)
        self.assertEqual(self.request("GET", "/api/inventory/items"), (200, []))

    def testInv010GetItemsFiltersByLocation(self) -> None:
        self.createItem(name="Cilantro", locationId="queChille")
        self.createItem(name="Servilletas", locationId="chilliBeans", category="packaging", unitOfMeasure="unit", reorderPoint="500")
        statusCode, everything = self.request("GET", "/api/inventory/items")
        self.assertEqual((statusCode, len(everything)), (200, 2))
        statusCode, filtered = self.request("GET", "/api/inventory/items?locationId=chilliBeans")
        self.assertEqual((statusCode, [item["name"] for item in filtered]), (200, ["Servilletas"]))
        self.assertEqual(self.request("GET", "/api/inventory/items?locationId=laArepita"), (200, []))
        self.assertEqual(self.request("GET", "/api/inventory/items?locationId=unknown")[0], 404)
        self.assertEqual(self.request("GET", "/api/inventory/items?locationId=queChille&locationId=chilliBeans")[0], 400)
        self.assertEqual(self.request("GET", "/api/inventory/items?stock=5")[0], 400)

    def testInv009UnknownItemReturns404(self) -> None:
        unknownId = "7d6b2a56-2f4e-4a2b-9a58-2c2f8a1f0e11"
        for itemId in (unknownId, "not-a-uuid"):
            for method, payload in (("GET", None), ("PATCH", {"name": "Otro"}), ("DELETE", None)):
                with self.subTest(itemId=itemId, method=method):
                    statusCode, body = self.request(method, f"/api/inventory/items/{itemId}", payload)
                    self.assertEqual(statusCode, 404)
                    self.assertIn("error", body)

    def testInv038StockFieldReturns400(self) -> None:
        item = self.createItem()
        for fieldName in ("stock", "quantity", "stockMilli"):
            with self.subTest(fieldName=fieldName):
                statusCode, body = self.request("POST", "/api/inventory/items", self.itemFields(**{fieldName: "5"}))
                self.assertEqual(statusCode, 400)
                self.assertIn("Unsupported", body["error"])
                statusCode, body = self.request("PATCH", f"/api/inventory/items/{item['id']}", {fieldName: "5"})
                self.assertEqual(statusCode, 400)
        self.assertEqual(self.request("GET", f"/api/inventory/items/{item['id']}")[1]["stock"], "0.000")

    def testInv007DeleteItemWithoutMovementsReturns200(self) -> None:
        item = self.createItem()
        statusCode, body = self.request("DELETE", f"/api/inventory/items/{item['id']}")
        self.assertEqual((statusCode, body), (200, {"deleted": item["id"]}))
        self.assertEqual(self.request("GET", f"/api/inventory/items/{item['id']}")[0], 404)
        self.assertEqual(self.request("GET", "/api/inventory/items"), (200, []))

    def testInv008DeleteItemWithMovementsReturns409(self) -> None:
        item = self.createItem()
        self.addMovement(item["id"])
        statusCode, body = self.request("DELETE", f"/api/inventory/items/{item['id']}")
        self.assertEqual(statusCode, 409)
        self.assertIn("error", body)
        self.assertEqual(self.request("GET", f"/api/inventory/items/{item['id']}")[1]["stock"], "5.000")

    def testInv006PatchStructuralFieldWithMovementsReturns409(self) -> None:
        item = self.createItem()
        self.addMovement(item["id"])
        for changes in ({"locationId": "laArepita"}, {"category": "packaging"}, {"unitOfMeasure": "ml"}):
            with self.subTest(changes=changes):
                statusCode, body = self.request("PATCH", f"/api/inventory/items/{item['id']}", changes)
                self.assertEqual(statusCode, 409)
                self.assertIn("error", body)
        statusCode, updated = self.request(
            "PATCH", f"/api/inventory/items/{item['id']}", {"name": "Jugo de lulo 1 l", "reorderPoint": "12.5"}
        )
        self.assertEqual((statusCode, updated["name"], updated["reorderPoint"], updated["stock"]), (200, "Jugo de lulo 1 l", "12.500", "5.000"))
        other = self.createItem(name="Sin movimientos")
        statusCode, moved = self.request("PATCH", f"/api/inventory/items/{other['id']}", {"locationId": "laArepita"})
        self.assertEqual((statusCode, moved["locationId"]), (200, "laArepita"))

    def testInv037NoRouteWritesStock(self) -> None:
        item = self.createItem()
        stockPaths = ("/api/inventory/stock", f"/api/inventory/items/{item['id']}/stock", f"/api/inventory/items/{item['id']}/stockMilli")
        for method in ("POST", "PATCH", "PUT", "DELETE"):
            for stockPath in stockPaths:
                with self.subTest(method=method, path=stockPath):
                    statusCode, _ = self.request(method, stockPath, {"stock": "99"})
                    self.assertIn(statusCode, (404, 405))
        self.assertEqual(self.request("PUT", f"/api/inventory/items/{item['id']}", self.itemFields())[0], 405)
        self.assertEqual(self.request("GET", f"/api/inventory/items/{item['id']}")[1]["stock"], "0.000")

    def testDeleteOnIncidentRoutesStillReturns405(self) -> None:
        self.assertEqual(self.request("DELETE", "/api/incidents/7d6b2a56-2f4e-4a2b-9a58-2c2f8a1f0e11")[0], 405)
        self.assertEqual(self.request("DELETE", "/")[0], 405)


if __name__ == "__main__":
    unittest.main()
