"""Validated domain catalogs for Brasaland incidents."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CatalogEntry:
    id: str
    label: str
    assignable: bool = True


channels = (
    CatalogEntry("whatsapp", "WhatsApp"),
    CatalogEntry("telefono", "teléfono"),
    CatalogEntry("email", "email"),
)

incidentTypes = (
    CatalogEntry("operacionRestaurante", "Operación de Restaurante"),
    CatalogEntry("comprasProveedores", "Compras y Proveedores"),
    CatalogEntry("marketingExperienciaDigital", "Marketing y Experiencia Digital"),
    CatalogEntry("personasCultura", "Personas y Cultura"),
    CatalogEntry("formacionCalidad", "Formación y Calidad"),
    CatalogEntry("tecnologia", "Tecnología"),
)

severities = (
    CatalogEntry("critica", "Crítica"),
    CatalogEntry("alta", "Alta"),
    CatalogEntry("media", "Media"),
    CatalogEntry("baja", "Baja"),
)

responsibleAreas = (
    CatalogEntry("operacionesRestaurante", "Operaciones de Restaurante"),
    CatalogEntry("comprasProveedores", "Compras y Proveedores"),
    CatalogEntry("marketingExperienciaDigital", "Marketing y Experiencia Digital"),
    CatalogEntry("personasCultura", "Personas y Cultura"),
    CatalogEntry("formacionEstandaresCalidad", "Formación y Estándares de Calidad"),
    CatalogEntry("tecnologia", "Tecnología"),
    CatalogEntry("direccionEjecutiva", "Dirección Ejecutiva", assignable=False),
)

statuses = (
    CatalogEntry("nueva", "Nueva"),
    CatalogEntry("enCurso", "En curso"),
    CatalogEntry("resuelta", "Resuelta"),
    CatalogEntry("cerrada", "Cerrada"),
)

catalogs = {
    "channels": channels,
    "incidentTypes": incidentTypes,
    "severities": severities,
    "responsibleAreas": responsibleAreas,
    "statuses": statuses,
}

units = (
    CatalogEntry("kg", "kg"),
    CatalogEntry("g", "g"),
    CatalogEntry("l", "l"),
    CatalogEntry("ml", "ml"),
    CatalogEntry("unit", "unit"),
)

categories = (
    CatalogEntry("meat", "meat"),
    CatalogEntry("produce", "produce"),
    CatalogEntry("sauces_condiments", "sauces_condiments"),
    CatalogEntry("beverages", "beverages"),
    CatalogEntry("packaging", "packaging"),
    CatalogEntry("cleaning_supplies", "cleaning_supplies"),
)

movementTypes = (
    CatalogEntry("inbound", "inbound"),
    CatalogEntry("outbound", "outbound"),
    CatalogEntry("adjustment", "adjustment"),
)

adjustmentReasons = (
    CatalogEntry("waste", "waste"),
    CatalogEntry("theft", "theft"),
    CatalogEntry("count_correction", "count_correction"),
)

locations = (
    CatalogEntry("laArepita", "La Arepita (Colombia)"),
    CatalogEntry("queChille", "QueChille (Colombia)"),
    CatalogEntry("theBigSauce", "The BigSauce (Estados Unidos, Florida)"),
    CatalogEntry("chilliBeans", "ChilliBeans (Estados Unidos, Florida)"),
)

inventoryCatalogs = {
    "units": units,
    "categories": categories,
    "movementTypes": movementTypes,
    "adjustmentReasons": adjustmentReasons,
    "locations": locations,
}


def catalogIds(catalogName: str, assignableOnly: bool = False) -> tuple[str, ...]:
    try:
        entries = {**catalogs, **inventoryCatalogs}[catalogName]
    except KeyError as error:
        raise ValueError(f"Unknown catalog: {catalogName}") from error

    return tuple(
        entry.id
        for entry in entries
        if not assignableOnly or entry.assignable
    )
