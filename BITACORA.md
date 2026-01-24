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
- Inclusión de __init__.py en cada módulo.

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
