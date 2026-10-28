import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from services.api import inventory
from services.api.database import createConnection, initializeDatabase
from services.api.inventory import BusinessRuleError, calculateStock, createItem, listItems
from services.api.inventoryseed import loadInventorySeed, main

repositoryRoot = Path(__file__).resolve().parents[3]

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


class SeedGuardTests(SeedTestCase):
    def counts(self) -> dict:
        return {
            tableName: self.connection.execute(f"SELECT COUNT(*) FROM {tableName}").fetchone()[0]
            for tableName in ("inventoryItems", "inventoryLots", "stockMovements")
        }

    def testInv066SeedRejectedWhenItemsExist(self) -> None:
        createItem(
            self.connection,
            {"name": "Jugo de lulo", "locationId": "queChille", "category": "beverages", "unitOfMeasure": "l", "reorderPoint": "10"},
            now=self.fixedNow,
        )
        with self.assertRaisesRegex(BusinessRuleError, "already"):
            loadInventorySeed(self.connection, now=self.fixedNow)
        self.assertEqual(self.counts(), {"inventoryItems": 1, "inventoryLots": 0, "stockMovements": 0})
        self.assertFalse(self.connection.in_transaction)

    def testInv066RejectedSeedChangesNothing(self) -> None:
        loadInventorySeed(self.connection, now=self.fixedNow)
        before = self.counts()
        stockBefore = calculateStock(self.connection)
        with self.assertRaises(BusinessRuleError):
            loadInventorySeed(self.connection, now=self.fixedNow)
        self.assertEqual(self.counts(), before)
        self.assertEqual(calculateStock(self.connection), stockBefore)

    def testInv059SeedIsAtomicWhenAMovementFails(self) -> None:
        calls = []

        def failingRegisterMovement(*arguments: object, **keywords: object) -> dict:
            calls.append(1)
            if len(calls) == 20:
                raise RuntimeError("simulated failure")
            return inventory.registerMovement(*arguments, **keywords)

        with mock.patch("services.api.inventoryseed.registerMovement", failingRegisterMovement):
            with self.assertRaisesRegex(RuntimeError, "simulated"):
                loadInventorySeed(self.connection, now=self.fixedNow)
        self.assertGreaterEqual(len(calls), 20)
        self.assertEqual(self.counts(), {"inventoryItems": 0, "inventoryLots": 0, "stockMovements": 0})
        self.assertFalse(self.connection.in_transaction)
        loadInventorySeed(self.connection, now=self.fixedNow)
        self.assertEqual(self.counts()["inventoryItems"], 16)


class SeedCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        temporaryDirectory = tempfile.TemporaryDirectory()
        self.addCleanup(temporaryDirectory.cleanup)
        self.databasePath = Path(temporaryDirectory.name) / "data" / "inventory.sqlite"

    def itemCount(self) -> int:
        connection = createConnection(self.databasePath)
        try:
            return connection.execute("SELECT COUNT(*) FROM inventoryItems").fetchone()[0]
        finally:
            connection.close()

    def testInv059CommandLoadsSeedIntoDatabaseFile(self) -> None:
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        command = [sys.executable, "-m", "services.api.inventoryseed", "--database", str(self.databasePath)]
        first = subprocess.run(command, cwd=repositoryRoot, env=environment, capture_output=True, text=True, timeout=60)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("16", first.stdout)
        self.assertEqual(self.itemCount(), 16)
        second = subprocess.run(command, cwd=repositoryRoot, env=environment, capture_output=True, text=True, timeout=60)
        self.assertEqual(second.returncode, 1)
        self.assertIn("already", second.stderr)
        self.assertEqual(self.itemCount(), 16)

    def testInv059MainReturnsExitCodes(self) -> None:
        self.assertEqual(main(["--database", str(self.databasePath)]), 0)
        self.assertEqual(main(["--database", str(self.databasePath)]), 1)
        self.assertEqual(self.itemCount(), 16)


if __name__ == "__main__":
    unittest.main()
