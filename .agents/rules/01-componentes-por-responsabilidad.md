---
id: "01-componentes-por-responsabilidad"
aplicacion: "agente"
alcance: "Creación, traslado o reorganización de aplicaciones, servicios, agentes y pipelines."
justificacion_aplicacion: "La regla interviene al decidir la ubicación y documentación de un componente, no en cambios que no afectan su estructura."
description: "Usa esta regla al crear, mover o reorganizar una aplicación, servicio, agente o pipeline."
origen: "codigo"
evidencia:
  - "README.es.md:29: cada app, servicio, agente o pipeline nuevo lleva subcarpeta y README."
  - "README.es.md:40-48: asigna responsabilidades a las carpetas de primer nivel."
  - "memory-bank/registro/convenciones.md:7-12: registra NC-01 y sus 13 áreas documentadas."
---

# Ubica y documenta cada componente en su área responsable

## Se hace
- Consulta la guía raíz y ubica cada componente en la carpeta de primer nivel que corresponda a su responsabilidad.
- Crea una subcarpeta para cada nueva aplicación, servicio, agente o pipeline y documenta el componente con una guía de carpeta.
- Si la guía no asigna una responsabilidad al componente, pregunta antes de crear una carpeta de primer nivel nueva.

## No se hace
- No coloques un componente directamente en la raíz del repositorio.
- No añadas una carpeta de primer nivel cuya responsabilidad no esté documentada.

## Cómo comprobarlo
- Contrasta el directorio del componente con la tabla de responsabilidades de la guía raíz.
- Comprueba que cada nueva aplicación, servicio, agente o pipeline tenga una subcarpeta y una guía de carpeta.

## Ejemplo
- ✅ Crear un servicio en `services/<componente>/` y documentar esa carpeta.
- ❌ Añadir el servicio directamente en la raíz sin una carpeta responsable ni guía.

## Prueba asociada
- NC-01 en `memory-bank/registro/pruebas-reglas.md`.
