import sqlite3
import unittest

from services.api.catalogs import catalogIds, catalogs, inventoryCatalogs
from services.api.database import createConnection, initializeDatabase
from services.api.inventory import formatQuantity, parseQuantity
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


if __name__ == "__main__":
    unittest.main()
