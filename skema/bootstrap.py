from dataclasses import dataclass
from sqlalchemy.orm import Session
from skema.adapters.classifiers import HybridClassifierAdapter
from skema.infrastructure.repositories import (
    PostgreSQLRequirementRepository,
    PostgreSQLClassificationRepository,
    FeedbackRepository
)
from skema.infrastructure.database import SessionLocal
from skema.core.use_cases import ClassifyRequirementUseCase

@dataclass
class Container:
    """
    Contenedor simple de dependencias (Service Locator pattern lite).
    Agrupa todos los casos de uso listos para consumir.
    """
    classify_requirement: ClassifyRequirementUseCase
    feedback_repository: FeedbackRepository


def bootstrap(session: Session = None) -> Container:
    """
    Punto Único de Ensamblaje (Composition Root).
    
    Decisiones de infraestructura:
    - Base de datos: PostgreSQL (con fallback a SQLite si no está disponible)
    - Clasificador: HybridClassifier (Reglas + Embeddings)
    - Persistencia: SQLAlchemy ORM
    
    Retorna un contenedor con la aplicación totalmente conexionada.
    """
    
    # Si no se proporciona sesión, usa la configurada en database.py
    if session is None:
        session = SessionLocal()
    
    # 1. Infrastructure Layer (Adapters)
    requirement_repository = PostgreSQLRequirementRepository(session)
    classification_repository = PostgreSQLClassificationRepository(session)
    feedback_repository = FeedbackRepository(session)
    classifier = HybridClassifierAdapter()  # Híbrido: Reglas + Embeddings
    
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
