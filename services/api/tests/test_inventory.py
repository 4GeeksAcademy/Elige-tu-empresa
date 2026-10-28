import sqlite3
import unittest
from datetime import datetime, timezone

from services.api.catalogs import catalogIds, catalogs, inventoryCatalogs
from services.api.database import createConnection, initializeDatabase, stockDeltaSql
from services.api.inventory import (
    BusinessRuleError,
    calculateStock,
    createItem,
    deleteItem,
    formatQuantity,
    getItem,
    listItems,
    parseQuantity,
    registerMovement,
    updateItem,
)
from services.api.models import formatUtcTimestamp, generateId, isUuid4, parseUtcTimestamp, utcNow


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
        self.connection.commit()
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
        self.connection.commit()
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
        self.connection.commit()
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


class CreateItemTests(InventorySchemaTestCase):
    fixedNow = datetime(2026, 10, 28, 12, 0, 0, tzinfo=timezone.utc)

    def validFields(self, **overrides: object) -> dict:
        fields = {
            "name": "Cilantro",
            "locationId": "queChille",
            "category": "produce",
            "unitOfMeasure": "kg",
            "reorderPoint": "2",
        }
        fields.update(overrides)
        return fields

    def itemCount(self) -> int:
        return self.connection.execute("SELECT COUNT(*) FROM inventoryItems").fetchone()[0]

    def testInv001CreatesItemWithUniqueIdAndZeroStock(self) -> None:
        first = createItem(self.connection, self.validFields(), now=self.fixedNow)
        second = createItem(
            self.connection,
            self.validFields(name="Refresco de cola", category="beverages", unitOfMeasure="unit", reorderPoint="48"),
            now=self.fixedNow,
        )
        self.assertTrue(isUuid4(first["id"]))
        self.assertNotEqual(first["id"], second["id"])
        self.assertEqual(
            {key: first[key] for key in ("name", "locationId", "category", "unitOfMeasure", "reorderPoint", "stock")},
            {
                "name": "Cilantro",
                "locationId": "queChille",
                "category": "produce",
                "unitOfMeasure": "kg",
                "reorderPoint": "2.000",
                "stock": "0.000",
            },
        )
        self.assertEqual((second["reorderPoint"], second["stock"]), ("48", "0"))
        self.assertEqual(first["createdAt"], formatUtcTimestamp(self.fixedNow))
        row = self.connection.execute("SELECT * FROM inventoryItems WHERE id = ?", (first["id"],)).fetchone()
        self.assertEqual((row["name"], row["reorderPointMilli"]), ("Cilantro", 2000))
        self.assertEqual(calculateStock(self.connection, itemId=first["id"]), {first["id"]: 0})
        self.assertIs(first["needsReorder"], True)

    def testInv001CreateJoinsOuterTransactionAndRollsBack(self) -> None:
        self.connection.execute("BEGIN IMMEDIATE")
        createItem(self.connection, self.validFields(), now=self.fixedNow)
        self.assertTrue(self.connection.in_transaction)
        self.connection.rollback()
        self.assertEqual(self.itemCount(), 0)
        createItem(self.connection, self.validFields(), now=self.fixedNow)
        self.assertFalse(self.connection.in_transaction)
        self.assertEqual(self.itemCount(), 1)

    def testInv002RejectsBlankNameOrValuesOutsideCatalogsOnCreate(self) -> None:
        for overrides in (
            {"name": ""},
            {"name": "   "},
            {"name": 5},
            {"locationId": "unknown"},
            {"category": "unknown"},
            {"unitOfMeasure": "lb"},
            {"locationId": None},
        ):
            with self.subTest(overrides=overrides):
                with self.assertRaises(ValueError):
                    createItem(self.connection, self.validFields(**overrides), now=self.fixedNow)
        fields = self.validFields()
        del fields["category"]
        with self.assertRaisesRegex(ValueError, "Missing"):
            createItem(self.connection, fields, now=self.fixedNow)
        self.assertEqual(self.itemCount(), 0)

    def testInv003RejectsInvalidReorderPointOnCreate(self) -> None:
        for overrides in (
            {"reorderPoint": "-1"},
            {"reorderPoint": "1.0005"},
            {"unitOfMeasure": "unit", "reorderPoint": "2.5"},
            {"reorderPoint": 5},
            {"reorderPoint": ""},
        ):
            with self.subTest(overrides=overrides):
                with self.assertRaises(ValueError):
                    createItem(self.connection, self.validFields(**overrides), now=self.fixedNow)
        created = createItem(self.connection, self.validFields(reorderPoint="0"), now=self.fixedNow)
        self.assertEqual(created["reorderPoint"], "0.000")
        self.assertEqual(self.itemCount(), 1)

    def testInv038RejectsStockFieldOnCreate(self) -> None:
        for fieldName in ("stock", "quantity", "stockMilli", "availableStock"):
            with self.subTest(fieldName=fieldName):
                with self.assertRaisesRegex(ValueError, "Unsupported"):
                    createItem(self.connection, self.validFields(**{fieldName: "5"}), now=self.fixedNow)
        self.assertEqual(self.itemCount(), 0)


