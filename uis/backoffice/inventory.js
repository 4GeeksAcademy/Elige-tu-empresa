"use strict";

const apiBase = "/api/inventory";
const elements = {
  connectionStatus: document.querySelector("#connectionStatus"),
  feedback: document.querySelector("#feedback"),
  registerItemForm: document.querySelector("#registerItemForm"),
  editItemPanel: document.querySelector("#editItemPanel"),
  editItemForm: document.querySelector("#editItemForm"),
  cancelEdit: document.querySelector("#cancelEdit"),
  locationFilter: document.querySelector("#locationFilter"),
  itemRows: document.querySelector("#itemRows"),
  emptyItems: document.querySelector("#emptyItems"),
};

let catalogs = null;
let editingItemId = null;

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
      createCell(`${item.stock} ${item.unitOfMeasure}`),
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
  renderItems(await requestJson(`/items${query}`));
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
    fillSelect(elements.locationFilter, catalogs.locations, true);
    await refreshItems();
    setConnection(true);
  } catch (error) {
    setConnection(false);
    showFeedback(error.message, "error");
  }
}

start();
