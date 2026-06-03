from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from skema.adapters.classifiers import HybridClassifierAdapter
from skema.infrastructure.repositories import (
    PostgreSQLRequirementRepository,
    PostgreSQLClassificationRepository,
    FeedbackRepository
)
from skema.infrastructure.database import SessionLocal
from skema.core.use_cases import ClassifyRequirementUseCase
from skema.infrastructure.database import SessionLocal
from skema.infrastructure.repositories import (
    FeedbackRepository,
    PostgreSQLClassificationRepository,
    PostgreSQLRequirementRepository,
)


@dataclass
class Container:
    """
    Contenedor simple de dependencias (Service Locator pattern lite).
    Agrupa todos los casos de uso listos para consumir.
    """
    classify_requirement: ClassifyRequirementUseCase
    feedback_repository: FeedbackRepository


# Singleton para el clasificador (evita recargar el modelo de IA en cada petición)
_classifier_instance = None

def get_classifier() -> HybridClassifierAdapter:
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = HybridClassifierAdapter()
    return _classifier_instance


def bootstrap(session: AsyncSession = None) -> Container:
    """
    Punto Único de Ensamblaje (Composition Root).
    
    Retorna un contenedor con la aplicación totalmente conexionada.
    """
    
    # 1. Infrastructure Layer (Adapters)
    requirement_repository = PostgreSQLRequirementRepository(session)
    classification_repository = PostgreSQLClassificationRepository(session)
    feedback_repository = FeedbackRepository(session)
    
    # Usa el Singleton para el clasificador
    classifier = get_classifier()
    
    # 2. Application Layer (Use Cases)
    classify_use_case = ClassifyRequirementUseCase(
        classifier=classifier,
        repository=classification_repository
    )

    # 3. Retornar contenedor
    return Container(
        classify_requirement=classify_use_case,
        feedback_repository=feedback_repository
    )