class UpdateItemTests(InventorySchemaTestCase):
    fixedNow = datetime(2026, 10, 28, 12, 0, 0, tzinfo=timezone.utc)

    def createBaseItem(self, **overrides: object) -> dict:
        fields = {
            "name": "Cilantro",
            "locationId": "queChille",
            "category": "produce",
            "unitOfMeasure": "kg",
            "reorderPoint": "2",
        }
        fields.update(overrides)
        return createItem(self.connection, fields, now=self.fixedNow)

    def storedItem(self, itemId: str) -> dict:
        return dict(self.connection.execute("SELECT * FROM inventoryItems WHERE id = ?", (itemId,)).fetchone())

    def testInv004EditsNameAndReorderPointWithMovements(self) -> None:
        item = self.createBaseItem()
        self.insertMovement(item["id"], quantityMilli=4000)
        updated = updateItem(self.connection, item["id"], {"name": " Cilantro fresco ", "reorderPoint": "3.5"})
        self.assertEqual((updated["name"], updated["reorderPoint"], updated["stock"]), ("Cilantro fresco", "3.500", "4.000"))
        self.assertEqual(updated["needsReorder"], False)
        stored = self.storedItem(item["id"])
        self.assertEqual((stored["name"], stored["reorderPointMilli"]), ("Cilantro fresco", 3500))

    def testInv005EditsStructuralFieldsWithoutMovements(self) -> None:
        item = self.createBaseItem()
        updated = updateItem(
            self.connection,
            item["id"],
            {"locationId": "laArepita", "category": "beverages", "unitOfMeasure": "l"},
        )
        self.assertEqual(
            (updated["locationId"], updated["category"], updated["unitOfMeasure"], updated["reorderPoint"]),
            ("laArepita", "beverages", "l", "2.000"),
        )
        self.assertEqual(self.storedItem(item["id"])["locationId"], "laArepita")

    def testInv006RejectsStructuralChangeWithMovements(self) -> None:
        item = self.createBaseItem()
        self.insertMovement(item["id"])
        for changes in (
            {"locationId": "laArepita"},
            {"category": "meat"},
            {"unitOfMeasure": "l"},
            {"name": "Otro nombre", "category": "meat"},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(BusinessRuleError):
                    updateItem(self.connection, item["id"], changes)
        stored = self.storedItem(item["id"])
        self.assertEqual((stored["name"], stored["locationId"], stored["category"], stored["unitOfMeasure"]), ("Cilantro", "queChille", "produce", "kg"))
        repeated = updateItem(self.connection, item["id"], {"locationId": "queChille", "name": "Cilantro 2"})
        self.assertEqual(repeated["name"], "Cilantro 2")

    def testInv002RejectsInvalidValuesOnEdit(self) -> None:
        item = self.createBaseItem()
        for changes in (
            {"name": ""},
            {"name": "   "},
            {"name": 5},
            {"locationId": "unknown"},
            {"category": "unknown"},
            {"unitOfMeasure": "lb"},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    updateItem(self.connection, item["id"], changes)
        self.assertEqual(self.storedItem(item["id"])["name"], "Cilantro")

    def testInv003RejectsInvalidReorderPointOnEdit(self) -> None:
        item = self.createBaseItem(reorderPoint="2.5")
        for changes in (
            {"reorderPoint": "-1"},
            {"reorderPoint": "1.0005"},
            {"reorderPoint": 5},
            {"unitOfMeasure": "unit"},
            {"unitOfMeasure": "unit", "reorderPoint": "2.5"},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    updateItem(self.connection, item["id"], changes)
        self.assertEqual(self.storedItem(item["id"])["reorderPointMilli"], 2500)
        converted = updateItem(self.connection, item["id"], {"unitOfMeasure": "unit", "reorderPoint": "3"})
        self.assertEqual((converted["unitOfMeasure"], converted["reorderPoint"]), ("unit", "3"))

    def testInv038RejectsStockFieldOnEdit(self) -> None:
        item = self.createBaseItem()
        for fieldName in ("stock", "quantity", "stockMilli", "availableStock"):
            with self.subTest(fieldName=fieldName):
                with self.assertRaisesRegex(ValueError, "Unsupported"):
                    updateItem(self.connection, item["id"], {"name": "Otro", fieldName: "5"})
        with self.assertRaisesRegex(ValueError, "No fields"):
            updateItem(self.connection, item["id"], {})
        self.assertEqual(self.storedItem(item["id"])["name"], "Cilantro")

    def testInv009RejectsEditOfUnknownItem(self) -> None:
        with self.assertRaises(LookupError):
            updateItem(self.connection, generateId(), {"name": "Otro"})
        with self.assertRaises(LookupError):
            updateItem(self.connection, "not-a-uuid", {"name": "Otro"})


class DeleteItemTests(InventorySchemaTestCase):
    def testInv007DeletesItemWithoutMovements(self) -> None:
        itemId = self.insertItem()
        otherItemId = self.insertItem(name="Cebolla cabezona")
        self.assertEqual(deleteItem(self.connection, itemId), {"deleted": itemId})
        remaining = {row["id"] for row in self.connection.execute("SELECT id FROM inventoryItems")}
        self.assertEqual(remaining, {otherItemId})
        self.assertFalse(self.connection.in_transaction)

    def testInv008RejectsDeleteWithMovementsAndKeepsThem(self) -> None:
        itemId = self.insertItem()
        self.insertMovement(itemId, quantityMilli=4000)
        with self.assertRaises(BusinessRuleError):
            deleteItem(self.connection, itemId)
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM inventoryItems").fetchone()[0], 1)
        self.assertEqual(calculateStock(self.connection, itemId=itemId), {itemId: 4000})
        self.assertFalse(self.connection.in_transaction)

    def testInv009RejectsDeleteOfUnknownItem(self) -> None:
        itemId = self.insertItem()
        with self.assertRaises(LookupError):
            deleteItem(self.connection, generateId())
        with self.assertRaises(LookupError):
            deleteItem(self.connection, "not-a-uuid")
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM inventoryItems").fetchone()[0], 1)
        self.assertEqual(self.connection.execute("SELECT id FROM inventoryItems").fetchone()["id"], itemId)


class ListItemsTests(InventorySchemaTestCase):
    fixedNow = datetime(2026, 10, 28, 12, 0, 0, tzinfo=timezone.utc)

    def createBaseItem(self, **overrides: object) -> dict:
        fields = {
            "name": "Cilantro",
            "locationId": "queChille",
            "category": "produce",
            "unitOfMeasure": "kg",
            "reorderPoint": "2",
        }
        fields.update(overrides)
        return createItem(self.connection, fields, now=self.fixedNow)

    def testInv010ListsItemsWithStockAndReorderMark(self) -> None:
        cilantro = self.createBaseItem()
        cola = self.createBaseItem(
            name="Refresco de cola", locationId="theBigSauce", category="beverages", unitOfMeasure="unit", reorderPoint="48"
        )
        self.insertMovement(cilantro["id"], quantityMilli=7500)
        self.insertMovement(cilantro["id"], movementType="outbound", quantityMilli=1000, reason="sale")
        self.insertMovement(cola["id"], quantityMilli=100000)
        items = listItems(self.connection)
        self.assertEqual([item["name"] for item in items], ["Cilantro", "Refresco de cola"])
        byName = {item["name"]: item for item in items}
        self.assertEqual(
            (byName["Cilantro"]["stock"], byName["Cilantro"]["needsReorder"], byName["Cilantro"]["reorderPoint"]),
            ("6.500", False, "2.000"),
        )
        self.assertEqual(
            (byName["Refresco de cola"]["stock"], byName["Refresco de cola"]["needsReorder"]),
            ("100", False),
        )
        self.assertEqual(
            set(byName["Cilantro"]),
            {"id", "name", "locationId", "category", "unitOfMeasure", "reorderPoint", "stock", "needsReorder", "createdAt"},
        )
        self.assertEqual(getItem(self.connection, cilantro["id"]), byName["Cilantro"])

    def testInv010FiltersByLocationId(self) -> None:
        self.createBaseItem(name="Cilantro", locationId="queChille")
        self.createBaseItem(name="Jalapeños", locationId="chilliBeans")
        self.createBaseItem(name="Cebolla", locationId="chilliBeans")
        self.assertEqual([item["name"] for item in listItems(self.connection, "chilliBeans")], ["Cebolla", "Jalapeños"])
        self.assertEqual([item["name"] for item in listItems(self.connection, locationId="queChille")], ["Cilantro"])
        self.assertEqual(listItems(self.connection, "laArepita"), [])
        self.assertEqual(len(listItems(self.connection)), 3)

    def testInv010RejectsUnknownLocation(self) -> None:
        for locationId in ("unknown", "", 5):
            with self.subTest(locationId=locationId):
                with self.assertRaises(LookupError):
                    listItems(self.connection, locationId)

    def testInv009RejectsGetOfUnknownItem(self) -> None:
        with self.assertRaises(LookupError):
            getItem(self.connection, generateId())
        with self.assertRaises(LookupError):
            getItem(self.connection, "not-a-uuid")

    def testInv042ItemAboveReorderPointHasNoMark(self) -> None:
        item = self.createBaseItem(reorderPoint="2")
        self.insertMovement(item["id"], quantityMilli=2001)
        self.assertIs(getItem(self.connection, item["id"])["needsReorder"], False)
        self.assertIs(listItems(self.connection)[0]["needsReorder"], False)

    def testInv043ListMarksItemAtOrBelowReorderPoint(self) -> None:
        atPoint = self.createBaseItem(name="En el punto", reorderPoint="2")
        below = self.createBaseItem(name="Por debajo", reorderPoint="2")
        empty = self.createBaseItem(name="Sin movimientos", reorderPoint="0")
        self.insertMovement(atPoint["id"], quantityMilli=2000)
        self.insertMovement(below["id"], quantityMilli=1999)
        marks = {item["name"]: item["needsReorder"] for item in listItems(self.connection, "queChille")}
        self.assertEqual(marks, {"En el punto": True, "Por debajo": True, "Sin movimientos": True})
        self.assertIs(getItem(self.connection, empty["id"])["needsReorder"], True)


class MovementTestCase(InventorySchemaTestCase):
    fixedNow = datetime(2026, 10, 28, 12, 0, 0, tzinfo=timezone.utc)

    def setUp(self) -> None:
        super().setUp()
        self.item = createItem(
            self.connection,
            {
                "name": "Jugo de lulo",
                "locationId": "queChille",
                "category": "beverages",
                "unitOfMeasure": "l",
                "reorderPoint": "10",
            },
            now=self.fixedNow,
        )
        self.itemId = self.item["id"]

    def inbound(self, **overrides: object) -> dict:
        fields = {"movementType": "inbound", "quantity": "5", "reason": "weekly delivery"}
        fields.update(overrides)
        return fields

    def movementCount(self) -> int:
        return self.connection.execute("SELECT COUNT(*) FROM stockMovements").fetchone()[0]



class RegisterInboundTests(MovementTestCase):
    def testInv011RecordsInboundWithSystemUtcCreatedAt(self) -> None:
        movement = registerMovement(self.connection, self.itemId, self.inbound(), now=self.fixedNow)
        self.assertTrue(isUuid4(movement["id"]))
        self.assertEqual(
            {key: movement[key] for key in ("itemId", "movementType", "quantity", "reason", "lotCode", "createdAt")},
            {
                "itemId": self.itemId,
                "movementType": "inbound",
                "quantity": "5.000",
                "reason": "weekly delivery",
                "lotCode": None,
                "createdAt": formatUtcTimestamp(self.fixedNow),
            },
        )
        row = self.connection.execute("SELECT * FROM stockMovements WHERE id = ?", (movement["id"],)).fetchone()
        self.assertEqual((row["quantityMilli"], row["createdAt"]), (5000, formatUtcTimestamp(self.fixedNow)))
        before = utcNow()
        automatic = registerMovement(self.connection, self.itemId, self.inbound())
        after = utcNow()
        self.assertTrue(before <= parseUtcTimestamp(automatic["createdAt"]) <= after)
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            registerMovement(self.connection, self.itemId, self.inbound(createdAt="2020-01-01T00:00:00Z"))
        self.assertEqual(self.movementCount(), 2)

    def testInv012InboundIncreasesStock(self) -> None:
        self.assertEqual(self.item["stock"], "0.000")
        first = registerMovement(self.connection, self.itemId, self.inbound(quantity="5"))
        second = registerMovement(self.connection, self.itemId, self.inbound(quantity="2.5"))
        self.assertEqual((first["stock"], second["stock"]), ("5.000", "7.500"))
        self.assertEqual(getItem(self.connection, self.itemId)["stock"], "7.500")
        self.assertFalse(self.connection.in_transaction)

    def testInv015RejectsUnknownMovementType(self) -> None:
        for movementType in ("transfer", "", "INBOUND", None, 5):
            with self.subTest(movementType=movementType):
                with self.assertRaises(ValueError):
                    registerMovement(self.connection, self.itemId, self.inbound(movementType=movementType))
        with self.assertRaisesRegex(ValueError, "Missing"):
            registerMovement(self.connection, self.itemId, {"quantity": "5", "reason": "weekly delivery"})
        self.assertEqual(self.movementCount(), 0)

    def testInv016RejectsMovementOfUnknownItem(self) -> None:
        for itemId in (generateId(), "not-a-uuid"):
            with self.subTest(itemId=itemId):
                with self.assertRaises(LookupError):
                    registerMovement(self.connection, itemId, self.inbound())
        self.assertEqual(self.movementCount(), 0)

    def testInv017RejectsNonPositiveInbound(self) -> None:
        for quantity in ("0", "0.000", "-1", "-0.500"):
            with self.subTest(quantity=quantity):
                with self.assertRaises(ValueError):
                    registerMovement(self.connection, self.itemId, self.inbound(quantity=quantity))
        self.assertEqual(self.movementCount(), 0)

    def testInv020RejectsExcessDecimalsInMovement(self) -> None:
        unitItem = createItem(
            self.connection,
            {
                "name": "Servilletas",
                "locationId": "chilliBeans",
                "category": "packaging",
                "unitOfMeasure": "unit",
                "reorderPoint": "500",
            },
            now=self.fixedNow,
        )
        with self.assertRaisesRegex(ValueError, "decimal"):
            registerMovement(self.connection, self.itemId, self.inbound(quantity="1.2345"))
        with self.assertRaisesRegex(ValueError, "decimal"):
            registerMovement(self.connection, unitItem["id"], self.inbound(quantity="1.5"))
        with self.assertRaises(ValueError):
            registerMovement(self.connection, self.itemId, self.inbound(quantity=5))
        self.assertEqual(self.movementCount(), 0)
        registerMovement(self.connection, self.itemId, self.inbound(quantity="1.234"))
        registerMovement(self.connection, unitItem["id"], self.inbound(quantity="1500"))
        self.assertEqual(self.movementCount(), 2)

    def testInv021RejectsBlankInboundReason(self) -> None:
        for reason in ("", "   ", None, 5):
            with self.subTest(reason=reason):
                with self.assertRaises(ValueError):
                    registerMovement(self.connection, self.itemId, self.inbound(reason=reason))
        fields = self.inbound()
        del fields["reason"]
        with self.assertRaisesRegex(ValueError, "Missing"):
            registerMovement(self.connection, self.itemId, fields)
        self.assertEqual(self.movementCount(), 0)


class RegisterOutboundTests(MovementTestCase):
    def outbound(self, **overrides: object) -> dict:
        fields = {"movementType": "outbound", "quantity": "3.5", "reason": "kitchen use"}
        fields.update(overrides)
        return fields

    def stockMilli(self) -> int:
        return calculateStock(self.connection, itemId=self.itemId)[self.itemId]

    def testInv013OutboundDecreasesStock(self) -> None:
        registerMovement(self.connection, self.itemId, self.inbound(quantity="10"))
        movement = registerMovement(self.connection, self.itemId, self.outbound(), now=self.fixedNow)
        self.assertEqual(
            (movement["movementType"], movement["quantity"], movement["reason"], movement["stock"]),
            ("outbound", "3.500", "kitchen use", "6.500"),
        )
        self.assertEqual(movement["createdAt"], formatUtcTimestamp(self.fixedNow))
        row = self.connection.execute("SELECT * FROM stockMovements WHERE id = ?", (movement["id"],)).fetchone()
        self.assertEqual(row["quantityMilli"], 3500)
        self.assertEqual(self.stockMilli(), 6500)

    def testInv017RejectsNonPositiveOutbound(self) -> None:
        registerMovement(self.connection, self.itemId, self.inbound(quantity="10"))
        for quantity in ("0", "-1", "-0.500"):
            with self.subTest(quantity=quantity):
                with self.assertRaises(ValueError):
                    registerMovement(self.connection, self.itemId, self.outbound(quantity=quantity))
        self.assertEqual(self.movementCount(), 1)
        self.assertEqual(self.stockMilli(), 10000)

    def testInv021RejectsBlankOutboundReason(self) -> None:
        registerMovement(self.connection, self.itemId, self.inbound(quantity="10"))
        for reason in ("", "   ", None, 5):
            with self.subTest(reason=reason):
                with self.assertRaises(ValueError):
                    registerMovement(self.connection, self.itemId, self.outbound(reason=reason))
        self.assertEqual(self.movementCount(), 1)

    def testInv023RejectsOutboundBelowZero(self) -> None:
        with self.assertRaises(BusinessRuleError):
            registerMovement(self.connection, self.itemId, self.outbound(quantity="0.001"))
        registerMovement(self.connection, self.itemId, self.inbound(quantity="5"))
        with self.assertRaisesRegex(BusinessRuleError, "stock"):
            registerMovement(self.connection, self.itemId, self.outbound(quantity="5.001"))
        self.assertEqual(self.stockMilli(), 5000)

    def testInv023AcceptsOutboundThatLeavesStockAtZero(self) -> None:
        registerMovement(self.connection, self.itemId, self.inbound(quantity="5"))
        movement = registerMovement(self.connection, self.itemId, self.outbound(quantity="5"))
        self.assertEqual(movement["stock"], "0.000")
        self.assertEqual(self.stockMilli(), 0)
        with self.assertRaises(BusinessRuleError):
            registerMovement(self.connection, self.itemId, self.outbound(quantity="0.001"))

    def testInv023RejectionLeavesNoMovement(self) -> None:
        registerMovement(self.connection, self.itemId, self.inbound(quantity="2"))
        with self.assertRaises(BusinessRuleError):
            registerMovement(self.connection, self.itemId, self.outbound(quantity="3"))
        self.assertEqual(self.movementCount(), 1)
        self.assertFalse(self.connection.in_transaction)
        registerMovement(self.connection, self.itemId, self.outbound(quantity="2"))
        self.assertEqual(self.movementCount(), 2)


class RegisterAdjustmentTests(MovementTestCase):
    def adjustment(self, **overrides: object) -> dict:
        fields = {"movementType": "adjustment", "quantity": "-2", "reason": "waste"}
        fields.update(overrides)
        return fields

    def stockMilli(self) -> int:
        return calculateStock(self.connection, itemId=self.itemId)[self.itemId]

    def testInv014AdjustmentAddsSignedQuantity(self) -> None:
        registerMovement(self.connection, self.itemId, self.inbound(quantity="10"))
        reduced = registerMovement(self.connection, self.itemId, self.adjustment(), now=self.fixedNow)
        self.assertEqual(
            (reduced["movementType"], reduced["quantity"], reduced["reason"], reduced["stock"]),
            ("adjustment", "-2.000", "waste", "8.000"),
        )
        self.assertEqual(reduced["createdAt"], formatUtcTimestamp(self.fixedNow))
        increased = registerMovement(
            self.connection, self.itemId, self.adjustment(quantity="1.5", reason="count_correction")
        )
        self.assertEqual((increased["quantity"], increased["stock"]), ("1.500", "9.500"))
        row = self.connection.execute("SELECT quantityMilli FROM stockMovements WHERE id = ?", (reduced["id"],)).fetchone()
        self.assertEqual(row["quantityMilli"], -2000)
        self.assertEqual(self.stockMilli(), 9500)

    def testInv014CountCorrectionAcceptsBothSigns(self) -> None:
        registerMovement(self.connection, self.itemId, self.inbound(quantity="3"))
        down = registerMovement(self.connection, self.itemId, self.adjustment(quantity="-1", reason="count_correction"))
        up = registerMovement(self.connection, self.itemId, self.adjustment(quantity="4", reason="count_correction"))
        self.assertEqual((down["stock"], up["stock"]), ("2.000", "6.000"))

    def testInv018RejectsZeroAdjustment(self) -> None:
        registerMovement(self.connection, self.itemId, self.inbound(quantity="3"))
        for reason in ("waste", "theft", "count_correction"):
            for quantity in ("0", "0.000", "-0"):
                with self.subTest(reason=reason, quantity=quantity):
                    with self.assertRaises(ValueError):
                        registerMovement(self.connection, self.itemId, self.adjustment(quantity=quantity, reason=reason))
        self.assertEqual(self.movementCount(), 1)

    def testInv019RejectsPositiveWasteAndTheft(self) -> None:
        registerMovement(self.connection, self.itemId, self.inbound(quantity="3"))
        for reason in ("waste", "theft"):
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(ValueError, "negative"):
                    registerMovement(self.connection, self.itemId, self.adjustment(quantity="1", reason=reason))
        self.assertEqual(self.movementCount(), 1)
        self.assertEqual(self.stockMilli(), 3000)

    def testInv022RejectsMissingOrUnknownAdjustmentReason(self) -> None:
        registerMovement(self.connection, self.itemId, self.inbound(quantity="3"))
        for reason in ("", "   ", "purchase", "Waste", None, 5):
            with self.subTest(reason=reason):
                with self.assertRaises(ValueError):
                    registerMovement(self.connection, self.itemId, self.adjustment(reason=reason))
        fields = self.adjustment()
        del fields["reason"]
        with self.assertRaisesRegex(ValueError, "Missing"):
            registerMovement(self.connection, self.itemId, fields)
        self.assertEqual(self.movementCount(), 1)

    def testInv024RejectsAdjustmentBelowZero(self) -> None:
        registerMovement(self.connection, self.itemId, self.inbound(quantity="1"))
        with self.assertRaisesRegex(BusinessRuleError, "stock"):
            registerMovement(self.connection, self.itemId, self.adjustment(quantity="-1.001"))
        with self.assertRaises(BusinessRuleError):
            registerMovement(self.connection, self.itemId, self.adjustment(quantity="-1.001", reason="count_correction"))
        self.assertEqual(self.stockMilli(), 1000)
        registerMovement(self.connection, self.itemId, self.adjustment(quantity="-1", reason="theft"))
        self.assertEqual(self.stockMilli(), 0)
        with self.assertRaises(BusinessRuleError):
            registerMovement(self.connection, self.itemId, self.adjustment(quantity="-0.001", reason="count_correction"))
        self.assertEqual(self.movementCount(), 2)
        self.assertFalse(self.connection.in_transaction)


if __name__ == "__main__":
    unittest.main()
