# Skills

Definición
---------
Una *Skill* es una implementación concreta de un `Port` (adaptador). Proporciona una capacidad reusable (p.ej. clasificación, almacenamiento, búsqueda) que un `Agent` puede invocar.

Convenciones y ubicación
-----------------------
- Cada skill debe vivir en `skema/adapters/` y preferiblemente en un subpaquete lógico, p.ej. `skema/adapters/classifiers/`.
- Naming: `PascalCase` para clases adaptadoras (p.ej. `DummyClassifierAdapter`), archivos en `snake_case`.
- Una skill = un adaptador por archivo/implementación (granularidad por adaptador).

Implementación mínima
--------------------
1. Implementar el `Port` correspondiente, p.ej. `ClassifierPort` en `skema/core/ports/interfaces.py`.
2. Proveer un constructor sin efectos colaterales y un método de healthcheck opcional.
3. Exponer configuración (env vars) y versionado (`model_version` o `adapter_version`).

Plantilla de ejemplo (pseudo)

```python
from skema.core.ports.interfaces import ClassifierPort
from skema.core.domain.models import Requirement, ClassificationResult

class MyClassifierAdapter(ClassifierPort):
    def classify(self, req: Requirement) -> ClassificationResult:
        # implementar
        pass
```

Contract tests
--------------
- Añadir pruebas en `tests/contracts/` que validen que una skill cumple el contrato del `Port`.
- Ejemplo: `tests/contracts/test_classifier_contract.py` valida que cualquier `Classifier` devuelva un `ClassificationResult` válido.

Operacional
----------
- Healthchecks: exponer método `is_healthy()` o endpoint separado.
- Métricas: instrumentar latencia y tasa de errores (OpenTelemetry/Prometheus).
- Resiliencia: timeouts, retries y circuit-breaker en el Agent cuando invoque la skill.

Registro y despliegue
---------------------
- Registrar la skill en `skema/bootstrap.py` para que sea inyectada en los Agents.
- Mantener compatibilidad hacia atrás cuando se versionen skills (semver para adaptadores).

## Inventario de Super-Skills (Paramétricas)
------------------------------------------

### 1. RequirementProcessor (Fusión de `Preprocessor` y `Formatter`)
- **Parámetros:** `clean: bool`, `lowercase: bool`, `remove_special: bool`.
- **Lógica:** Implementa el 80% de la lógica de limpieza de texto dispersa en `preprocessing/main.py`.

### 2. DataArchivist (Fusión de `Ingestor`, `Repository` y `Storage`)
- **Parámetros:** `source: string`, `destination: string`, `mode: ['read', 'write', 'stream']`.
- **Lógica:** Unifica el acceso a datos (Lectura/Escritura) bajo una misma interfaz paramétrica.

### 3. SmartClassifier (Skill Paramétrica)
- **Parámetros:** `engine: ['dummy', 'openai', 'spacy']`, `min_confidence: float`.
- **Lógica:** Encapsula múltiples motores de clasificación en una sola Skill.
