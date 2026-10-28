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


class SeedExpiredLotTests(SeedTestCase):
    def cilantro(self) -> dict:
        return [item for item in listItems(self.connection, now=self.fixedNow) if item["name"] == "Cilantro"][0]

    def lotRows(self, itemId: str) -> list:
        return self.connection.execute(
            "SELECT * FROM inventoryLots WHERE itemId = ? ORDER BY expiryDate", (itemId,)
        ).fetchall()

    def testInv064CilantroHasExpiredLotWithStock(self) -> None:
        loadInventorySeed(self.connection, now=self.fixedNow)
        item = self.cilantro()
        expired = [lot for lot in self.lotRows(item["id"]) if lot["expiryDate"] == "2026-10-01"]
        self.assertEqual(len(expired), 1)
        self.assertEqual(item["locationId"], "queChille")
        lotStock = calculateStock(self.connection, itemId=item["id"], groupByLot=True)[(item["id"], expired[0]["lotCode"])]
        self.assertGreater(lotStock, 0)
        self.assertEqual(
            [(lot["lotCode"], lot["expiryDate"]) for lot in item["expiredLots"]],
            [(expired[0]["lotCode"], "2026-10-01")],
        )
        self.assertFalse(item["needsReorder"])

    def testInv064CilantroOutboundUsesNonExpiredLot(self) -> None:
        loadInventorySeed(self.connection, now=self.fixedNow)
        item = self.cilantro()
        outbounds = self.connection.execute(
            "SELECT lotCode FROM stockMovements WHERE itemId = ? AND movementType = 'outbound'", (item["id"],)
        ).fetchall()
        self.assertTrue(outbounds)
        expiryByLot = {lot["lotCode"]: lot["expiryDate"] for lot in self.lotRows(item["id"])}
        self.assertEqual(len(expiryByLot), 2)
        for outbound in outbounds:
            self.assertGreater(expiryByLot[outbound["lotCode"]], "2026-10-28")

    def testInv065OtherSeedLotsExpireAfterLoadDay(self) -> None:
        loadInventorySeed(self.connection, now=self.fixedNow)
        lots = self.connection.execute("SELECT lotCode, expiryDate, itemId FROM inventoryLots").fetchall()
        self.assertGreater(len(lots), 8)
        cilantroId = self.cilantro()["id"]
        others = [lot for lot in lots if lot["expiryDate"] != "2026-10-01"]
        self.assertEqual(len(lots) - len(others), 1)
        for lot in others:
            with self.subTest(lotCode=lot["lotCode"]):
                self.assertGreater(lot["expiryDate"], "2026-10-28")
        self.assertIn(cilantroId, {lot["itemId"] for lot in others})

    def testInv065LotDatesFollowTheLoadDay(self) -> None:
        later = datetime(2027, 3, 1, 8, 0, 0, tzinfo=timezone.utc)
        loadInventorySeed(self.connection, now=later)
        expiryDates = sorted(row["expiryDate"] for row in self.connection.execute("SELECT expiryDate FROM inventoryLots"))
        self.assertEqual(expiryDates[0], "2026-10-01")
        self.assertTrue(all(expiryDate > "2027-03-01" for expiryDate in expiryDates[1:]))


if __name__ == "__main__":
    unittest.main()
