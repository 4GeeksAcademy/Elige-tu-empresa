---
id: "04-nombres-camel-case"
aplicacion: "siempre"
alcance: "Nombres de identificadores propiedad del proyecto y etiquetas de identificadores de dominio; conserva las convenciones existentes para tipos y archivos."
justificacion_aplicacion: "El usuario pidió mantener camelCase en los identificadores, incluidos los IDs de dominio; la regla debe estar presente en todo trabajo."
applyTo: "**"
origen: "encargo"
evidencia:
  - "packages/shared/types/index.ts: los campos createdAt y updatedAt usan camelCase y la interfaz BaseEntity usa PascalCase."
  - "shared/format-label.ts: la función formatLabel usa camelCase y el archivo format-label.ts usa kebab-case."
  - "Usuario, 2026-10-27: pidió mantener camelCase y confirmó cambiar también los IDs de catálogos y entidades."
  - "Briefing, §2: «No inventes otros ni los renombres» (valores de catálogo del inventario). El archivo `company-BRIEFING.md` no existe; el usuario fijó `CONTEXT.md` como briefing el 2026-10-28."
---

# Mantén las convenciones camelCase del código

## Se hace
- Usa `camelCase` ASCII para variables, funciones, métodos, campos, propiedades, constantes e identificadores de dominio propiedad del proyecto.
- Usa `PascalCase` para tipos, interfaces y clases, siguiendo el patrón existente de `BaseEntity`.
- Conserva las etiquetas visibles para usuarios y los nombres impuestos por contratos externos, protocolos o interfaces obligatorias exactamente como los requiere su consumidor.
- Conserva literalmente los valores de catálogo que fija `company-BRIEFING.md` (por ejemplo, `sauces_condiments` o `inbound`), porque son un contrato externo.
- Mantén los nombres de archivos en el patrón ya establecido en su área; por ejemplo, `shared/format-label.ts`.
- Al modificar código existente, no renombres identificadores ajenos al alcance de la tarea solo para aplicar la convención retroactivamente.

## No se hace
- No introduzcas `snake_case` ni `UPPER_SNAKE_CASE` para nuevos identificadores propiedad del proyecto.
- No nombres tipos, interfaces o clases con `camelCase`.
- No cambies etiquetas de dominio visibles ni nombres exigidos por APIs, protocolos o herramientas externas para ajustarlos a esta regla.

## Cómo comprobarlo
- Revisa los identificadores nuevos o renombrados en el diff: valores, funciones, campos e IDs de dominio en `camelCase`; tipos, interfaces y clases en `PascalCase`.
- Comprueba que los nombres de archivos respetan el patrón de su área y que cada excepción de identificador corresponde a un contrato externo documentado.

## Ejemplo
- ✅ `operacionesRestaurante` como ID de área, `createdAt` como campo, `BaseEntity` como interfaz y `format-label.ts` como archivo.
- ❌ `operaciones_restaurante` como ID de dominio nuevo, `created_at` como campo nuevo o `baseEntity` como interfaz.
