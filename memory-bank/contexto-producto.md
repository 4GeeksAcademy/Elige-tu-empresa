# Contexto de producto — Brasaland

> Paso 09, actualizado en la ronda 09b. Fuente de dominio: `../CONTEXT.md`. Las propuestas derivadas y los catálogos de abajo fueron validados por el usuario; no se presentan como valores literales del briefing.

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
WhatsApp, teléfono y email se validaron como canales de registro manual, sin integración automática.

## Quién usa el backoffice

Los nombres y funciones son literales de «Cómo está organizada la empresa» y «Los departamentos y sus problemas». Las necesidades del gestor son derivadas y fueron validadas por el usuario; no se definen permisos.

| Persona o rol del briefing | Necesidad propuesta para el gestor |
|---|---|
| Felipe Guerrero y supervisores de Operaciones de Restaurante | Registrar y seguir problemas operativos de los locales y conocer su responsable |
| Lucía Fernández, Compras y Proveedores | Consultar y gestionar incidencias de abastecimiento y proveedores |
| Camila Ospina, Marketing y Experiencia Digital | Seguir problemas de la web, la app y la experiencia digital |
| Ashley Turner, Personas y Cultura | Seguir problemas administrativos y de incorporación de personal |
| Jake Morrison, Formación y Estándares de Calidad | Seguir problemas de consulta o distribución de recetas y procedimientos |
| Nicolás Park y el equipo de Tecnología | Gestionar problemas técnicos y su trazabilidad |
| Mariana Restrepo, Dirección Ejecutiva | Consultar el volumen y la situación de incidencias abiertas; no recibe asignaciones |

## Qué es una incidencia en esta operación

Propuesta derivada: un problema concreto que afecta la operación de Brasaland y necesita clasificación, responsable y seguimiento. Ejemplos hipotéticos, no sucesos constatados ni tipos aprobados:

- Rotura de stock de ingredientes en un local: «Operaciones de restaurante» describe roturas y pedidos sin datos de inventario.
- Un local no registra ventas durante su horario de apertura: esa misma sección pide alertas para esta condición.
- Un cambio de receta no llega a todos los locales: «Formación y estándares de calidad» describe demoras y confusión al distribuir actualizaciones.
- Un cambio de precio de un proveedor se detecta al recibir la factura: «Compras y proveedores» describe esta falta de visibilidad.

No se asignan nombres a locales: el briefing no ofrece un catálogo de establecimientos.

## Qué significa «crítica» aquí

El briefing no define severidades ni umbrales de impacto. Criterio **derivado y validado por el usuario**: una incidencia es crítica si impide que un local opere o atienda clientes durante su horario de apertura; una rotura de ingredientes que impida servir pedidos es un ejemplo.
La ausencia de registros de ventas por sí sola no demuestra una interrupción y no se clasifica automáticamente como crítica.
No se fijan plazos, SLA, umbrales económicos ni reglas de escalado.

## Catálogos

### Áreas responsables

Las etiquetas siguientes son literales de «Cómo está organizada la empresa». Su uso como áreas asignables se validó con el usuario para las seis áreas operativas; Dirección Ejecutiva es de consulta y no recibe asignaciones. Los identificadores siguen la convención validada de `camelCase` ASCII, con etiquetas visibles en español.

| Etiqueta exacta | Identificador en código | Asignable | Origen |
|---|---|---|
| Operaciones de Restaurante | `operacionesRestaurante` | Sí | literal: «Cómo está organizada la empresa»; asignabilidad validada por el usuario |
| Compras y Proveedores | `comprasProveedores` | Sí | literal: «Cómo está organizada la empresa»; asignabilidad validada por el usuario |
| Marketing y Experiencia Digital | `marketingExperienciaDigital` | Sí | literal: «Cómo está organizada la empresa»; asignabilidad validada por el usuario |
| Personas y Cultura | `personasCultura` | Sí | literal: «Cómo está organizada la empresa»; asignabilidad validada por el usuario |
| Formación y Estándares de Calidad | `formacionEstandaresCalidad` | Sí | literal: «Cómo está organizada la empresa»; asignabilidad validada por el usuario |
| Tecnología | `tecnologia` | Sí | literal: «Cómo está organizada la empresa»; asignabilidad validada por el usuario |
| Dirección Ejecutiva | `direccionEjecutiva` | No, consulta | literal: «Cómo está organizada la empresa»; uso de consulta validado por el usuario |

### Canales

El briefing menciona estos medios, pero no define un catálogo de entrada de incidencias. Su uso como canales de registro manual se validó por el usuario; no implica integración automática. Los identificadores siguen la convención validada de `camelCase` ASCII.

| Etiqueta | Identificador en código | Origen |
|---|---|---|
| WhatsApp | `whatsapp` | derivado y validado: «Operaciones de restaurante» lo usa para pedidos de ingredientes; se adopta como canal manual de registro |
| teléfono | `telefono` | derivado y validado: «Operaciones de restaurante» lo usa para pedidos; se adopta como canal manual de registro |
| email | `email` | derivado y validado: «Compras y proveedores» y «Personas y cultura» lo usan en sus procesos; se adopta como canal manual de registro |

### Tipos, severidades y estados

