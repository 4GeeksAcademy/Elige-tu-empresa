# Propuesta de Pull Request — Gestor centralizado de incidencias

## 1. Resumen

El trabajo organiza el repositorio con reglas verificables y memoria de proyecto, y entrega un gestor de incidencias para Brasaland. El gestor usa SQLite y biblioteca estándar de Python; expone una API JSON con `http.server` y sirve un backoffice estático desde el mismo origen. La interfaz permite registrar y clasificar incidencias, asignarlas, filtrarlas, consultar su historial, cambiar estado o área y ver el volumen abierto por severidad.

No se añaden dependencias de aplicación. No se incluyen autenticación, integraciones automáticas con los canales ni despliegue. El Paso 20 añade los ejemplos solicitados de importación, guía en inglés y función compartida.

## 2. Cómo trabaja el agente

- `AGENTS.md` define dónde viven las reglas, la memoria y el encargo, además del ciclo de trabajo y la aprobación necesaria antes de commitear.
- `.agents/rules/` contiene reglas separadas por preocupación y forma de aplicación.
- `memory-bank/` conserva el encargo, el contexto de Brasaland, el stack, el estado, el plan versionado y la evidencia.
- La fuente de los valores de dominio es `CONTEXT.md`; los valores derivados y catálogos se validaron con el usuario y se reflejan en `memory-bank/contexto-producto.md`.

## 3. Discrepancias entre el resumen inicial y el repositorio

El resumen inicial era una instantánea del repositorio anterior a varios commits. El contraste registrado en `memory-bank/registro/discrepancias.md` distingue lo correcto, lo impreciso y lo obsoleto: el checkout es Brasaland, `CONTEXT.md` contiene el briefing real, el agente de ejemplo estaba vacío y las recomendaciones de carpetas describían arquitectura prevista, no servicios implementados. También documenta que `pyproject.toml` y `uv.lock` aparecieron después del resumen para un entorno Python vacío; el lockfile no se leyó ni modificó en este trabajo.

## 4. Reglas definidas

| Regla | Aplicación | Alcance | Evidencia en el código |
|---|---|---|---|
| 00 — Commits y bitácora | Siempre | Cada paso, su commit, la bitácora y el estado | Commits con `Paso:` y `Checklist:`; `memory-bank/historial-commits.md` |
| 01 — Componentes por responsabilidad | Agente | Aplicaciones, servicios, agentes y pipelines | Servicio en `services/api/` con guía propia; backoffice en `uis/backoffice/` |
| 02 — Guías bilingües | Patrón `**/README*.md` | Guías de carpeta nuevas o modificadas | Pares `README.es.md` y `README.md` en `services/api/` y `uis/backoffice/` |
| 03 — Paquetes y recursos compartidos | Agente | Código empaquetable frente a recursos de `shared/` | `packages/shared/` contiene el paquete; `shared/format-label.ts` es el ejemplo solicitado |
| 04 — Nombres camelCase | Siempre | Identificadores propiedad del proyecto y etiquetas de dominio | `services/api/server.py`, `services/api/incidents.py` y `uis/backoffice/app.js`; los nombres exigidos por HTTP conservan su forma protocolaria |

Las reglas de código NC-01–NC-03 se derivan de las guías y estructura existentes, según `memory-bank/registro/convenciones.md`.

## 5. Propuesta de mejora no aplicada

`PM-01` propone definir exclusiones locales y de secretos en `.gitignore`, que estaba vacío en el análisis. La propuesta documenta beneficio y riesgo; no se aplicó.

## 6. Reglas que evitaron desviaciones

`memory-bank/registro/pruebas-reglas.md` registra que, ante solicitudes experimentales de ubicar un componente en la raíz, omitir la guía en español o poner código empaquetable en `shared/`, el agente con reglas señaló el conflicto y se detuvo. El usuario aceptó ese resultado; no se atribuye a las reglas una creación que no ocurrió.

No existe un archivo `desviaciones-evitadas.md`: el cierre del Paso 18 retiró ese registro porque no existía evidencia que documentar. Para no inventar eventos, esta descripción cita la prueba controlada y la decisión registrada en `memory-bank/historial-commits.md`.

## 7. Cómo verificar el gestor

