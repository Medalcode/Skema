# Arquitectura del Clasificador Automático de Requerimientos

## Estructura de Carpetas

- ingestion/: Módulo de ingesta de datos (fuentes externas, colas, APIs)
- preprocessing/: Preprocesamiento y limpieza de requerimientos
- classifier/: Modelos de Machine Learning y lógica de clasificación
- api/: API REST/gRPC para exponer el servicio
- storage/: Persistencia de datos (NoSQL, SQL, archivos)
- monitoring/: Monitoreo, logging y métricas

## Flujo General

1. **Ingesta**: Recibe requerimientos desde múltiples fuentes.
2. **Preprocesamiento**: Limpia, normaliza y transforma los datos.
3. **Clasificación**: Aplica modelos ML para categorizar los requerimientos.
4. **Almacenamiento**: Guarda resultados y logs.
5. **API**: Expone endpoints para consulta y operación.
6. **Monitoreo**: Supervisa salud, métricas y logs del sistema.

## Escalabilidad
- Cada módulo puede desplegarse como microservicio.
- Comunicación asíncrona mediante colas/mensajería.
- Despliegue en contenedores (Docker/Kubernetes).
- Autoescalado y balanceo de carga.

---

Cada carpeta contendrá su propio README y archivos de implementación.

## Guía rápida de integración y prueba

1. Ejecuta cada módulo por separado:
	- `python ingestion/main.py` para simular la ingesta de requerimientos.
	- `python preprocessing/main.py` para limpiar y normalizar requerimientos.
	- `python classifier/main.py` para clasificar requerimientos.
	- `python storage/main.py` para simular el guardado de resultados.
	- `python monitoring/main.py` para exponer métricas en http://localhost:8001.
	- `python api/main.py` para levantar la API REST (FastAPI) en http://localhost:8000.

2. Prueba la API:
	- Realiza un POST a `/clasificar` con un JSON como `{ "texto": "El sistema debe permitir login de usuarios" }` y recibe la categoría.

3. Integra los módulos conectando la salida de uno como entrada del siguiente para un flujo automatizado.

4. Personaliza cada módulo para fuentes, modelos y almacenamiento reales según tus necesidades.