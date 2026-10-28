import unittest

from services.api.catalogs import catalogIds, catalogs, inventoryCatalogs


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


if __name__ == "__main__":
    unittest.main()
