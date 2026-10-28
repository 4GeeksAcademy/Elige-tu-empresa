---
id: "05-desarrollo-guiado-por-spec"
aplicacion: "siempre"
alcance: "Todo cambio de código, spec, plan y tareas del gestor de inventario (`specs/inventory-manager/`) y sus commits"
justificacion_aplicacion: "El orden spec → plan → tareas → código gobierna cada paso de este encargo, así que la regla afecta a cualquier tarea"
applyTo: "**"
origen: "encargo"
evidencia:
  - "memory-bank/encargo.md §1 (Cómo se trabaja: Spec Driven Development): primero el spec, criterios EARS con ID, tareas pequeñas, trazabilidad y cambios de requisito en orden spec → plan → tareas"
  - "memory-bank/encargo.md §5: la línea `Checklist:` del commit lleva `T-NN (INV-…)` en las implementaciones y `spec vX.Y`, `plan vX.Y` o `tasks vX.Y` en las otras capas"
  - "memory-bank/encargo.md §6, Paso 02 y Paso 08: contenido de esta regla y orden de un cambio de requisito"
---

# Desarrolla solo desde una tarea del spec

## Se hace
- Antes de cambiar código, comprueba que existe en `specs/inventory-manager/tasks.md` una tarea que cita al menos un `INV` y que ese `INV` existe en `specs/inventory-manager/spec.md`.
- Escribe el commit de implementación con `Checklist: T-NN (INV-…)` y con el ámbito `inventory`.
- Escribe los commits de las otras capas con `Checklist: spec vX.Y (INV-001–INV-0NN)`, `plan vX.Y` o `tasks vX.Y` y con el ámbito `specs`.
- Incluye el ID del criterio en el nombre de cada test, en camelCase (por ejemplo, `testInv012RejectsOutboundBelowZero`).
- Ante un cambio de requisito, haz un commit por capa y en este orden:
  1. el spec, con la versión nueva y una entrada en su historial de cambios;
  2. el plan, solo si le afecta, con una entrada en su historial de cambios;
  3. las tareas afectadas, con IDs nuevos;
  4. el código, un commit por tarea regenerada.
- Marca `retirado` un criterio que deja de aplicar y `sustituida por T-xx` una tarea que deja de aplicar.

## No se hace
- Cambiar código sin una tarea de `tasks.md`.
- Editar el spec, el plan o las tareas para que cuadren con código ya escrito.
- Crear una tarea que agrupe criterios sin relación entre sí.
- Reescribir el spec o la lista de tareas completos por un cambio puntual: se editan solo las secciones y las tareas afectadas.
- Renumerar o reutilizar un ID de criterio (`INV-xxx`) o de tarea (`T-xx`).

## Cómo comprobarlo
- `git log --format='%h %s%n%b' --grep='^feat(inventory)\|^test(inventory)' | grep -c 'Checklist: T-.*INV-'` es igual a `git log --oneline --grep='^feat(inventory)\|^test(inventory)' | wc -l`.
- `git log --format='%h %s' -- specs/inventory-manager/spec.md` lista el commit del cambio de spec antes (más abajo en el log) que los commits de código del mismo cambio.
- `grep -o 'INV-[0-9]\{3\}' specs/inventory-manager/spec.md | sort | uniq -d` devuelve los IDs repetidos en la tabla de criterios: cada ID aparece en una sola fila.
- `grep -rho 'testInv[0-9]\{3\}' services/api/tests | sort -u` cubre todos los `INV` no retirados del spec.

## Ejemplo
- ✅ `feat(inventory): rechazar salidas que dejan stock negativo`, con cuerpo `Paso: 06`, `Checklist: T-07 (INV-012)` y el test `testInv012RejectsOutboundBelowZero`.
- ❌ Un commit `feat(inventory)` sin `T-` ni `INV-`, o un commit que modifica el spec para describir un comportamiento que el código ya implementó.
