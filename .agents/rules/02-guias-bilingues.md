---
id: "02-guias-bilingues"
aplicacion: "patron"
alcance: "Guías nuevas o modificadas que documentan carpetas del proyecto; no requiere traducir retroactivamente memory-bank/README.md."
justificacion_aplicacion: "El patrón limita la carga a los archivos README, que son las guías de carpeta cubiertas por esta regla."
applyTo: "**/README*.md"
origen: "codigo"
evidencia:
  - "README.es.md:8: enlaza la versión en inglés de la guía raíz."
  - "memory-bank/registro/convenciones.md:14-19: registra 20 pares y memory-bank/README.md como excepción sin pareja."
---

# Mantén las guías de carpeta en español e inglés

## Se hace
- Para cada guía de carpeta nueva o modificada, mantén `README.es.md` en español y `README.md` en inglés en la misma carpeta.
- Mantén equivalentes las instrucciones, rutas, comandos y advertencias de ambas versiones.

## No se hace
- No dejes una guía de carpeta del proyecto únicamente en uno de esos idiomas.
- No traduzcas retroactivamente `memory-bank/README.md` por aplicación de esta regla.

## Cómo comprobarlo
- Para cada carpeta con un README nuevo o modificado, comprueba que existen ambos nombres de archivo.
- Compara las dos versiones y verifica que coincidan las instrucciones, rutas, comandos y advertencias, cada una en su idioma.

## Ejemplo
- ✅ Crear `README.es.md` y `README.md` con la misma orientación de carpeta en español e inglés.
- ❌ Crear solo `README.md` para una nueva carpeta de componente.

## Prueba asociada
- NC-02 en `memory-bank/registro/pruebas-reglas.md`.
