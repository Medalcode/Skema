# Skema

# Clasificador Automático de Requerimientos

Arquitectura modular y escalable para la clasificación automática de requerimientos.

## Módulos principales
- **ingestion/**: Ingesta de datos desde fuentes externas.
- **preprocessing/**: Limpieza y normalización de requerimientos.
- **classifier/**: Modelos de Machine Learning y lógica de clasificación.
- **api/**: API REST para exponer el servicio.
- **storage/**: Persistencia de resultados y logs.
- **monitoring/**: Monitoreo y métricas.

## Guía rápida
1. Instala dependencias: `pip install -r requirements.txt`
2. Ejecuta cada módulo por separado (ver ARQUITECTURA.md para detalles).
3. Prueba la API en http://localhost:8000 (`/health` y `/clasificar`).
4. Consulta métricas en http://localhost:8001

## Bitácora
Consulta el archivo BITACORA.md para ver el historial de tareas realizadas y pendientes.
# Skema