El briefing describe problemas pero no define una taxonomía de incidencias. Estos tipos se derivan de los problemas descritos y fueron validados por el usuario.

| Tipo de incidencia | Identificador en código | Origen |
|---|---|---|
| Operación de Restaurante | `operacionRestaurante` | derivado y validado: «Operaciones de restaurante» describe roturas de stock y falta de registros de ventas |
| Compras y Proveedores | `comprasProveedores` | derivado y validado: «Compras y proveedores» describe falta de visibilidad de compras y cambios de precios |
| Marketing y Experiencia Digital | `marketingExperienciaDigital` | derivado y validado: «Marketing y experiencia digital» describe problemas de la web y la app |
| Personas y Cultura | `personasCultura` | derivado y validado: «Personas y cultura» describe carga administrativa y dificultades de onboarding |
| Formación y Calidad | `formacionCalidad` | derivado y validado: «Formación y estándares de calidad» describe dificultades con recetas y distribución de actualizaciones |
| Tecnología | `tecnologia` | derivado y validado: «Tecnología» describe sistemas de punto de venta distintos, ausencia de API e infraestructura digital mínima |

El briefing no enumera niveles de severidad. Se validó la siguiente escala derivada, ligada al impacto descrito en la operación:

| Severidad | Identificador en código | Criterio | Origen |
|---|---|---|---|
| Crítica | `critica` | Un local no puede operar o atender clientes durante su horario de apertura | derivado y validado: «Operaciones de restaurante» describe la operación de cada local y roturas de stock; la ausencia de registros de ventas no basta por sí sola |
| Alta | `alta` | Una función esencial de ventas o pedidos no está disponible, aunque el local pueda seguir atendiendo | derivado y validado: «Operaciones de restaurante» describe pedidos por WhatsApp/teléfono y alertas por falta de registros de ventas |
| Media | `media` | Un proceso operativo está afectado, pero existe una alternativa manual | derivado y validado: «Operaciones de restaurante», «Compras y proveedores» y «Personas y cultura» describen procesos con WhatsApp, teléfono, email, papel o Excel |
| Baja | `baja` | No hay interrupción operativa inmediata | derivado y validado: «Dónde está la empresa hoy» y las secciones de departamentos describen brechas de visibilidad y tareas administrativas sin afirmar una interrupción inmediata |

El briefing no define estados ni transiciones. Se validó este flujo derivado del requisito de seguimiento y cierre del encargo:

| Estado | Identificador en código | Transición |
|---|---|---|
| Nueva | `nueva` | Estado inicial al registrar |
| En curso | `enCurso` | Desde Nueva; también desde Resuelta antes del cierre |
| Resuelta | `resuelta` | Desde En curso |
| Cerrada | `cerrada` | Desde Resuelta; estado final, sin reapertura |

Los identificadores de tipos, severidades y estados usan `camelCase` ASCII; las etiquetas visibles conservan español y tildes.

## Glosario de entidades

| Nombre de dominio | Identificador en código | Fuente y estado |
|---|---|---|
| Brasaland | `brasaland` | literal: introducción |
| Área | `area` | derivado: las áreas se enumeran en «Cómo está organizada la empresa» |
| Local / restaurante | `restaurante` | literal: introducción y «Operaciones de restaurante»; sin catálogo de nombres |
| Proveedor | `proveedor` | literal: «Compras y proveedores»; sin catálogo de nombres |
| Incidencia | `incidencia` | requisito del encargo; el briefing no define esta entidad |
| Evento de historial | `eventoHistorial` | requisito de trazabilidad del encargo; no es una entidad definida en el briefing |

Los identificadores del glosario usan `camelCase` ASCII según la convención validada por el usuario.

## Gestor de inventario

El inventario es un producto separado del gestor de incidencias y cubre artículos, movimientos de entrada/salida/ajuste, lotes, existencias derivadas, reorden e informes para los cuatro locales acordados. Su alcance, catálogos y reglas aprobadas están especificados en [`specs/inventory-manager/spec.md`](../specs/inventory-manager/spec.md); esta memoria no duplica esos requisitos. La implementación comparte SQLite con el servicio existente y el detalle técnico está en [`stack-tecnologico.md`](./stack-tecnologico.md).

## Fuera de alcance

- Construir los demás productos solicitados en el briefing: CRM, fidelización, pedidos, RRHH, formación, compras y dashboards de ventas.
- Integrar automáticamente WhatsApp, email, teléfono o puntos de venta; los tres primeros son canales manuales, no integraciones.
- Inventar locales, proveedores, usuarios, permisos, SLA o valores de catálogo.
- Elegir stack, persistencia o identidad en este paso; corresponden a las siguientes fases del encargo.

## Validación

- En 2026-10-27, el usuario validó las necesidades propuestas para los roles, seis áreas asignables, Dirección Ejecutiva como consulta, canales manuales, tipos, severidades, criterio de «crítica», estados y transiciones, y la convención `camelCase` ASCII para IDs.
- Estos valores que no aparecen literalmente en el briefing están marcados como derivados y enlazados con su base y razonamiento.
- No se definieron permisos, SLA, integraciones, catálogos de locales/proveedores ni tecnologías de implementación.
