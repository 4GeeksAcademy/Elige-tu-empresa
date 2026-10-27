"use strict";

const apiBase = "/api";
const elements = {
  connectionStatus: document.querySelector("#connectionStatus"),
  feedback: document.querySelector("#feedback"),
  severitySummary: document.querySelector("#severitySummary"),
  registerForm: document.querySelector("#registerForm"),
  filterForm: document.querySelector("#filterForm"),
  incidentRows: document.querySelector("#incidentRows"),
  emptyList: document.querySelector("#emptyList"),
  detailsPanel: document.querySelector("#detailsPanel"),
  incidentDetails: document.querySelector("#incidentDetails"),
  statusForm: document.querySelector("#statusForm"),
  areaForm: document.querySelector("#areaForm"),
  historyEvents: document.querySelector("#historyEvents"),
  emptyHistory: document.querySelector("#emptyHistory"),
};

let catalogs = null;
let selectedIncidentId = null;

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

function formatLocalTimestamp(value) {
  return new Date(value).toLocaleString();
}

function addDetailItem(container, label, value, className = "") {
  const item = document.createElement("div");
  item.className = `detailItem ${className}`.trim();
  const itemLabel = document.createElement("span");
  itemLabel.textContent = label;
  const itemValue = document.createElement("strong");
  itemValue.textContent = value || "—";
  item.append(itemLabel, itemValue);
  container.append(item);
}

async function refreshSummary() {
  const counts = await requestJson("/incidents/summary/by-severity");
  elements.severitySummary.replaceChildren();
  for (const severity of catalogs.severities) {
    const card = document.createElement("article");
    card.className = "summaryCard";
    card.dataset.severity = severity.id;
    const label = document.createElement("span");
    label.textContent = severity.label;
    const count = document.createElement("strong");
    count.textContent = String(counts[severity.id] ?? 0);
    card.append(label, count);
    elements.severitySummary.append(card);
  }
}

async function refreshIncidents() {
  const filters = new URLSearchParams();
  for (const fieldName of ["statusId", "severityId", "responsibleAreaId"]) {
    const value = elements.filterForm.elements.namedItem(fieldName).value;
    if (value) filters.set(fieldName, value);
  }
  const query = filters.toString();
  const incidents = await requestJson(`/incidents${query ? `?${query}` : ""}`);
  elements.incidentRows.replaceChildren();
  elements.emptyList.hidden = incidents.length > 0;
  for (const incident of incidents) {
    const row = document.createElement("tr");
    const titleCell = document.createElement("td");
    titleCell.className = "tableTitle";
    titleCell.textContent = incident.title;
    const statusCell = document.createElement("td");
    statusCell.textContent = catalogLabel("statuses", incident.statusId);
    const severityCell = document.createElement("td");
    severityCell.textContent = catalogLabel("severities", incident.severityId);
    const areaCell = document.createElement("td");
    areaCell.textContent = catalogLabel("responsibleAreas", incident.responsibleAreaId);
    const updatedCell = document.createElement("td");
    updatedCell.textContent = formatLocalTimestamp(incident.updatedAt);
    const actionCell = document.createElement("td");
    const detailsButton = document.createElement("button");
    detailsButton.type = "button";
    detailsButton.className = "viewButton";
    detailsButton.textContent = "Ver ficha";
    detailsButton.addEventListener("click", () => loadIncidentDetails(incident.id));
    actionCell.append(detailsButton);
    row.append(titleCell, statusCell, severityCell, areaCell, updatedCell, actionCell);
    elements.incidentRows.append(row);
  }
}

function allowedStatusIds(currentStatusId) {
  const statusTransitions = {
    nueva: ["enCurso"],
    enCurso: ["resuelta"],
    resuelta: ["cerrada", "enCurso"],
    cerrada: [],
  };
  return statusTransitions[currentStatusId] || [];
}

