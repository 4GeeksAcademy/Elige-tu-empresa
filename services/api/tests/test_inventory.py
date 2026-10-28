import unittest

from services.api.catalogs import catalogIds, catalogs, inventoryCatalogs
from services.api.inventory import formatQuantity, parseQuantity


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


if __name__ == "__main__":
    unittest.main()
