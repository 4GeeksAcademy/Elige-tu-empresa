---
id: "03-paquetes-y-recursos-compartidos"
aplicacion: "agente"
alcance: "Creación o traslado de código reutilizable y recursos compartidos entre packages/ y shared/."
justificacion_aplicacion: "La regla se necesita al decidir si un elemento reutilizable es código empaquetable o un recurso compartido no empaquetado."
description: "Usa esta regla al decidir dónde crear o mover código reutilizable o recursos compartidos entre packages/ y shared/."
origen: "codigo"
evidencia:
  - "README.es.md:169-180: describe packages/ como código versionable reutilizado."
  - "README.es.md:182-189: describe shared/ como recursos no empaquetados."
  - "packages/README.es.md:3-5: describe código reutilizable y paquetes versionables."
  - "shared/README.es.md:3: enumera recursos compartidos no empaquetados."
  - "memory-bank/registro/convenciones.md:21-26: registra NC-03 y el package.json existente bajo packages/shared/."
---

# Separa los paquetes de los recursos compartidos no empaquetados

## Se hace
- Ubica el código reutilizable como paquete bajo `packages/`.
- Ubica en `shared/` los recursos compartidos que no se empaquetan, como esquemas, plantillas, assets, documentación técnica breve o configuraciones.
- Crea cada paquete nuevo en una subcarpeta propia y documenta su propósito, API pública y forma de consumo en un README.
- Documenta los recursos añadidos a `shared/` y enlázalos desde los componentes que los consumen.

## No se hace
- No coloques en `shared/` código reutilizable que se mantenga como paquete.
- No crees en `packages/` un recurso que no constituye un paquete solo porque lo compartan varios componentes.

## Cómo comprobarlo
- Contrasta cada elemento nuevo o trasladado con las definiciones de `packages/README.es.md` y `shared/README.es.md`.
- Comprueba que cada paquete nuevo tenga su subcarpeta y README propio.
- Comprueba que cada recurso nuevo en `shared/` esté documentado y enlazado desde sus consumidores.

## Ejemplo
- ✅ Colocar una biblioteca reutilizable en `packages/<paquete>/` y una plantilla común no empaquetada en `shared/`.
- ❌ Guardar una biblioteca reutilizable en `shared/` solo porque ya contiene otros recursos comunes.

## Prueba asociada
- NC-03 en `memory-bank/registro/pruebas-reglas.md`.
