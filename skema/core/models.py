import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, order=True)
class ConfidenceScore:
    value: float

    def __post_init__(self):
        if not (0.0 <= self.value <= 1.0):
            raise ValueError(f"ConfidenceScore must be between 0.0 and 1.0, got {self.value}")

    def __str__(self):
        return f"{self.value:.2f}"


@dataclass(frozen=True)
class Requirement:
    id: str
    text: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    context: dict[str, Any] = field(default_factory=dict)
    source: str | None = None

    @classmethod
    def create(cls, text: str, context: dict[str, Any] | None = None,
               source: str | None = None) -> 'Requirement':
        if not text.strip():
            raise ValueError("Requirement text cannot be empty")
        if len(text) > 5000:
            raise ValueError("Requirement text too long (max 5000 chars)")
        return cls(
            id=str(uuid.uuid4()),
            text=text,
            context=context or {},
            source=source
        )


@dataclass(frozen=True)
class ClassificationResult:
    requirement_id: str
    category: str
    confidence: ConfidenceScore
    model_version: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
