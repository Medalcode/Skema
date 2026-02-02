# Bitácora de Desarrollo: Clasificador Automático de Requerimientos

## Tareas Realizadas

- Diseño de arquitectura escalable y modular.
- Creación de estructura de carpetas para cada módulo:
  - ingestion/
  - preprocessing/
  - classifier/
  - api/
  - storage/
  - monitoring/
- Documentación de arquitectura y guía rápida en ARQUITECTURA.md.
- Implementación de esqueleto en Python para cada módulo:
  - Ingesta: Simulación de recepción y envío a cola.
  - Preprocesamiento: Limpieza y normalización de texto.
  - Clasificador: DummyClassifier para clasificación por palabras clave.
  - API: Endpoint REST para clasificación y health check.
  - Almacenamiento: Simulación de guardado de resultados.
  - Monitoreo: Exposición de métricas simuladas con Prometheus.
- Creación de requirements.txt con dependencias clave.
- Inclusión de **init**.py en cada módulo.

## Tareas Pendientes

- Integración real entre módulos (mensajería, orquestación).
- Implementar conectores reales para ingesta (Kafka, APIs, archivos).
- Sustituir DummyClassifier por un modelo de ML real (scikit-learn, transformers, etc.).
- Persistencia real en base de datos (MongoDB, PostgreSQL, etc.).
- Logging estructurado y centralizado.
- Pruebas automáticas unitarias e integración.
- Despliegue con Docker/Kubernetes.
- Seguridad y autenticación en la API.
- Dashboards de monitoreo y alertas.
- Documentación técnica y de usuario final.

---

## 🗓 Iteración 2: Refactorización Arquitectónica "Core Domain"

### Estado Actual:

El sistema funciona como un conjunto de scripts aislados. Existe divergencia en la lógica de negocio (duplicación de código) y acoplamiento implícito mediante diccionarios sin tipado. La arquitectura documentada no refleja la realidad del código.

### Objetivos Técnicos:

1.  **Establecer la "Fuente de Verdad":** Crear un núcleo de dominio (`skema/core`) agnóstico a frameworks.
2.  **Eliminar Duplicación:** Centralizar la lógica de clasificación y almacenamiento, eliminando copias en `api/` y `classifier/`.
3.  **Contratos Explícitos:** Reemplazar pasos de diccionarios por objetos tipados (`Requerimiento`, `ClassificationResult`).

### Decisiones Arquitectónicas:

- **Arquitectura Hexagonal (Puertos y Adaptadores):** Se adoptará este patrón para aislar el dominio.
  - `core/domain`: Entidades de negocio puras.
  - `core/ports`: Interfaces abstractas (Protocolos).
  - `adapters/`: Implementaciones concretas (Dummy, Scikit, FastAPI).
- **Inyección de Dependencias:** La API REST ensamblará las dependencias en tiempo de ejecución, en lugar de instanciar clases directamente.

### Riesgos Identificados:

- **Refactor Breaking Changes:** La migración romperá temporalmente los scripts de `main.py` de cada módulo hasta que se reconecten al nuevo Core.
- **Curva de Complejidad:** La introducción de abstracciones puede parecer "over-engineering" inicial comparado con los scripts simples actuales.

### Criterios de Éxito:

- [ ] El código de `Classifier` existe en un solo lugar y es importado por la API.
- [ ] No existen diccionarios "mágicos" pasando datos críticos; se usan Dataclasses/Pydantic.
- [ ] La API puede cambiar de clasificador `Dummy` a `Scikit` cambiando solo una línea de configuración.
