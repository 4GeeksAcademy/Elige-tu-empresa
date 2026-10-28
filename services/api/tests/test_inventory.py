import sqlite3
import unittest

from services.api.catalogs import catalogIds, catalogs, inventoryCatalogs
from services.api.database import createConnection, initializeDatabase, stockDeltaSql
from services.api.inventory import calculateStock, formatQuantity, parseQuantity
from services.api.models import formatUtcTimestamp, generateId, utcNow


class InventoryCatalogTests(unittest.TestCase):
    def testInv002InventoryCatalogsHaveApprovedValues(self) -> None:
        self.assertEqual(catalogIds("units"), ("kg", "g", "l", "ml", "unit"))
        self.assertEqual(
            catalogIds("categories"),
            (
                "meat",
                "produce",
                "sauces_condiments",
                "beverages",
                "packaging",
                "cleaning_supplies",
            ),
        )
        self.assertEqual(
            catalogIds("locations"),
            ("laArepita", "queChille", "theBigSauce", "chilliBeans"),
        )
        self.assertEqual(
            tuple(entry.label for entry in inventoryCatalogs["locations"]),
            (
                "La Arepita (Colombia)",
                "QueChille (Colombia)",
                "The BigSauce (Estados Unidos, Florida)",
                "ChilliBeans (Estados Unidos, Florida)",
            ),
        )

    def testInv015MovementTypesAreInboundOutboundAdjustment(self) -> None:
        self.assertEqual(
            catalogIds("movementTypes"),
            ("inbound", "outbound", "adjustment"),
        )

    def testInv022AdjustmentReasonsAreWasteTheftCountCorrection(self) -> None:
        self.assertEqual(
            catalogIds("adjustmentReasons"),
            ("waste", "theft", "count_correction"),
        )

    def testInv002IncidentCatalogsAreUnchanged(self) -> None:
        self.assertEqual(
            set(catalogs),
            {"channels", "incidentTypes", "severities", "responsibleAreas", "statuses"},
        )
        self.assertEqual(catalogIds("channels"), ("whatsapp", "telefono", "email"))
        self.assertTrue(set(catalogs).isdisjoint(inventoryCatalogs))