Desde la raíz del repositorio:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s services/api/tests -v
PYTHONDONTWRITEBYTECODE=1 python -m services.api.server
```

La suite pasa con 35 pruebas. Al iniciar el servidor, abrir `http://127.0.0.1:8000/`. El servidor crea `data/incidents.sqlite` y escucha en loopback por defecto. Node.js no está disponible en el entorno de verificación, por lo que no se ejecutó `node --check`.

## 8. Auditoría C01–C15 y mapa del checklist a los commits

La comparación de historial y manifiestos se hizo contra `origin/main`, tras autorización expresa para obtener esa referencia. Hay 23 commits entre `origin/main` y `HEAD`; los 23 incluyen `Paso:` y `Checklist:`. El diff de manifiestos identifica únicamente `pyproject.toml`, que declara `dependencies = []`; no se accedió a `uv.lock`.

| Criterio | Evidencia | Commit(s) | Resultado |
|---|---|---|---|
| C01 | Reglas 01–03 con `origen: codigo`, derivadas de convenciones del repositorio | `c3e6e02` | ✅ |
| C02 | Frontmatter de las cinco reglas declara aplicación y alcance | `647f20a`, `c3e6e02`, `0009ed6` | ✅ |
| C03 | Cada regla incluye acciones, prohibiciones y forma de comprobación | `647f20a`, `c3e6e02`, `0009ed6` | ✅ |
| C04 | Contexto, stack y estado en `memory-bank/` | `6297019`, `e29aaa3` | ✅ |
| C05 | `memory-bank/contexto-producto.md` describe empresa, operación y usuarios | `6297019` | ✅ |
| C06 | Plan versionado y alineado con API estándar y backoffice entregados | `7419deb`, `12cfc19`, `1430eb5` | ✅ |
| C07 | Contraste del resumen inicial en `memory-bank/registro/discrepancias.md` | `f3ea528` | ✅ |
| C08 | Registro y asignación en los casos de uso y API HTTP | `d568bd7`, `1430eb5` | ✅ |
| C09 | Transiciones de estado y ciclo hasta cierre | `99ba6b1`, `1430eb5` | ✅ |
| C10 | Ficha con historial, autor y marca temporal | `99ba6b1`, `1430eb5` | ✅ |
| C11 | Filtros por estado, severidad y área responsable | `e88b8ce`, `1430eb5` | ✅ |
| C12 | Conteos por severidad y tarjetas visibles en el backoffice | `ffb7701`, `1430eb5` | ✅ |
| C13 | Catálogos validados en contexto, persistencia y pruebas | `6297019`, `f7fb380`, `1430eb5` | ✅ |
| C14 | Biblioteca estándar, `dependencies = []` y ningún cambio de dependencia de aplicación | `3078274`, `1430eb5` | ✅ |
| C15 | Historial de 23 commits separados, cada uno con marcador de paso y checklist | Todos los commits de `origin/main..HEAD` | ✅ |

| Tarea / hito | Commit |
|---|---|
| E1, E3, RG1, BM1 | `647f20a` |
| RC1 | `21878b8` |
| E2 | `3078274` |
| RC2, RC3, C07 | `f3ea528` |
| RC4, RC5 | `a10cf11` |
| RG5 | `e6d3a95`, `d354891`, `ea2740a` |
| RG1–RG4, C01–C03 | `c3e6e02` |
| BM1, BM2, BM5, C05, C13 | `6297019` |
| BM1, C04, C14 | `e29aaa3` |
| BM3, C06 | `7419deb`, `12cfc19` |
| NC-01–NC-03 | `d455189` |
| C08 | `f7fb380`, `d568bd7`, `1430eb5` |
| C09–C10 | `99ba6b1`, `1430eb5` |
| C11 | `e88b8ce`, `1430eb5` |
| C12 | `ffb7701`, `1430eb5` |
| C13–C14 | `f7fb380`, `1430eb5` |
| V1 | `90017dd`, `1430eb5` |
| BM4 | `efd5492` |
| C06, C12, C14 — cambio a HTTP estándar | `12cfc19` |

No se hizo push ni se creó un Pull Request en esta fase; esas acciones requieren autorización explícita.
