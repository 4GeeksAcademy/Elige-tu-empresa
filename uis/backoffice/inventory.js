"use strict";

const apiBase = "/api/inventory";
const elements = {
  connectionStatus: document.querySelector("#connectionStatus"),
  feedback: document.querySelector("#feedback"),
  registerItemForm: document.querySelector("#registerItemForm"),
  movementForm: document.querySelector("#movementForm"),
  adjustmentReasonField: document.querySelector("#adjustmentReasonField"),
  freeReasonField: document.querySelector("#freeReasonField"),
  expiryDateField: document.querySelector("#expiryDateField"),
  editItemPanel: document.querySelector("#editItemPanel"),
  editItemForm: document.querySelector("#editItemForm"),
  cancelEdit: document.querySelector("#cancelEdit"),
  locationFilter: document.querySelector("#locationFilter"),
  itemRows: document.querySelector("#itemRows"),
  emptyItems: document.querySelector("#emptyItems"),
  stockReportPanel: document.querySelector("#stockReportPanel"),
  reportItemFilter: document.querySelector("#reportItemFilter"),
  stockReportDetails: document.querySelector("#stockReportDetails"),
  emptyStockReport: document.querySelector("#emptyStockReport"),
  reorderLocationFilter: document.querySelector("#reorderLocationFilter"),
  reorderRows: document.querySelector("#reorderRows"),
  emptyReorder: document.querySelector("#emptyReorder"),
};

let catalogs = null;
let editingItemId = null;
let items = [];
const movementLotsByItem = new Map();

async function requestJson(path, options = {}) {
  const response = await fetch(`${apiBase}${path}`, options);
  const responseData = await response.json();
  if (!response.ok) {
    throw new Error(responseData.error || `La solicitud falló (${response.status}).`);
  }
  return responseData;
}

function showFeedback(message, kind) {
  elements.feedback.textContent = message;
  elements.feedback.dataset.kind = kind;
}

function clearFeedback() {
  elements.feedback.textContent = "";
  delete elements.feedback.dataset.kind;
}

function fillSelect(select, entries, includeEmpty = false) {
  select.replaceChildren();
  if (includeEmpty) {
    const emptyOption = document.createElement("option");
    emptyOption.value = "";
    emptyOption.textContent = "Todos";
    select.append(emptyOption);
  }
  for (const entry of entries) {
    const option = document.createElement("option");
    option.value = entry.id;
    option.textContent = entry.label;
    select.append(option);
  }
}

function catalogLabel(catalogName, value) {
  return catalogs[catalogName].find((entry) => entry.id === value)?.label || value;
}

function setConnection(isConnected) {
  elements.connectionStatus.textContent = isConnected ? "Conectado" : "Sin conexión";
}

function createCell(text) {
  const cell = document.createElement("td");
  cell.textContent = text;
  return cell;
}

function createDetail(label, value) {
  const detail = document.createElement("div");
  detail.className = "detailItem";
  const title = document.createElement("span");
  title.textContent = label;
  const content = document.createElement("strong");
  content.textContent = value;
  detail.append(title, content);
  return detail;
}

function formatStockSummary(item) {
  const expiredLots = (item.expiredLots || []).filter((lot) => Number(lot.stock) > 0);
  if (expiredLots.length === 0) {
    return `${item.stock} ${item.unitOfMeasure}`;
  }
  const expiredText = expiredLots
    .map((lot) => `${lot.stock} ${item.unitOfMeasure} caducados (lote ${lot.lotCode})`)
    .join(", ");
  return `${item.stock} ${item.unitOfMeasure} disponibles, de ellos ${expiredText}`;
}

function createActionButton(label, className, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.textContent = label;
  button.addEventListener("click", onClick);
  return button;
}

function renderItems(items) {
  elements.itemRows.replaceChildren();
  elements.emptyItems.hidden = items.length > 0;
  for (const item of items) {
    const row = document.createElement("tr");
    const markCell = document.createElement("td");
    if (item.needsReorder) {
      const mark = document.createElement("span");
      mark.className = "reorderMark";
      mark.textContent = "Reordenar";
      markCell.append(mark);
    } else {
      markCell.textContent = "—";
    }
    const actionsCell = document.createElement("td");
    actionsCell.className = "rowActions";
    actionsCell.append(
      createActionButton("Editar", "viewButton secondaryButton", () => startEdit(item)),
      createActionButton("Dar de baja", "viewButton textButton", () => removeItem(item)),
    );
    row.append(
      createCell(item.name),
      createCell(catalogLabel("locations", item.locationId)),
      createCell(item.category),
      createCell(formatStockSummary(item)),
      createCell(`${item.reorderPoint} ${item.unitOfMeasure}`),
      markCell,
      actionsCell,
    );
    elements.itemRows.append(row);
  }
}

