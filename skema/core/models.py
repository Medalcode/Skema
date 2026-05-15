from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

@dataclass(frozen=True, order=True)
class ConfidenceScore:
    """
    Value Object que representa la certeza de una clasificación.
    Garantiza que el valor siempre esté entre 0.0 y 1.0.
    """
    value: float

    def __post_init__(self):
        if not (0.0 <= self.value <= 1.0):
            raise ValueError(f"ConfidenceScore must be between 0.0 and 1.0, got {self.value}")

    def __str__(self):
        return f"{self.value:.2f}"

@dataclass(frozen=True)
class Requirement:
    """
    Entidad raíz del agregado. Representa la unidad de trabajo cruda.
    Inmutable.
    """
    id: str
    text: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, text: str, metadata: Optional[Dict[str, Any]] = None) -> 'Requirement':
        if not text.strip():
            raise ValueError("Requirement text cannot be empty")
        return cls(
            id=str(uuid.uuid4()),
            text=text,
            metadata=metadata or {}
        )

@dataclass(frozen=True)
class ClassificationResult:
    """
    Value Object complejo que agrupa el resultado de la inferencia.
    """
    requirement_id: str
    category: str
    confidence: ConfidenceScore
    model_version: str
    timestamp: datetime = field(default_factory=datetime.now)