async function loadIncidentDetails(incidentId) {
  const details = await requestJson(`/incidents/${encodeURIComponent(incidentId)}`);
  selectedIncidentId = incidentId;
  const incident = details.incident;
  const detailGrid = document.createElement("div");
  detailGrid.className = "detailsGrid";
  addDetailItem(detailGrid, "Título", incident.title);
  addDetailItem(detailGrid, "Canal", catalogLabel("channels", incident.channelId));
  addDetailItem(detailGrid, "Tipo", catalogLabel("incidentTypes", incident.typeId));
  addDetailItem(detailGrid, "Severidad", catalogLabel("severities", incident.severityId));
  addDetailItem(detailGrid, "Estado", catalogLabel("statuses", incident.statusId));
  addDetailItem(detailGrid, "Área responsable", catalogLabel("responsibleAreas", incident.responsibleAreaId));
  addDetailItem(detailGrid, "Creada por", incident.createdBy);
  addDetailItem(detailGrid, "Creada", formatLocalTimestamp(incident.createdAt));
  addDetailItem(detailGrid, "Actualizada", formatLocalTimestamp(incident.updatedAt));
  addDetailItem(detailGrid, "Descripción", incident.description, "detailsDescription");
  elements.incidentDetails.replaceChildren(detailGrid);

  const statusSelect = elements.statusForm.elements.namedItem("statusId");
  const allowedStatuses = allowedStatusIds(incident.statusId).map((statusId) =>
    catalogs.statuses.find((entry) => entry.id === statusId)
  );
  fillSelect(statusSelect, allowedStatuses);
  elements.statusForm.querySelector("button").disabled = allowedStatuses.length === 0;
  fillSelect(
    elements.areaForm.elements.namedItem("responsibleAreaId"),
    catalogs.responsibleAreas.filter((entry) => entry.assignable && entry.id !== incident.responsibleAreaId)
  );
  elements.areaForm.querySelector("button").disabled =
    elements.areaForm.elements.namedItem("responsibleAreaId").options.length === 0;

  elements.historyEvents.replaceChildren();
  elements.emptyHistory.hidden = details.historyEvents.length > 0;
  for (const event of details.historyEvents) {
    const item = document.createElement("li");
    const eventCard = document.createElement("div");
    eventCard.className = "historyEvent";
    const title = document.createElement("strong");
    title.textContent = event.changeType === "estado" ? "Cambio de estado" : "Cambio de área";
    const values = document.createElement("p");
    const catalogName = event.changeType === "estado" ? "statuses" : "responsibleAreas";
    values.textContent = `${catalogLabel(catalogName, event.previousValue)} → ${catalogLabel(catalogName, event.newValue)}`;
    const author = document.createElement("p");
    author.textContent = `Autor: ${event.author}`;
    const timestamp = document.createElement("time");
    timestamp.dateTime = event.createdAt;
    timestamp.textContent = formatLocalTimestamp(event.createdAt);
    eventCard.append(title, values, author, timestamp);
    item.append(eventCard);
    elements.historyEvents.append(item);
  }

  elements.detailsPanel.hidden = false;
  elements.detailsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function refreshAll() {
  await Promise.all([refreshSummary(), refreshIncidents()]);
}

async function initializeBackoffice() {
  try {
    catalogs = await requestJson("/catalogs");
    fillSelect(elements.registerForm.elements.namedItem("channelId"), catalogs.channels);
    fillSelect(elements.registerForm.elements.namedItem("typeId"), catalogs.incidentTypes);
    fillSelect(elements.registerForm.elements.namedItem("severityId"), catalogs.severities);
    fillSelect(
      elements.registerForm.elements.namedItem("responsibleAreaId"),
      catalogs.responsibleAreas.filter((entry) => entry.assignable)
    );
    fillSelect(elements.filterForm.elements.namedItem("statusId"), catalogs.statuses, true);
    fillSelect(elements.filterForm.elements.namedItem("severityId"), catalogs.severities, true);
    fillSelect(
      elements.filterForm.elements.namedItem("responsibleAreaId"),
      catalogs.responsibleAreas.filter((entry) => entry.assignable),
      true
    );
    elements.connectionStatus.textContent = "Servicio conectado";
    await refreshAll();
  } catch (error) {
    elements.connectionStatus.textContent = "Servicio no disponible";
    showFeedback(error.message, "error");
  }
}

elements.registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearFeedback();
  const incidentValues = Object.fromEntries(new FormData(elements.registerForm));
  try {
    const incident = await requestJson("/incidents", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(incidentValues),
    });
    elements.registerForm.reset();
    showFeedback(`Incidencia registrada: ${incident.title}`, "success");
    await refreshAll();
    await loadIncidentDetails(incident.id);
  } catch (error) {
    showFeedback(error.message, "error");
  }
});

elements.filterForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await refreshIncidents();
    clearFeedback();
  } catch (error) {
    showFeedback(error.message, "error");
  }
});

elements.filterForm.addEventListener("reset", () => {
  window.setTimeout(() => {
    refreshIncidents().catch((error) => showFeedback(error.message, "error"));
  }, 0);
});

elements.statusForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!selectedIncidentId) return;
  const values = Object.fromEntries(new FormData(elements.statusForm));
  try {
    await requestJson(`/incidents/${encodeURIComponent(selectedIncidentId)}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    });
    showFeedback("Estado actualizado y añadido al historial.", "success");
    await refreshAll();
    await loadIncidentDetails(selectedIncidentId);
  } catch (error) {
    showFeedback(error.message, "error");
  }
});

elements.areaForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!selectedIncidentId) return;
  const values = Object.fromEntries(new FormData(elements.areaForm));
  try {
    await requestJson(`/incidents/${encodeURIComponent(selectedIncidentId)}/area`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    });
    showFeedback("Área reasignada y añadida al historial.", "success");
    await refreshAll();
    await loadIncidentDetails(selectedIncidentId);
  } catch (error) {
    showFeedback(error.message, "error");
  }
});

document.querySelector("#closeDetails").addEventListener("click", () => {
  selectedIncidentId = null;
  elements.detailsPanel.hidden = true;
});

initializeBackoffice();
