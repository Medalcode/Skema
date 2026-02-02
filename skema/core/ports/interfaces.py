from abc import ABC, abstractmethod
from typing import Optional
from skema.core.domain.models import Requirement, ClassificationResult

class ClassifierPort(ABC):
    """
    Puerto de SALIDA (Driven Port).
    Define la capacidad de clasificar un requerimiento.
    Implementado por adaptadores como: OpenAIAdapter, SpacyAdapter, DummyAdapter.
    """
    @abstractmethod
    def classify(self, req: Requirement) -> ClassificationResult:
        pass

class RequirementRepositoryPort(ABC):
    """
    Puerto de SALIDA (Driven Port).
    Gestiona la persistencia de los Requerimientos crudos (Input).
    """
    @abstractmethod
    def save(self, req: Requirement) -> None:
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Requirement]:
        pass

class ClassificationRepositoryPort(ABC):
    """
    Puerto de SALIDA (Driven Port).
    Gestiona la persistencia de los resultados de clasificación (Output).
    """
    @abstractmethod
    def save(self, result: ClassificationResult) -> None:
        pass

    @abstractmethod
    def get_by_requirement_id(self, req_id: str) -> Optional[ClassificationResult]:
        pass
