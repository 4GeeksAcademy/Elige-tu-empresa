# Trazabilidad de requisitos — gestor de inventario

- **Spec:** [`specs/inventory-manager/spec.md`](../../specs/inventory-manager/spec.md), v1.0.
- **Tareas:** [`specs/inventory-manager/tasks.md`](../../specs/inventory-manager/tasks.md), v1.0.
- **Base de hashes:** historial de `6260bb2` (base aceptada del proyecto) a `HEAD` en `feature/inventory-manager`.
- **Cobertura comprobada:** 66/66 criterios `INV` aparecen en la sección de criterios del spec y cada uno tiene al menos un método de test con su ID en el nombre. Los tests negativos de las reglas de rechazo están incluidos; los tests de HTTP/UI se vinculan cuando cubren el contrato expuesto.

| INV | Tipo EARS | Tarea(s) | Test(s) | Commit(s) |
|---|---|---|---|---|
| INV-001 | Evento | T-08, T-25 | `testInv001CreateJoinsOuterTransactionAndRollsBack`, `testInv001CreatesItemWithUniqueIdAndZeroStock`, `testInv001PostItemReturns201WithZeroStock` | `a1bde2f`, `cb1db28` |
| INV-002 | No deseado | T-01, T-03, T-08, T-09, T-25 | `testInv002IncidentCatalogsAreUnchanged`, `testInv002InventoryCatalogsHaveApprovedValues`, `testInv002PostItemWithInvalidValuesReturns400`, `testInv002RejectsBlankNameOrValuesOutsideCatalogsOnCreate`, `testInv002RejectsInvalidValuesOnEdit`, `testInv002SqlRejectsValuesOutsideCatalogs` | `8333ab2`, `806c8d1`, `a1bde2f`, `4ba0ab7`, `cb1db28` |
| INV-003 | No deseado | T-02, T-03, T-08, T-09 | `testInv003RejectsInvalidReorderPointOnCreate`, `testInv003RejectsInvalidReorderPointOnEdit`, `testInv003RejectsReorderPointWithTooManyDecimals`, `testInv003SqlRejectsNegativeReorderPoint` | `0a71518`, `806c8d1`, `a1bde2f`, `4ba0ab7` |
| INV-004 | Evento | T-09 | `testInv004EditsNameAndReorderPointWithMovements` | `4ba0ab7` |
| INV-005 | Evento | T-09 | `testInv005EditsStructuralFieldsWithoutMovements` | `4ba0ab7` |
| INV-006 | No deseado | T-06, T-09, T-25 | `testInv006PatchStructuralFieldWithMovementsReturns409`, `testInv006RejectsStructuralChangeWithMovements`, `testInv006SqlAllowsStructuralChangeWithoutMovements`, `testInv006SqlRejectsStructuralChangeWithMovements` | `37f144d`, `4ba0ab7`, `cb1db28` |
| INV-007 | Evento | T-10, T-25 | `testInv007DeleteItemWithoutMovementsReturns200`, `testInv007DeletesItemWithoutMovements` | `891ea51`, `cb1db28` |
| INV-008 | No deseado | T-06, T-10, T-25 | `testInv008DeleteItemWithMovementsReturns409`, `testInv008RejectsDeleteWithMovementsAndKeepsThem`, `testInv008SqlRejectsDeleteOfItemWithMovements` | `37f144d`, `891ea51`, `cb1db28` |
| INV-009 | No deseado | T-09, T-10, T-11, T-20, T-25 | `testInv009RejectsDeleteOfUnknownItem`, `testInv009RejectsEditOfUnknownItem`, `testInv009RejectsGetOfUnknownItem`, `testInv009RejectsReportOfUnknownItem`, `testInv009UnknownItemReturns404` | `4ba0ab7`, `891ea51`, `b929193`, `3195fed`, `cb1db28` |
| INV-010 | Evento | T-11, T-25 | `testInv010FiltersByLocationId`, `testInv010GetItemsFiltersByLocation`, `testInv010InventoryCatalogsEndpointReturnsCatalogs`, `testInv010ListsItemsWithStockAndReorderMark`, `testInv010RejectsUnknownLocation` | `b929193`, `cb1db28` |
| INV-011 | Ubicuo | T-04, T-12 | `testInv011RecordsInboundWithSystemUtcCreatedAt`, `testInv011SqlStoresItemTypeQuantityReasonAndCreatedAt` | `b6644dd`, `04da6cd` |
| INV-012 | Evento | T-12, T-26 | `testInv012InboundIncreasesStock`, `testInv012PostInboundReturns201WithStock` | `04da6cd`, `1d31c09` |
| INV-013 | Evento | T-13 | `testInv013OutboundDecreasesStock` | `ce8f7ae` |
| INV-014 | Evento | T-14 | `testInv014AdjustmentAddsSignedQuantity`, `testInv014CountCorrectionAcceptsBothSigns` | `6209939` |
| INV-015 | No deseado | T-01, T-12, T-26 | `testInv015MovementTypesAreInboundOutboundAdjustment`, `testInv015RejectsUnknownMovementType`, `testInv015UnknownMovementTypeReturns400` | `8333ab2`, `04da6cd`, `1d31c09` |
| INV-016 | No deseado | T-12, T-26 | `testInv016RejectsMovementOfUnknownItem`, `testInv016UnknownItemReturns404` | `04da6cd`, `1d31c09` |
| INV-017 | No deseado | T-04, T-12, T-13 | `testInv017RejectsNonPositiveInbound`, `testInv017RejectsNonPositiveOutbound`, `testInv017SqlRejectsNonPositiveInboundAndOutbound` | `b6644dd`, `04da6cd`, `ce8f7ae` |
| INV-018 | No deseado | T-04, T-14 | `testInv018RejectsZeroAdjustment`, `testInv018SqlRejectsZeroAdjustment` | `b6644dd`, `6209939` |
| INV-019 | No deseado | T-04, T-14 | `testInv019RejectsPositiveWasteAndTheft`, `testInv019SqlRejectsPositiveWasteAndTheft` | `b6644dd`, `6209939` |
| INV-020 | No deseado | T-02, T-12, T-26 | `testInv020AcceptsThreeDecimalsInKgAndL`, `testInv020QuantityAsJsonNumberReturns400`, `testInv020RejectsExcessDecimalsInMovement`, `testInv020RejectsJsonNumbers`, `testInv020RejectsMalformedText`, `testInv020RejectsMoreDecimalsThanUnitAllows` | `0a71518`, `04da6cd`, `1d31c09` |
| INV-021 | No deseado | T-04, T-12, T-13 | `testInv021RejectsBlankInboundReason`, `testInv021RejectsBlankOutboundReason`, `testInv021SqlRejectsBlankReasonOnInboundAndOutbound` | `b6644dd`, `04da6cd`, `ce8f7ae` |
| INV-022 | No deseado | T-01, T-04, T-14 | `testInv022AdjustmentReasonsAreWasteTheftCountCorrection`, `testInv022RejectsMissingOrUnknownAdjustmentReason`, `testInv022SqlRejectsAdjustmentReasonOutsideCatalog` | `8333ab2`, `b6644dd`, `6209939` |
| INV-023 | No deseado | T-05, T-13, T-26 | `testInv023AcceptsOutboundThatLeavesStockAtZero`, `testInv023OutboundBelowZeroReturns409`, `testInv023RejectionLeavesNoMovement`, `testInv023RejectsOutboundBelowZero`, `testInv023SqlRejectsOutboundBelowZero` | `e3a3374`, `ce8f7ae`, `1d31c09` |
| INV-024 | No deseado | T-05, T-14 | `testInv024RejectsAdjustmentBelowZero`, `testInv024SqlRejectsAdjustmentBelowZero` | `e3a3374`, `6209939` |
| INV-025 | No deseado | T-15 | `testInv025ConcurrentOutboundsNeverLeaveNegativeStock`, `testInv025OnlyMovementsThatFitAreRegistered` | `2f6895a` |
| INV-026 | No deseado | T-16 | `testInv026RejectsMeatMovementWithoutLot`, `testInv026RejectsProduceMovementWithoutLot` | `cc77f44` |
| INV-027 | Opcional | T-16 | `testInv027AcceptsMovementWithoutLotForOtherCategories` | `cc77f44` |
| INV-028 | Evento | T-17 | `testInv028InboundWithNewLotCreatesLot`, `testInv028ReceivedAtIsRegistrationInstant` | `bf1c538` |
| INV-029 | No deseado | T-17 | `testInv029RejectsNewLotWithoutValidExpiryDate` | `bf1c538` |
| INV-030 | Evento | T-03, T-17 | `testInv030InboundOnExistingLotAddsStockKeepsExpiryDate`, `testInv030SqlRejectsLotDelete` | `806c8d1`, `bf1c538` |
| INV-031 | No deseado | T-03, T-17 | `testInv031RejectsInboundWithDifferentExpiryDate`, `testInv031SqlRejectsLotExpiryDateUpdate` | `806c8d1`, `bf1c538` |
| INV-032 | No deseado | T-18 | `testInv032RejectsAdjustmentOnUnknownLot`, `testInv032RejectsOutboundOnUnknownLot` | `7f79857` |
| INV-033 | No deseado | T-04, T-17, T-18 | `testInv033RejectsInboundOnLotOfAnotherItem`, `testInv033RejectsOutboundOnLotOfAnotherItem`, `testInv033SqlRejectsLotOfAnotherItem` | `b6644dd`, `bf1c538`, `7f79857` |
| INV-034 | No deseado | T-05, T-18 | `testInv034RejectsMovementBelowLotStock`, `testInv034SqlRejectsLotBelowZero` | `e3a3374`, `7f79857` |
| INV-035 | Ubicuo | T-07, T-18 | `testInv035LotStockIgnoresOtherLots`, `testInv035LotStockUsesOnlyLotMovements` | `da0e7a4`, `7f79857` |
| INV-055 | Evento | T-17 | `testInv055InboundMayOpenAlreadyExpiredLot` | `bf1c538` |
| INV-036 | Ubicuo | T-07 | `testInv036ItemWithoutMovementsHasZeroStock`, `testInv036StockIsSumOfSignedMovements`, `testInv036TriggerAndCalculateStockShareSignRule` | `da0e7a4` |
| INV-037 | Ubicuo | T-03, T-25, T-28 | `testInv037InventoryPageHasNoStockInput`, `testInv037NoRouteWritesStock`, `testInv037SchemaHasNoStockColumn` | `806c8d1`, `cb1db28`, `e295b29` |
| INV-038 | No deseado | T-08, T-09, T-25 | `testInv038RejectsStockFieldOnCreate`, `testInv038RejectsStockFieldOnEdit`, `testInv038StockFieldReturns400` | `a1bde2f`, `4ba0ab7`, `cb1db28` |
| INV-039 | Ubicuo | T-04, T-26 | `testInv039NoRouteChangesOrDeletesMovements`, `testInv039SqlRejectsMovementUpdateAndDelete` | `b6644dd`, `1d31c09` |
| INV-040 | Ubicuo | T-07 | `testInv040SameIngredientInTwoLocationsHasIndependentStock` | `da0e7a4` |
| INV-041 | Evento | T-21, T-26 | `testInv041GetReorderReturnsItems`, `testInv041ItemWithoutMovementsAppears`, `testInv041ReorderSignalReturnsItemsAtOrBelowReorderPoint` | `a03d510`, `1d31c09` |
| INV-042 | No deseado | T-11, T-21 | `testInv042ItemAboveReorderPointHasNoMark`, `testInv042ReorderSignalExcludesItemsAboveReorderPoint` | `b929193`, `a03d510` |
| INV-043 | Estado | T-11, T-20 | `testInv043ListMarksItemAtOrBelowReorderPoint`, `testInv043ReportMarksReorder` | `b929193`, `3195fed` |
| INV-044 | No deseado | T-21, T-26 | `testInv044RejectsReorderSignalOfUnknownLocation`, `testInv044UnknownLocationReorderReturns404` | `a03d510`, `1d31c09` |
| INV-045 | Evento | T-20, T-26 | `testInv045GetReportReturnsTotals`, `testInv045ReportReturnsStockAndInboundOutboundTotals` | `3195fed`, `1d31c09` |
| INV-046 | Evento | T-20 | `testInv046ReportAlwaysListsThreeReasons`, `testInv046ReportReturnsWasteTheftCountCorrectionSeparately` | `3195fed` |
| INV-047 | Evento | T-20 | `testInv047ReportReturnsStockPerLotWithExpiryDate` | `3195fed` |
| INV-048 | Ubicuo | T-19 | `testInv048LotExpiringTodayIsNotExpired`, `testInv048LotIsExpiredWhenExpiryDateBeforeTodayUtc` | `3f667ba` |
| INV-049 | Ubicuo | T-19, T-21 | `testInv049ExpiredStockCountsInAvailableStock`, `testInv049ReorderSignalCountsExpiredStock` | `3f667ba`, `a03d510` |
| INV-050 | No deseado | T-19 | `testInv050RejectsOutboundOnExpiredLot` | `3f667ba` |
| INV-051 | No deseado | T-19 | `testInv051RejectsNonWasteAdjustmentOnExpiredLot` | `3f667ba` |
| INV-052 | Evento | T-19 | `testInv052WasteAdjustmentReducesExpiredLotStock` | `3f667ba` |
| INV-053 | Evento | T-20 | `testInv053ItemViewListsExpiredLotsWithStock`, `testInv053ReportReturnsExpiredStockPerLot` | `3195fed` |
| INV-054 | Evento | T-29 | `testInv054ScriptBuildsExpiredStockText` | `78d293c` |
| INV-055 | Evento | T-17 | `testInv055InboundMayOpenAlreadyExpiredLot` | `bf1c538` |
| INV-056 | Evento | T-27 | `testInv056IndexAndInventoryPagesLinkEachOther`, `testInv056InventoryPageHasItemCreateEditDeleteControls`, `testInv056ServerServesInventoryPage` | `066c3ea` |
| INV-057 | Evento | T-28 | `testInv057MovementFormHasNoStockField`, `testInv057MovementFormOffersThreeTypes`, `testInv057ScriptShowsServerRejectionMessage` | `e295b29` |
| INV-058 | Evento | T-29 | `testInv058PageHasReportAndReorderPanels`, `testInv058ReportShowsWasteAndTheftSeparately` | `78d293c` |
| INV-059 | Evento | T-22, T-24 | `testInv059CommandLoadsSeedIntoDatabaseFile`, `testInv059MainReturnsExitCodes`, `testInv059SeedCreatesSixteenItemsWithDeclaredFields`, `testInv059SeedIsAtomicWhenAMovementFails` | `d6c83fc`, `a69fbe6` |
| INV-060 | Ubicuo | T-22 | `testInv060SeedStockComesOnlyFromMovements` | `d6c83fc` |
| INV-061 | Estado | T-22 | `testInv061EverySeedItemHasInboundOutboundAndAdjustment` | `d6c83fc` |
| INV-062 | Estado | T-22 | `testInv062SeedAdjustmentsIncludeAllThreeReasons` | `d6c83fc` |
| INV-063 | Estado | T-22 | `testInv063OnlyGarlicSauceAndTakeawayContainersAreAtOrBelowReorderPoint` | `d6c83fc` |
| INV-064 | Estado | T-23 | `testInv064CilantroHasExpiredLotWithStock`, `testInv064CilantroOutboundUsesNonExpiredLot` | `4c1bf10` |
| INV-065 | Estado | T-23 | `testInv065LotDatesFollowTheLoadDay`, `testInv065OtherSeedLotsExpireAfterLoadDay` | `4c1bf10` |
| INV-066 | No deseado | T-24 | `testInv066RejectedSeedChangesNothing`, `testInv066SeedRejectedWhenItemsExist` | `a69fbe6` |

## Comprobación reproducible de cobertura

Desde la raíz, la búsqueda de métodos con ID confirma que hay tests nombrados para los 66 criterios:

```bash
python - <<'PY'
import re
from pathlib import Path
spec = Path('specs/inventory-manager/spec.md').read_text()
criteria = set(re.findall(r'^\| (INV-\d{3}) \|', spec, re.M))
tests = set()
for path in Path('services/api/tests').glob('test*.py'):
    tests.update(re.findall(r'testInv\d{3}\w+', path.read_text()))
missing = sorted(inv for inv in criteria if not any(name.startswith('testInv' + inv[-3:]) for name in tests))
print(f'{len(criteria) - len(missing)}/{len(criteria)} criteria with a named test')
if missing:
    raise SystemExit(f'Missing test IDs: {missing}')
PY
```

Cada fila de tareas indica las pruebas directas y el asunto de commit; los hashes de esta tabla se resolvieron por asunto en el historial de la rama.