async function refreshItems() {
  const locationId = elements.locationFilter.value;
  const query = locationId ? `?locationId=${encodeURIComponent(locationId)}` : "";
  items = await requestJson(`/items${query}`);
  renderItems(items);
  const selectedItemId = elements.movementForm.elements.itemId.value;
  fillSelect(elements.movementForm.elements.itemId, items.map((item) => ({
    id: item.id,
    label: `${item.name} (${item.stock} ${item.unitOfMeasure})`,
  })));
  if (items.some((item) => item.id === selectedItemId)) {
    elements.movementForm.elements.itemId.value = selectedItemId;
  }
  fillSelect(elements.reportItemFilter, items.map((item) => ({
    id: item.id,
    label: item.name,
  })));
  if (items.some((item) => item.id === reportItemId)) {
    elements.reportItemFilter.value = reportItemId;
  }
  reportItemId = elements.reportItemFilter.value;
  elements.emptyStockReport.hidden = items.length > 0;
  await refreshStockReport();
}

let reportItemId = "";

async function refreshStockReport() {
  const itemId = elements.reportItemFilter.value;
  elements.stockReportDetails.replaceChildren();
  if (!itemId) {
    return;
  }
  reportItemId = itemId;
  const report = await requestJson(`/items/${encodeURIComponent(itemId)}/report`);
  const item = items.find((entry) => entry.id === itemId);
  const details = [
    ["Artículo", item?.name || itemId],
    ["Stock disponible", `${report.stock} ${report.unitOfMeasure}`],
    ["Punto de reorden", `${report.reorderPoint} ${report.unitOfMeasure}`],
    ["Entradas", `${report.totalInbound} ${report.unitOfMeasure}`],
    ["Salidas", `${report.totalOutbound} ${report.unitOfMeasure}`],
    ["Reorden", report.needsReorder ? "Reordenar" : "No requiere reorden"],
  ];
  for (const adjustment of report.adjustments) {
    const label = adjustment.reason === "waste"
      ? "Desperdicio (waste)"
      : adjustment.reason === "theft" ? "Robo (theft)" : "Corrección de conteo (count_correction)";
    details.push([label, `${adjustment.total} ${report.unitOfMeasure}`]);
  }
  for (const lot of report.lots) {
    details.push([
      `Lote ${lot.lotCode} · caducidad ${lot.expiryDate}${lot.expired ? " · caducado" : ""}`,
      `${lot.stock} ${report.unitOfMeasure} (${lot.expiredStock} caducados)`,
    ]);
  }
  for (const [label, value] of details) {
    elements.stockReportDetails.append(createDetail(label, value));
  }
}

async function refreshReorderSignal() {
  const locationId = elements.reorderLocationFilter.value;
  const signal = await requestJson(`/locations/${encodeURIComponent(locationId)}/reorder`);
  elements.reorderRows.replaceChildren();
  elements.emptyReorder.hidden = signal.length > 0;
  if (signal.length === 0) {
    return;
  }
  const table = document.createElement("table");
  const head = document.createElement("thead");
  const headerRow = document.createElement("tr");
  for (const label of ["Artículo", "Stock disponible", "Punto de reorden"]) {
    const cell = document.createElement("th");
    cell.textContent = label;
    headerRow.append(cell);
  }
  head.append(headerRow);
  const body = document.createElement("tbody");
  for (const entry of signal) {
    const row = document.createElement("tr");
    row.append(
      createCell(entry.name),
      createCell(`${entry.stock} ${entry.unitOfMeasure}`),
      createCell(`${entry.reorderPoint} ${entry.unitOfMeasure}`),
    );
    body.append(row);
  }
  table.append(head, body);
  elements.reorderRows.append(table);
}

function updateMovementFields() {
  const form = elements.movementForm;
  const isAdjustment = form.elements.movementType.value === "adjustment";
  const selectedItem = items.find((item) => item.id === form.elements.itemId.value);
  const opensNewLot = form.elements.movementType.value === "inbound"
    && form.elements.lotCode.value.trim() !== ""
    && !movementLotsByItem.get(selectedItem?.id)?.some((lot) => lot.lotCode === form.elements.lotCode.value.trim());
  elements.adjustmentReasonField.hidden = !isAdjustment;
  elements.freeReasonField.hidden = isAdjustment;
  form.elements.adjustmentReason.required = isAdjustment;
  form.elements.freeReason.required = !isAdjustment;
  elements.expiryDateField.hidden = !opensNewLot;
  form.elements.expiryDate.required = opensNewLot;
}

async function refreshMovementLots() {
  const itemId = elements.movementForm.elements.itemId.value;
  if (!itemId || movementLotsByItem.has(itemId)) {
    updateMovementFields();
    return;
  }
  try {
    const report = await requestJson(`/items/${encodeURIComponent(itemId)}/report`);
    movementLotsByItem.set(itemId, report.lots);
  } catch (error) {
    showFeedback(error.message, "error");
  }
  updateMovementFields();
}

