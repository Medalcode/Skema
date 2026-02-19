# Agents

Definición
---------
Un *Agent* es un orquestador de alto nivel (un caso de uso / coordinator). Su responsabilidad es coordinar la entrada, aplicar lógica de negocio y componer `skills` para resolver una tarea.

Responsabilidades
-----------------
- Orquestar el flujo de un requerimiento: ingestión → preprocesamiento → clasificación → persistencia.
- Componer y llamar a `skills` (adaptadores) que implementen los `ports` relevantes.
- Encapsular políticas de reintento, timeouts y manejo de errores de negocio.

Mapping al código
------------------
- Implementación de ejemplo: `skema/core/application/use_cases.py` contiene casos de uso que actúan como Agents.
- Wiring / composición: `skema/bootstrap.py` muestra cómo se inyectan adaptadores (skills) en los casos de uso.
- Endpoints que exponen Agents: `skema/api/main.py`.

Plantilla rápida (práctica)
--------------------------
1. Crear un caso de uso en `skema/core/application/` que reciba los puertos necesarios.
2. Recibir las dependencias vía constructor (inyección explícita).
3. Documentar inputs/outputs y añadir tests unitarios que simulen `skills` con fakes/dummies.

Checklist para PR de un Agent
----------------------------
- [ ] Docs actualizados (`docs/agents.md` referenciado).
- [ ] Tests unitarios del caso de uso con mocks de skills.
- [ ] Ejemplo de integración (opcional) en `tests/integration/`.

