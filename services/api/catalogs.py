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


def catalogIds(catalogName: str, assignableOnly: bool = False) -> tuple[str, ...]:
    try:
        entries = catalogs[catalogName]
    except KeyError as error:
        raise ValueError(f"Unknown catalog: {catalogName}") from error

    return tuple(
        entry.id
        for entry in entries
        if not assignableOnly or entry.assignable
    )
