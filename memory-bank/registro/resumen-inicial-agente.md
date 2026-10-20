> **Fecha:** 2026-10-20 · **Modo:** Ask
> Generado sin contexto previo. No editar: es la hipótesis de partida.

---

# Resumen del proyecto

## 1. Qué es

Es una plantilla educativa de monorepo para desarrollar, a lo largo de varios hitos de un programa de Ingeniería de IA, las herramientas de una empresa ficticia o asignada. La guía plantea aplicaciones web, servicios, datos, agentes de IA y automatizaciones, pero el estado actual es principalmente estructura y documentación: no hay una aplicación completa lista para ejecutar.

En este checkout, el contexto empresarial es **Brasaland**, una cadena de restaurantes que busca modernizar sus operaciones. `company-choice.md` propone como idea de proyecto un agente conversacional para gestionar reservas. La plantilla también menciona TrackFlow y Nexova como posibles empresas.

**Fuentes:** [README.es.md](./README.es.md), [CONTEXT.md](./CONTEXT.md), [company-choice.md](./company-choice.md).

## 2. Stack

- **Python:** hay una plantilla mínima de agente y un ejemplo de limpieza de datos con pandas. No se encontró un manifiesto Python que declare dependencias.
- **TypeScript:** hay tipos compartidos de ejemplo en `packages/shared/types/index.ts`.
- **Backend propuesto:** FastAPI aparece como arquitectura recomendada para `services/`, pero no hay una aplicación FastAPI implementada en este checkout.
- **Gestor de paquetes:** no se define uno para el repositorio. El único manifiesto localizado es `packages/shared/package.json`; no hay manifiesto raíz ni lockfile de workspace.
- **Base de datos:** no se especifica ni hay una configuración de base de datos presente.
- **Lint, formato y tests:** no se encontraron configuraciones o comandos de lint/formato/test. La plantilla de agente incluye una carpeta `tests/` documentada, pero no un runner configurado en la raíz.

Por tanto, Python, pandas y TypeScript están representados en ejemplos; FastAPI y Docker se proponen en la documentación. No hay configuración suficiente para considerar implementado o configurado un stack de ejecución.

**Fuentes:** [README.es.md](./README.es.md), [agents/_template/README.es.md](./agents/_template/README.es.md), [agents/_template/agent.py](./agents/_template/agent.py), [packages/shared/package.json](./packages/shared/package.json), [packages/shared/types/index.ts](./packages/shared/types/index.ts), [skills/data-analysis/scripts/pandas_clean.py](./skills/data-analysis/scripts/pandas_clean.py).

## 3. Estructura

- `agents/`: agentes de IA y herramientas asociadas. `_template/` es la base documentada para crear agentes; `tools/` tiene su propia guía.
- `skills/`: instrucciones y capacidades reutilizables. Incluye skills de revisión de código, análisis de datos y research; `data-analysis/` contiene recursos y un script pandas.
- `services/`: lugar previsto para la API centralizada de la empresa y, si hace falta, workers.
- `uis/`: aplicaciones y dashboards con los que interactúan usuarios u operadores.
- `data/`: ciclo de datos separado en `raw/` (fuentes), `pipelines/` (transformación), `process/` (salidas intermedias) y `eval/` (medición de calidad). El flujo descrito es `raw → pipelines → process`, cuyos resultados pueden consumir servicios, interfaces o agentes.
- `mcps/`: servidores MCP para conectar modelos con herramientas y sistemas.
- `workflows/`: automatizaciones y orquestaciones entre componentes, por ejemplo flujos n8n.
- `packages/`: código versionable reutilizable. `packages/shared/` contiene el paquete `@repo/shared-types` y tipos TypeScript de ejemplo.
- `shared/`: esquemas, plantillas y otros recursos comunes que no necesitan ser un paquete de código.
- `docs/`: documentación transversal, arquitectura y decisiones.
- `infra/`: configuración de infraestructura y despliegue.
- `scripts/`: scripts de ayuda pequeños; `internal/`: herramientas de desarrollo más estructuradas.
- En la raíz están las guías en español e inglés, `CONTEXT.md` con el briefing empresarial y `company-choice.md` con la idea de proyecto.