class QuantityTests(unittest.TestCase):
    def testInv020AcceptsThreeDecimalsInKgAndL(self) -> None:
        self.assertEqual(parseQuantity("12.500", "kg"), 12500)
        self.assertEqual(parseQuantity("12.5", "kg"), 12500)
        self.assertEqual(parseQuantity("12", "l"), 12000)
        self.assertEqual(parseQuantity("0.001", "kg"), 1)
        self.assertEqual(parseQuantity("-0.250", "l"), -250)
        self.assertEqual(parseQuantity("12", "g"), 12000)
        self.assertEqual(parseQuantity("48", "unit"), 48000)
        self.assertEqual(formatQuantity(12500, "kg"), "12.500")
        self.assertEqual(formatQuantity(-250, "l"), "-0.250")
        self.assertEqual(formatQuantity(0, "kg"), "0.000")
        self.assertEqual(formatQuantity(12000, "unit"), "12")
        self.assertEqual(formatQuantity(-500000, "ml"), "-500")

    def testInv020RejectsMoreDecimalsThanUnitAllows(self) -> None:
        for text, unit in (
            ("0.0001", "kg"),
            ("1.2345", "l"),
            ("12.5", "g"),
            ("12.0", "ml"),
            ("1.5", "unit"),
        ):
            with self.subTest(text=text, unit=unit):
                with self.assertRaisesRegex(ValueError, "decimal"):
                    parseQuantity(text, unit)
        with self.assertRaisesRegex(ValueError, "decimal"):
            formatQuantity(12500, "unit")

    def testInv020RejectsJsonNumbers(self) -> None:
        for value in (12, 12.5, True, None, [1]):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "string"):
                    parseQuantity(value, "kg")

    def testInv020RejectsMalformedText(self) -> None:
        for text in ("", " 12", "12 ", "+1", ".5", "5.", "1e3", "1,5", "abc", "--1", "0x10"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parseQuantity(text, "kg")
        with self.assertRaisesRegex(ValueError, "Unknown unit"):
            parseQuantity("1", "lb")

    def testInv003RejectsReorderPointWithTooManyDecimals(self) -> None:
        with self.assertRaisesRegex(ValueError, "decimal"):
            parseQuantity("2.5", "unit")
        with self.assertRaisesRegex(ValueError, "decimal"):
            parseQuantity("2.0005", "kg")
        self.assertEqual(parseQuantity("0", "unit"), 0)


class InventorySchemaTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = createConnection(":memory:")
        initializeDatabase(self.connection)
        self.addCleanup(self.connection.close)

    def insertItem(self, **overrides: object) -> str:
        values = {
            "id": generateId(),
            "name": "Cilantro",
            "locationId": "queChille",
            "category": "produce",
            "unitOfMeasure": "kg",
            "reorderPointMilli": 2000,
            "createdAt": formatUtcTimestamp(utcNow()),
        }
        values.update(overrides)
        self.connection.execute(
            """
            INSERT INTO inventoryItems (
                id, name, locationId, category, unitOfMeasure, reorderPointMilli, createdAt
            ) VALUES (:id, :name, :locationId, :category, :unitOfMeasure, :reorderPointMilli, :createdAt)
            """,
            values,
        )
        return values["id"]

    def insertLot(self, itemId: str, **overrides: object) -> str:
        values = {
            "lotCode": "lotA",
            "itemId": itemId,
            "expiryDate": "2026-12-01",
            "receivedAt": formatUtcTimestamp(utcNow()),
        }
        values.update(overrides)
        self.connection.execute(
            """
            INSERT INTO inventoryLots (lotCode, itemId, expiryDate, receivedAt)
            VALUES (:lotCode, :itemId, :expiryDate, :receivedAt)
            """,
            values,
        )
        return values["lotCode"]

    def insertMovement(self, itemId: str, **overrides: object) -> str:
        values = {
            "id": generateId(),
            "itemId": itemId,
            "lotCode": None,
            "movementType": "inbound",
            "quantityMilli": 5000,
            "reason": "purchase",
            "createdAt": formatUtcTimestamp(utcNow()),
        }
        values.update(overrides)
        self.connection.execute(
            """
            INSERT INTO stockMovements (
                id, itemId, lotCode, movementType, quantityMilli, reason, createdAt
            ) VALUES (:id, :itemId, :lotCode, :movementType, :quantityMilli, :reason, :createdAt)
            """,
            values,
        )
        return values["id"]


class InventoryItemSchemaTests(InventorySchemaTestCase):
    def testInv037SchemaHasNoStockColumn(self) -> None:
        for tableName in ("inventoryItems", "inventoryLots"):
            columns = {row["name"].lower() for row in self.connection.execute(f"PRAGMA table_info({tableName})")}
            with self.subTest(tableName=tableName):
                self.assertTrue(columns)
                self.assertFalse(any("stock" in name or "quantity" in name for name in columns))

    def testInv002SqlRejectsValuesOutsideCatalogs(self) -> None:
        self.insertItem()
        for overrides in (
            {"locationId": "unknown"},
            {"category": "unknown"},
            {"unitOfMeasure": "lb"},
            {"name": "   "},
            {"id": "not-a-uuid"},
        ):
            with self.subTest(overrides=overrides):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.insertItem(**overrides)

    def testInv003SqlRejectsNegativeReorderPoint(self) -> None:
        self.insertItem(reorderPointMilli=0)
        with self.assertRaises(sqlite3.IntegrityError):
            self.insertItem(reorderPointMilli=-1)


class InventoryLotSchemaTests(InventorySchemaTestCase):
    def testInv031SqlRejectsLotExpiryDateUpdate(self) -> None:
        itemId = self.insertItem()
        self.insertLot(itemId)
        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable"):
            self.connection.execute("UPDATE inventoryLots SET expiryDate = '2027-01-01'")

    def testInv030SqlRejectsLotDelete(self) -> None:
        itemId = self.insertItem()
        self.insertLot(itemId)
        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable"):
            self.connection.execute("DELETE FROM inventoryLots")


class StockMovementSchemaTests(InventorySchemaTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.itemId = self.insertItem()

    def testInv011SqlStoresItemTypeQuantityReasonAndCreatedAt(self) -> None:
        createdAt = formatUtcTimestamp(utcNow())
        movementId = self.insertMovement(
            self.itemId,
            movementType="inbound",
            quantityMilli=12500,
            reason="weekly delivery",
            createdAt=createdAt,
        )
        row = self.connection.execute("SELECT * FROM stockMovements WHERE id = ?", (movementId,)).fetchone()
        self.assertEqual(
            (row["itemId"], row["movementType"], row["quantityMilli"], row["reason"], row["createdAt"]),
            (self.itemId, "inbound", 12500, "weekly delivery", createdAt),
        )
        self.assertIsNone(row["lotCode"])
        with self.assertRaises(sqlite3.IntegrityError):
            self.insertMovement(self.itemId, movementType="transfer")
        with self.assertRaises(sqlite3.IntegrityError):
            self.insertMovement(generateId())
        with self.assertRaises(sqlite3.IntegrityError):
            self.insertMovement(self.itemId, createdAt=None)

    def testInv017SqlRejectsNonPositiveInboundAndOutbound(self) -> None:
        for movementType in ("inbound", "outbound"):
            for quantityMilli in (0, -1000):
                with self.subTest(movementType=movementType, quantityMilli=quantityMilli):
                    with self.assertRaises(sqlite3.IntegrityError):
                        self.insertMovement(self.itemId, movementType=movementType, quantityMilli=quantityMilli)

    def testInv018SqlRejectsZeroAdjustment(self) -> None:
        for reason in ("waste", "theft", "count_correction"):
            with self.subTest(reason=reason):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.insertMovement(self.itemId, movementType="adjustment", quantityMilli=0, reason=reason)

    def testInv019SqlRejectsPositiveWasteAndTheft(self) -> None:
        for reason in ("waste", "theft"):
            with self.subTest(reason=reason):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.insertMovement(self.itemId, movementType="adjustment", quantityMilli=1000, reason=reason)
        self.insertMovement(self.itemId, movementType="adjustment", quantityMilli=1000, reason="count_correction")
        self.insertMovement(self.itemId, movementType="adjustment", quantityMilli=-1000, reason="count_correction")

    def testInv021SqlRejectsBlankReasonOnInboundAndOutbound(self) -> None:
        for movementType in ("inbound", "outbound"):
            for reason in ("", "   "):
                with self.subTest(movementType=movementType, reason=reason):
                    with self.assertRaises(sqlite3.IntegrityError):
                        self.insertMovement(self.itemId, movementType=movementType, reason=reason)

    def testInv022SqlRejectsAdjustmentReasonOutsideCatalog(self) -> None:
        for reason in ("", "purchase", "Waste"):
            with self.subTest(reason=reason):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.insertMovement(self.itemId, movementType="adjustment", quantityMilli=-1000, reason=reason)

    def testInv033SqlRejectsLotOfAnotherItem(self) -> None:
        otherItemId = self.insertItem(name="Cebolla cabezona")
        self.insertLot(self.itemId, lotCode="lotA")
        self.insertMovement(self.itemId, lotCode="lotA")
        with self.assertRaises(sqlite3.IntegrityError):
            self.insertMovement(otherItemId, lotCode="lotA")
        with self.assertRaises(sqlite3.IntegrityError):
            self.insertMovement(self.itemId, lotCode="unknownLot")

    def testInv039SqlRejectsMovementUpdateAndDelete(self) -> None:
        movementId = self.insertMovement(self.itemId)
        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable"):
            self.connection.execute("UPDATE stockMovements SET quantityMilli = 1 WHERE id = ?", (movementId,))
        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable"):
            self.connection.execute("DELETE FROM stockMovements WHERE id = ?", (movementId,))


class StockFloorTriggerTests(InventorySchemaTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.itemId = self.insertItem()

    def testInv023SqlRejectsOutboundBelowZero(self) -> None:
        self.insertMovement(self.itemId, quantityMilli=5000)
        with self.assertRaisesRegex(sqlite3.IntegrityError, "negative"):
            self.insertMovement(self.itemId, movementType="outbound", quantityMilli=5001, reason="sale")
        self.insertMovement(self.itemId, movementType="outbound", quantityMilli=5000, reason="sale")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "negative"):
            self.insertMovement(self.itemId, movementType="outbound", quantityMilli=1, reason="sale")
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM stockMovements").fetchone()[0], 2)

    def testInv024SqlRejectsAdjustmentBelowZero(self) -> None:
        self.insertMovement(self.itemId, quantityMilli=1000)
        with self.assertRaisesRegex(sqlite3.IntegrityError, "negative"):
            self.insertMovement(self.itemId, movementType="adjustment", quantityMilli=-1001, reason="waste")
        self.insertMovement(self.itemId, movementType="adjustment", quantityMilli=-1000, reason="waste")
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM stockMovements").fetchone()[0], 2)

    def testInv034SqlRejectsLotBelowZero(self) -> None:
        self.insertLot(self.itemId, lotCode="lotA")
        self.insertLot(self.itemId, lotCode="lotB")
        self.insertMovement(self.itemId, lotCode="lotA", quantityMilli=3000)
        self.insertMovement(self.itemId, lotCode="lotB", quantityMilli=3000)
        with self.assertRaisesRegex(sqlite3.IntegrityError, "Lot stock"):
            self.insertMovement(self.itemId, lotCode="lotA", movementType="outbound", quantityMilli=3001, reason="sale")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "Lot stock"):
            self.insertMovement(
                self.itemId, lotCode="lotB", movementType="adjustment", quantityMilli=-3001, reason="waste"
            )
        self.insertMovement(self.itemId, lotCode="lotA", movementType="outbound", quantityMilli=3000, reason="sale")


class ItemWithMovementsTriggerTests(InventorySchemaTestCase):
    def testInv006SqlRejectsStructuralChangeWithMovements(self) -> None:
        itemId = self.insertItem()
        self.insertMovement(itemId)
        for column, value in (
            ("locationId", "laArepita"),
            ("category", "beverages"),
            ("unitOfMeasure", "l"),
        ):
            with self.subTest(column=column):
                with self.assertRaisesRegex(sqlite3.IntegrityError, "movements"):
                    self.connection.execute(f"UPDATE inventoryItems SET {column} = ? WHERE id = ?", (value, itemId))
        self.connection.execute(
            "UPDATE inventoryItems SET name = 'Cilantro fresco', reorderPointMilli = 3000, locationId = 'queChille' WHERE id = ?",
            (itemId,),
        )
        row = self.connection.execute("SELECT * FROM inventoryItems WHERE id = ?", (itemId,)).fetchone()
        self.assertEqual((row["name"], row["reorderPointMilli"], row["locationId"]), ("Cilantro fresco", 3000, "queChille"))

    def testInv006SqlAllowsStructuralChangeWithoutMovements(self) -> None:
        itemId = self.insertItem()
        self.connection.execute(
            "UPDATE inventoryItems SET locationId = 'laArepita', category = 'beverages', unitOfMeasure = 'l' WHERE id = ?",
            (itemId,),
        )
        row = self.connection.execute("SELECT * FROM inventoryItems WHERE id = ?", (itemId,)).fetchone()
        self.assertEqual((row["locationId"], row["category"], row["unitOfMeasure"]), ("laArepita", "beverages", "l"))

    def testInv008SqlRejectsDeleteOfItemWithMovements(self) -> None:
        itemId = self.insertItem()
        emptyItemId = self.insertItem(name="Desengrasante")
        self.insertMovement(itemId)
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute("DELETE FROM inventoryItems WHERE id = ?", (itemId,))
        self.connection.execute("DELETE FROM inventoryItems WHERE id = ?", (emptyItemId,))
        remaining = {row["id"] for row in self.connection.execute("SELECT id FROM inventoryItems")}
        self.assertEqual(remaining, {itemId})
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM stockMovements").fetchone()[0], 1)


class CalculateStockTests(InventorySchemaTestCase):
    def testInv036StockIsSumOfSignedMovements(self) -> None:
        itemId = self.insertItem()
        self.insertMovement(itemId, quantityMilli=10000)
        self.insertMovement(itemId, movementType="outbound", quantityMilli=3000, reason="sale")
        self.insertMovement(itemId, movementType="adjustment", quantityMilli=-500, reason="waste")
        self.insertMovement(itemId, movementType="adjustment", quantityMilli=200, reason="count_correction")
        self.assertEqual(calculateStock(self.connection, itemId=itemId), {itemId: 6700})

    def testInv036ItemWithoutMovementsHasZeroStock(self) -> None:
        itemId = self.insertItem()
        self.assertEqual(calculateStock(self.connection, itemId=itemId), {itemId: 0})
        self.assertEqual(calculateStock(self.connection, locationId="queChille"), {itemId: 0})
        self.assertEqual(calculateStock(self.connection, itemId=generateId()), {})
        self.assertEqual(calculateStock(self.connection, locationId="laArepita"), {})

    def testInv040SameIngredientInTwoLocationsHasIndependentStock(self) -> None:
        firstItemId = self.insertItem(locationId="queChille")
        secondItemId = self.insertItem(locationId="chilliBeans")
        self.insertMovement(firstItemId, quantityMilli=8000)
        self.insertMovement(secondItemId, quantityMilli=3000)
        self.insertMovement(secondItemId, movementType="outbound", quantityMilli=1000, reason="sale")
        self.assertEqual(calculateStock(self.connection, locationId="queChille"), {firstItemId: 8000})
        self.assertEqual(calculateStock(self.connection, locationId="chilliBeans"), {secondItemId: 2000})
        self.assertEqual(
            calculateStock(self.connection),
            {firstItemId: 8000, secondItemId: 2000},
        )

    def testInv035LotStockUsesOnlyLotMovements(self) -> None:
        itemId = self.insertItem()
        otherItemId = self.insertItem(name="Cebolla cabezona")
        self.insertLot(itemId, lotCode="lotA")
        self.insertLot(itemId, lotCode="lotB")
        self.insertLot(otherItemId, lotCode="lotC")
        self.insertMovement(itemId, lotCode="lotA", quantityMilli=5000)
        self.insertMovement(itemId, lotCode="lotA", movementType="outbound", quantityMilli=2000, reason="sale")
        self.insertMovement(itemId, lotCode="lotB", quantityMilli=1500)
        self.insertMovement(itemId, quantityMilli=700)
        self.insertMovement(otherItemId, lotCode="lotC", quantityMilli=9000)
        self.assertEqual(
            calculateStock(self.connection, itemId=itemId, groupByLot=True),
            {(itemId, "lotA"): 3000, (itemId, "lotB"): 1500},
        )
        self.assertEqual(calculateStock(self.connection, itemId=itemId), {itemId: 5200})
        self.assertEqual(
            calculateStock(self.connection, locationId="queChille", groupByLot=True),
            {(itemId, "lotA"): 3000, (itemId, "lotB"): 1500, (otherItemId, "lotC"): 9000},
        )

    def testInv036TriggerAndCalculateStockShareSignRule(self) -> None:
        triggerSql = self.connection.execute(
            "SELECT sql FROM sqlite_master WHERE name = 'stockMovements_preventNegativeStock'"
        ).fetchone()["sql"]
        self.assertIn(stockDeltaSql(), triggerSql)
        self.assertIn(stockDeltaSql("NEW."), triggerSql)
        itemId = self.insertItem()
        self.insertMovement(itemId, quantityMilli=9000)
        self.insertMovement(itemId, movementType="adjustment", quantityMilli=-1500, reason="theft")
        availableStock = calculateStock(self.connection, itemId=itemId)[itemId]
        self.assertEqual(availableStock, 7500)
        with self.assertRaisesRegex(sqlite3.IntegrityError, "negative"):
            self.insertMovement(itemId, movementType="outbound", quantityMilli=availableStock + 1, reason="sale")
        self.insertMovement(itemId, movementType="outbound", quantityMilli=availableStock, reason="sale")
        self.assertEqual(calculateStock(self.connection, itemId=itemId), {itemId: 0})


if __name__ == "__main__":
    unittest.main()