function movementValues(form) {
  const fields = form.elements;
  const movement = {
    movementType: fields.movementType.value,
    quantity: fields.quantity.value,
  };
  if (fields.movementType.value === "adjustment") {
    movement.reason = fields.adjustmentReason.value;
  } else {
    movement.reason = fields.freeReason.value;
  }
  if (fields.lotCode.value.trim()) {
    movement.lotCode = fields.lotCode.value.trim();
  }
  if (!elements.expiryDateField.hidden && fields.expiryDate.value) {
    movement.expiryDate = fields.expiryDate.value;
  }
  return movement;
}

function closeEdit() {
  editingItemId = null;
  elements.editItemPanel.hidden = true;
  elements.editItemForm.reset();
}

function startEdit(item) {
  clearFeedback();
  editingItemId = item.id;
  const form = elements.editItemForm;
  form.elements.name.value = item.name;
  form.elements.locationId.value = item.locationId;
  form.elements.category.value = item.category;
  form.elements.unitOfMeasure.value = item.unitOfMeasure;
  form.elements.reorderPoint.value = item.reorderPoint;
  elements.editItemPanel.hidden = false;
  form.elements.name.focus();
}

async function removeItem(item) {
  clearFeedback();
  if (!window.confirm(`¿Dar de baja «${item.name}»? Solo es posible si no tiene movimientos.`)) {
    return;
  }
  try {
    await requestJson(`/items/${encodeURIComponent(item.id)}`, { method: "DELETE" });
    if (editingItemId === item.id) {
      closeEdit();
    }
    showFeedback(`Artículo dado de baja: ${item.name}`, "success");
    await refreshItems();
  } catch (error) {
    showFeedback(error.message, "error");
  }
}

elements.registerItemForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearFeedback();
  const itemValues = Object.fromEntries(new FormData(elements.registerItemForm));
  try {
    const item = await requestJson("/items", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(itemValues),
    });
    elements.registerItemForm.reset();
    showFeedback(`Artículo registrado: ${item.name}`, "success");
    await refreshItems();
  } catch (error) {
    showFeedback(error.message, "error");
  }
});

elements.movementForm.addEventListener("input", updateMovementFields);
elements.movementForm.addEventListener("change", (event) => {
  updateMovementFields();
  if (event.target === elements.movementForm.elements.itemId) {
    refreshMovementLots();
  }
});
elements.movementForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearFeedback();
  const itemId = elements.movementForm.elements.itemId.value;
  try {
    const movement = await requestJson(`/items/${encodeURIComponent(itemId)}/movements`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(movementValues(elements.movementForm)),
    });
    elements.movementForm.reset();
    updateMovementFields();
    showFeedback(`Movimiento registrado. Stock disponible: ${movement.stock}`, "success");
    movementLotsByItem.delete(itemId);
    await refreshItems();
    await refreshMovementLots();
  } catch (error) {
    showFeedback(error.message, "error");
  }
});

elements.editItemForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearFeedback();
  const itemValues = Object.fromEntries(new FormData(elements.editItemForm));
  try {
    const item = await requestJson(`/items/${encodeURIComponent(editingItemId)}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(itemValues),
    });
    closeEdit();
    showFeedback(`Artículo actualizado: ${item.name}`, "success");
    await refreshItems();
  } catch (error) {
    showFeedback(error.message, "error");
  }
});

elements.cancelEdit.addEventListener("click", closeEdit);

elements.locationFilter.addEventListener("change", async () => {
  clearFeedback();
  try {
    await refreshItems();
    await refreshMovementLots();
  } catch (error) {
    showFeedback(error.message, "error");
  }
});

elements.reportItemFilter.addEventListener("change", async () => {
  clearFeedback();
  try {
    await refreshStockReport();
  } catch (error) {
    showFeedback(error.message, "error");
  }
});

elements.reorderLocationFilter.addEventListener("change", async () => {
  clearFeedback();
  try {
    await refreshReorderSignal();
  } catch (error) {
    showFeedback(error.message, "error");
  }
});

async function start() {
  try {
    catalogs = await requestJson("/catalogs");
    for (const form of [elements.registerItemForm, elements.editItemForm]) {
      fillSelect(form.elements.locationId, catalogs.locations);
      fillSelect(form.elements.category, catalogs.categories);
      fillSelect(form.elements.unitOfMeasure, catalogs.units);
    }
    fillSelect(elements.movementForm.elements.adjustmentReason, catalogs.adjustmentReasons);
    fillSelect(elements.locationFilter, catalogs.locations, true);
    fillSelect(elements.reorderLocationFilter, catalogs.locations);
    await refreshItems();
    await refreshMovementLots();
    await refreshReorderSignal();
    updateMovementFields();
    setConnection(true);
  } catch (error) {
    setConnection(false);
    showFeedback(error.message, "error");
  }
}

start();