Las carpetas de la mayoría de estos componentes contienen guías, no implementaciones. La relación propuesta es que interfaces y agentes consuman los servicios y/o los datos preparados; `packages/` ofrece código compartido y `workflows/` conecta procesos.

**Fuentes:** [README.es.md](./README.es.md), [agents/README.es.md](./agents/README.es.md), [services/README.es.md](./services/README.es.md), [data/README.es.md](./data/README.es.md), [packages/README.es.md](./packages/README.es.md), [skills/README.es.md](./skills/README.es.md).

## 4. Puesta en marcha

La guía indica que se debe usar el repositorio como plantilla, crear el repositorio propio, clonarlo o abrirlo en Codespaces, sustituir `CONTEXT.md` por el briefing asignado, leer la guía de la carpeta de trabajo y añadir las aplicaciones o componentes en su ubicación correspondiente.

**No hay instrucciones de instalación de dependencias ni un comando para arrancar el proyecto en local**: no se encontró una configuración de aplicación raíz, gestor de workspace o `docker-compose.yml`. Aunque el README describe Docker Compose como ubicación prevista para orquestar el stack, ese archivo no está presente en este checkout. Por ello, todavía no hay un servicio o aplicación del monorepo que pueda iniciarse siguiendo un comando documentado.

Como ejemplo aislado, el script de análisis indica que puede ejecutarse con `python pandas_clean.py` desde su carpeta si pandas está instalado y se dispone de `data.csv`; el repositorio no proporciona los pasos para instalar pandas ni ese archivo de entrada.

**Fuentes:** [README.es.md](./README.es.md), [skills/data-analysis/scripts/pandas_clean.py](./skills/data-analysis/scripts/pandas_clean.py), [packages/shared/package.json](./packages/shared/package.json).

## 5. Convenciones

- Separar el contenido por responsabilidad y evitar colocar aplicaciones o scripts arbitrarios en la raíz.
- Crear una subcarpeta por aplicación, servicio o agente, y documentar cada nuevo componente con su propio README.
- Mantener cada agente como unidad con código, configuración, herramientas, prompts y pruebas; partir de `agents/_template/`.
- Empezar con una API FastAPI centralizada y extraer workers o servicios independientes solo cuando sea necesario.
- Para el procesamiento de datos, distinguir fuentes, pipelines, salidas procesadas y evaluación.
- Extraer a `packages/` el código compartido entre aplicaciones; reservar `shared/` para recursos comunes que no constituyen un paquete.
- Conservar documentación en español e inglés en varias guías de carpeta.
- El paquete compartido actual usa el ámbito `@repo/`; sus tipos son ejemplos mínimos para ampliar con entidades del dominio.

**Fuentes:** [README.es.md](./README.es.md), [agents/_template/README.es.md](./agents/_template/README.es.md), [packages/README.es.md](./packages/README.es.md), [packages/shared/package.json](./packages/shared/package.json), [packages/shared/types/index.ts](./packages/shared/types/index.ts).

## 6. Otros

- El `CONTEXT.md` presente describe Brasaland: una cadena de restaurantes con operaciones en Colombia y Florida y necesidades de digitalización. Es el contexto del negocio, no documentación de una aplicación técnica.
- `company-choice.md` presenta una idea inicial de agente de reservas por chat, con gestión de disponibilidad y sugerencias de horarios alternativos; todavía no hay una implementación correspondiente.
- La guía se autodefine como plantilla inicial. Conviene tratar los frameworks y servicios descritos en ella como orientación, y verificar la existencia de código/configuración antes de asumir que una función está disponible.

**Fuentes:** [CONTEXT.md](./CONTEXT.md), [company-choice.md](./company-choice.md), [README.es.md](./README.es.md).
