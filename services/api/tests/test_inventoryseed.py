import unittest
from datetime import datetime, timezone
from unittest import mock

from services.api import inventory
from services.api.database import createConnection, initializeDatabase
from services.api.inventory import calculateStock, listItems
from services.api.inventoryseed import loadInventorySeed

expectedItems = (
    ("laArepita", "Punta de anca de res", "meat", "kg", "20.000"),
    ("laArepita", "Pechuga de pollo", "meat", "kg", "15.000"),
    ("laArepita", "Cebolla cabezona", "produce", "kg", "10.000"),
    ("laArepita", "Salsa de ajo de la casa", "sauces_condiments", "l", "5.000"),
    ("queChille", "Costilla de cerdo", "meat", "kg", "12.000"),
    ("queChille", "Cilantro", "produce", "kg", "2.000"),
    ("queChille", "Jugo de lulo", "beverages", "l", "10.000"),
    ("queChille", "Desengrasante", "cleaning_supplies", "l", "4.000"),
    ("theBigSauce", "Brisket de res", "meat", "kg", "25.000"),
    ("theBigSauce", "Salsa BBQ de la casa", "sauces_condiments", "l", "8.000"),
    ("theBigSauce", "Refresco de cola", "beverages", "unit", "48"),
    ("theBigSauce", "Envases para llevar", "packaging", "unit", "200"),
    ("chilliBeans", "Alitas de pollo", "meat", "kg", "18.000"),
    ("chilliBeans", "Jalapeños", "produce", "kg", "3.000"),
    ("chilliBeans", "Servilletas", "packaging", "unit", "500"),
    ("chilliBeans", "Desinfectante", "cleaning_supplies", "l", "5.000"),
)


class SeedTestCase(unittest.TestCase):
    fixedNow = datetime(2026, 10, 28, 12, 0, 0, tzinfo=timezone.utc)

    def setUp(self) -> None:
        self.connection = createConnection(":memory:")
        initializeDatabase(self.connection)
        self.addCleanup(self.connection.close)

    def itemKey(self, item: dict) -> tuple:
        return (item["locationId"], item["name"], item["category"], item["unitOfMeasure"], item["reorderPoint"])


class SeedItemsTests(SeedTestCase):
    def testInv059SeedCreatesSixteenItemsWithDeclaredFields(self) -> None:
        loadInventorySeed(self.connection, now=self.fixedNow)
        items = listItems(self.connection, now=self.fixedNow)
        self.assertEqual(len(items), 16)
        self.assertEqual({self.itemKey(item) for item in items}, set(expectedItems))
        for locationId in ("laArepita", "queChille", "theBigSauce", "chilliBeans"):
            self.assertEqual(len(listItems(self.connection, locationId, now=self.fixedNow)), 4)
        self.assertEqual(len({item["category"] for item in items}), 6)

    def testInv060SeedStockComesOnlyFromMovements(self) -> None:
        with mock.patch(
            "services.api.inventoryseed.registerMovement", wraps=inventory.registerMovement
        ) as registerSpy, mock.patch(
            "services.api.inventoryseed.createItem", wraps=inventory.createItem
        ) as createSpy:
            loadInventorySeed(self.connection, now=self.fixedNow)
        movementCount = self.connection.execute("SELECT COUNT(*) FROM stockMovements").fetchone()[0]
        self.assertEqual(createSpy.call_count, 16)
        self.assertEqual(registerSpy.call_count, movementCount)
        self.assertGreaterEqual(movementCount, 48)
        signed = {
            row["itemId"]: row["total"]
            for row in self.connection.execute(
                """
                SELECT itemId, SUM(CASE movementType WHEN 'outbound' THEN -quantityMilli ELSE quantityMilli END) AS total
                FROM stockMovements GROUP BY itemId
                """
            )
        }
        self.assertEqual(signed, calculateStock(self.connection))
        self.assertTrue(all(total > 0 for total in signed.values()))

    def testInv061EverySeedItemHasInboundOutboundAndAdjustment(self) -> None:
        loadInventorySeed(self.connection, now=self.fixedNow)
        typesByItem: dict[str, set[str]] = {}
        for row in self.connection.execute("SELECT itemId, movementType FROM stockMovements"):
            typesByItem.setdefault(row["itemId"], set()).add(row["movementType"])
        self.assertEqual(len(typesByItem), 16)
        for itemId, movementTypes in typesByItem.items():
            with self.subTest(itemId=itemId):
                self.assertEqual(movementTypes, {"inbound", "outbound", "adjustment"})

    def testInv062SeedAdjustmentsIncludeAllThreeReasons(self) -> None:
        loadInventorySeed(self.connection, now=self.fixedNow)
        reasons = {
            row["reason"]
            for row in self.connection.execute("SELECT reason FROM stockMovements WHERE movementType = 'adjustment'")
        }
        self.assertEqual(reasons, {"waste", "theft", "count_correction"})

    def testInv063OnlyGarlicSauceAndTakeawayContainersAreAtOrBelowReorderPoint(self) -> None:
        loadInventorySeed(self.connection, now=self.fixedNow)
        items = listItems(self.connection, now=self.fixedNow)
        marked = {(item["locationId"], item["name"]) for item in items if item["needsReorder"]}
        self.assertEqual(
            marked,
            {("laArepita", "Salsa de ajo de la casa"), ("theBigSauce", "Envases para llevar")},
        )
        self.assertEqual(len([item for item in items if not item["needsReorder"]]), 14)


if __name__ == "__main__":
    unittest.main()
