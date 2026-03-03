# Arquitectura del Clasificador Automático de Requerimientos

## Estructura de Carpetas (Lean)

- skema/core/: Corazón del sistema (Modelos, Interfaces y Casos de Uso/Agente).
- skema/adapters/: Implementaciones concretas (Skills) de los puertos definidos en core.
- skema/api/: Punto de entrada REST (FastAPI).
- docs/: Documentación detallada de Agentes y Skills.
- tests/: Suite de pruebas unitarias, integrales y de contrato.

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

## Guía rápida de integración y operación (Consolidada)

1. **Agente Generalista**: Skema ahora opera mediante un único punto de entrada orquestado por `ClassifyRequirementUseCase`.
   - La lógica de ingesta, preprocesamiento y clasificación se ha unificado para reducir fragmentación.
   - Configura las Super-Skills en `skema/bootstrap.py`.

2. **Ejecución**:
   - Levanta la API REST: `python -m skema.api.main` (Puerto 8000).
   - El endpoint `/classify` orquesta automáticamente todas las etapas anteriores.

3. **Prueba la API**:
   - Realiza un POST a `/classify` con un JSON como `{ "text": "El sistema debe permitir login de usuarios" }`.
   - Recibirás una respuesta categorizada con nivel de confianza.

4. **Extensión**:
   - Para añadir capacidades, no crees nuevos módulos; añade Super-Skills paramétricas en `skema/adapters/`.