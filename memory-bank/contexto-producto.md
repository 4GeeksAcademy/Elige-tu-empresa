# Contexto de producto — Brasaland

> Paso 09. Fuente de dominio: `../CONTEXT.md`. Borrador pendiente de validación del usuario; no autoriza catálogos ni código.

## La empresa

Brasaland es una cadena de cocina a la brasa fundada en 2008 en Medellín.
Opera 14 restaurantes propios en Colombia y Florida (Estados Unidos).
Emplea unas 115 personas y factura alrededor de 6 millones de dólares anuales.
La sede está en Medellín y una oficina en Miami coordina los locales de Florida.
Mariana Restrepo es CEO desde 2019; Nicolás Park dirige Tecnología desde Medellín.
Brasaland Digital es el equipo interno encargado de modernizar sistemas y automatizaciones.
La operación depende de herramientas dispersas, sin visibilidad consolidada en tiempo real.
Fuente: introducción, «Cómo está organizada la empresa» y «Dónde está la empresa hoy».

## El problema

El encargo pide centralizar incidencias, clasificarlas, asignarlas y conservar su historial.
En Brasaland esto debe dar visibilidad sobre problemas de una operación repartida entre dos países y 14 locales, hoy dependiente de WhatsApp, teléfono, email, Excel e informes en papel.
El briefing describe esos medios y problemas, pero no define un sistema de incidencias ni sus catálogos.
No se presupone que todos esos medios deban integrarse automáticamente.

## Quién usa el backoffice

Los nombres y funciones son literales de «Cómo está organizada la empresa» y «Los departamentos y sus problemas». Las necesidades del gestor de esta tabla son derivadas y requieren validación; el briefing no asigna permisos.

| Persona o rol del briefing | Necesidad propuesta para el gestor |
|---|---|
| Felipe Guerrero y supervisores de Operaciones de Restaurante | Registrar y seguir problemas operativos de los locales y conocer su responsable |
| Lucía Fernández, Compras y Proveedores | Consultar y gestionar incidencias de abastecimiento y proveedores |
| Camila Ospina, Marketing y Experiencia Digital | Seguir problemas de la web, la app y la experiencia digital |
| Ashley Turner, Personas y Cultura | Seguir problemas administrativos y de incorporación de personal |
| Jake Morrison, Formación y Estándares de Calidad | Seguir problemas de consulta o distribución de recetas y procedimientos |
| Nicolás Park y el equipo de Tecnología | Gestionar problemas técnicos y su trazabilidad |
| Mariana Restrepo, Dirección Ejecutiva | Consultar el volumen y la situación de incidencias abiertas |

## Qué es una incidencia en esta operación

Propuesta derivada: un problema concreto que afecta la operación de Brasaland y necesita clasificación, responsable y seguimiento. Ejemplos hipotéticos, no sucesos constatados ni tipos aprobados:

- Rotura de stock de ingredientes en un local: «Operaciones de restaurante» describe roturas y pedidos sin datos de inventario.
- Un local no registra ventas durante su horario de apertura: esa misma sección pide alertas para esta condición.
- Un cambio de receta no llega a todos los locales: «Formación y estándares de calidad» describe demoras y confusión al distribuir actualizaciones.
- Un cambio de precio de un proveedor se detecta al recibir la factura: «Compras y proveedores» describe esta falta de visibilidad.

No se asignan nombres a locales: el briefing no ofrece un catálogo de establecimientos.

## Qué significa «crítica» aquí

**Pendiente.** El briefing no define severidades ni umbrales de impacto.
Propuesta derivada para validar: considerar crítica una incidencia que impida mantener la operación de un local durante su horario de apertura, por ejemplo una rotura de ingredientes que impida servir pedidos.
La ausencia de registros de ventas por sí sola no demuestra una interrupción y no se clasifica automáticamente como crítica.
No se fijan plazos, SLA, umbrales económicos ni reglas de escalado.

## Catálogos

### Áreas responsables

Las etiquetas siguientes son literales de «Cómo está organizada la empresa». Su uso como áreas asignables es derivado y está pendiente de validación.
Todos los identificadores en código están **pendientes**: no se ha establecido una convención de identificadores de dominio para el gestor.

| Etiqueta exacta | Identificador en código | Origen |
|---|---|---|
| Operaciones de Restaurante | pendiente | literal: «Cómo está organizada la empresa» |
| Compras y Proveedores | pendiente | literal: «Cómo está organizada la empresa» |
| Marketing y Experiencia Digital | pendiente | literal: «Cómo está organizada la empresa» |
| Personas y Cultura | pendiente | literal: «Cómo está organizada la empresa» |
| Formación y Estándares de Calidad | pendiente | literal: «Cómo está organizada la empresa» |
| Tecnología | pendiente | literal: «Cómo está organizada la empresa» |
| Dirección Ejecutiva | pendiente | literal: «Cómo está organizada la empresa» |

### Canales

El briefing menciona medios de comunicación, pero no define un catálogo de entrada de incidencias. Estos son candidatos, no valores aprobados.

| Etiqueta del briefing | Identificador en código | Origen de la candidatura |
|---|---|---|
| WhatsApp | pendiente | derivado: «Operaciones de restaurante» lo usa para pedidos de ingredientes; no confirma recepción de incidencias |
| teléfono | pendiente | derivado: «Operaciones de restaurante» lo usa para pedidos; no confirma recepción de incidencias |
| email | pendiente | derivado: «Compras y proveedores» y «Personas y cultura» lo usan en sus procesos; no confirma recepción de incidencias |

### Tipos, severidades y estados

| Catálogo | Etiquetas | Identificadores en código | Origen |
|---|---|---|---|
| Tipos de incidencia | pendiente | pendiente | pendiente: el briefing describe problemas, no una taxonomía de incidencias |
| Severidades | pendiente | pendiente | pendiente: el briefing no enumera niveles ni criterios |
| Estados y transiciones | pendiente | pendiente | pendiente: el briefing no define un ciclo de incidencias |

La palabra «crítica» del encargo no basta para inventar el resto de niveles. El requisito de cierre tampoco autoriza a inventar nombres de estados.

## Glosario de entidades

| Nombre de dominio | Identificador en código | Fuente y estado |
|---|---|---|
| Brasaland | pendiente | literal: introducción |
| Área | pendiente | derivado: organización de la empresa |
| Local / restaurante | pendiente | literal: introducción y «Operaciones de restaurante»; sin catálogo de nombres |
| Proveedor | pendiente | literal: «Compras y proveedores»; sin catálogo de nombres |
| Incidencia | pendiente | requisito del encargo; el briefing no define esta entidad |
| Evento de historial | pendiente | requisito de trazabilidad del encargo; no es una entidad definida en el briefing |

## Fuera de alcance

- Construir los demás productos solicitados en el briefing: CRM, fidelización, pedidos, RRHH, formación, compras y dashboards de ventas.
- Integrar automáticamente WhatsApp, correo, telefonía o puntos de venta sin aprobación.
- Inventar locales, proveedores, usuarios, permisos, SLA o valores de catálogo.
- Elegir stack, persistencia o identidad en este paso; corresponden a las siguientes fases del encargo.

## Validación pendiente

- Confirmar usuarios y necesidades propuestas del gestor.
- Confirmar qué áreas son asignables y qué medios son canales de entrada.
- Definir tipos, severidades, criterio de «crítica» y estados con sus transiciones.
- Aprobar la convención de identificadores en código antes de asignarlos.
- El usuario debe aportar o aprobar explícitamente los valores ausentes del briefing antes de implementarlos.
