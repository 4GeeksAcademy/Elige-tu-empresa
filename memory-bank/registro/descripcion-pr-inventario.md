# Pull Request — gestor de inventario Brasaland

## 1. Resumen

Implementa el gestor de inventario para los cuatro locales acordados: alta, edición, listado y baja de artículos; movimientos de entrada, salida y ajuste; control de lotes y caducidad; señal de reorden e informes de stock en el backoffice. El stock disponible se deriva exclusivamente de movimientos y los rechazos de negocio se devuelven con el estado HTTP definido en el contrato.

## 2. Spec, plan y tareas

- [Spec v1.0, aprobado](../../specs/inventory-manager/spec.md): criterios INV-001–INV-066.
- [Plan v1.0](../../specs/inventory-manager/plan.md): decisiones PD-01–PD-16.
- [Tareas v1.0](../../specs/inventory-manager/tasks.md): T-01–T-29, todas completadas.

## 3. Trazabilidad requisito → test → commit

La matriz completa de cada criterio, tarea, métodos de prueba y commit está en [trazabilidad-inventario.md](./trazabilidad-inventario.md). Los resultados de la suite y el recorrido HTTP real están en [verificacion-inventario.md](./verificacion-inventario.md).

## 4. Cambio de requisito

No se recibió ni aplicó un cambio de requisito durante este encargo; el Paso 08 no se activó. Por tanto, el spec permanece en v1.0 y no se regeneraron tareas.

## 5. Cómo verificar

Desde la raíz del repositorio:

```bash
# Suite completa (188 pruebas al cierre de la verificación)
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v

# Cargar semilla en la base predeterminada; esta debe estar vacía de artículos
PYTHONDONTWRITEBYTECODE=1 python -m services.api.inventoryseed

# Iniciar API y backoffice desde el mismo origen
PYTHONDONTWRITEBYTECODE=1 python -m services.api.server
```

La semilla acepta `--database <ruta>` para usar un SQLite distinto, por ejemplo una base temporal. El servidor del comando usa `data/incidents.sqlite`; para apuntar a una base temporal se crea con `createServer(databasePath)` desde `services.api.server`. La semilla no sobrescribe inventario existente. El recorrido HTTP que se ejecutó con una base temporal y la limitación de no contar con inspección visual en navegador están documentados en el registro de verificación.

## 6. Reglas que evitaron desviaciones

- **00 — commits y bitácora:** un commit por paso/tarea, historial actualizado y archivos acotados al paso; sin publicación ni merge antes de autorización.
- **01 — componentes por responsabilidad y 03 — paquetes/recursos compartidos:** servicio en `services/api/`, interfaz en `uis/backoffice/`, sin nuevos paquetes ni carpetas superiores.
- **02 — guías bilingües:** documentación de API y backoffice actualizada en español e inglés.
- **04 — nombres camelCase:** IDs y valores de catálogo respetan la convención validada.
- **05 — desarrollo guiado por spec:** orden spec → plan → tareas → implementación; cada tarea cita criterios INV y los métodos de prueba incluyen el ID.

**Nota de auditoría del historial:** `2b6a7f5` (registro del Paso 07) no contiene el cuerpo `Paso:`/`Checklist:` requerido por la regla 00. Se conserva el commit tal como fue creado, sin reescritura; los 29 commits de implementación fueron auditados y todos incluyen `T-*` e `INV-*`. El cambio se deja señalado para revisión.
