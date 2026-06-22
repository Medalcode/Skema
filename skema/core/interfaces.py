from abc import ABC, abstractmethod
from typing import Optional

from skema.core.models import ClassificationResult, Requirement


class ClassifierPort(ABC):
    """
    Puerto de SALIDA (Driven Port).
    Define la capacidad de clasificar un requerimiento.
    """
    @abstractmethod
    async def classify(self, req: Requirement) -> ClassificationResult:
        pass


class RequirementRepositoryPort(ABC):
    """
    Puerto de SALIDA (Driven Port).
    Gestiona la persistencia de los Requerimientos crudos (Input).
    """
    @abstractmethod
    async def save(self, req: Requirement) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, requirement_id: str) -> Optional[Requirement]:
        pass

    @abstractmethod
    async def get_recent(self, limit: int = 100) -> list[Requirement]:
        pass


class ClassificationRepositoryPort(ABC):
    """
    Puerto de SALIDA (Driven Port).
    Gestiona la persistencia de los resultados de clasificación (Output).
    """
    @abstractmethod
    async def save(self, result: ClassificationResult) -> None:
        pass

    @abstractmethod
    async def get_by_requirement_id(self, req_id: str) -> Optional[ClassificationResult]:
        pass

    @abstractmethod
    async def get_recent(self, limit: int = 100) -> list[ClassificationResult]:
        pass

    @abstractmethod
    async def get_low_confidence(self, threshold: float = 0.6, limit: int = 50) -> list[ClassificationResult]:
        pass


class FeedbackRepositoryPort(ABC):
    """
    Puerto de SALIDA (Driven Port) para feedback humano y métricas.
    """
    @abstractmethod
    async def save_feedback(self, classification_id: str, corrected_category: str,
                           is_correct: bool, notes: str = None, created_by: str = None) -> None:
        pass

    @abstractmethod
    async def calculate_accuracy(self) -> float:
        pass


class ProcessorPort(ABC):
    """
    Puerto de SALIDA (Driven Port) para procesamiento de texto.
    """
    @abstractmethod
    def process(self, text: str, clean: bool = True, lowercase: bool = True) -> str:
        pass
