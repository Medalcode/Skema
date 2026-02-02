from dataclasses import dataclass
from skema.adapters.classifiers.dummy_adapter import DummyClassifierAdapter
from skema.adapters.storage.memory_adapter import InMemoryClassificationRepository
from skema.core.application.use_cases import ClassifyRequirementUseCase

@dataclass
class Container:
    """
    Contenedor simple de dependencias (Service Locator pattern lite).
    Agrupa todos los casos de uso listos para consumir.
    """
    classify_requirement: ClassifyRequirementUseCase

def bootstrap() -> Container:
    """
    Punto Único de Ensamblaje (Composition Root).
    
    Aquí se toman las decisiones de infraestructura:
    - ¿Qué base de datos usar? (Memory vs Postgres)
    - ¿Qué clasificador usar? (Dummy vs OpenAI)
    
    Retorna un contenedor con la aplicación totalmente conexionada.
    """
    
    # 1. Infrastructure Layer (Adapters)
    # Podríamos leer variables de entorno aquí para decidir qué adaptador usar
    # ej: if os.getenv("DB_TYPE") == "postgres": ...
    repository = InMemoryClassificationRepository()
    classifier = DummyClassifierAdapter()

    # 2. Application Layer (Use Cases)
    # Inyección de dependencias pura
    classify_use_case = ClassifyRequirementUseCase(
        classifier=classifier, 
        repository=repository
    )

    # 3. Retornar contenedor
    return Container(
        classify_requirement=classify_use_case
    )
