import logging
from uuid import uuid4

from skema.core.interfaces import (
    ClassificationRepositoryPort,
    FeedbackRepositoryPort,
    RequirementRepositoryPort,
)
from skema.core.models import ClassificationResult, ConfidenceScore, Requirement

logger = logging.getLogger(__name__)


class InMemoryClassificationRepository(ClassificationRepositoryPort):
    def __init__(self):
        self._store: dict[str, ClassificationResult] = {}

    async def save(self, result: ClassificationResult) -> None:
        self._store[result.requirement_id] = result

    async def get_by_requirement_id(self, req_id: str) -> ClassificationResult | None:
        return self._store.get(req_id)

    async def get_recent(self, limit: int = 100) -> list[ClassificationResult]:
        items = sorted(
            self._store.values(),
            key=lambda r: (r.timestamp, r.requirement_id),
            reverse=True
        )
        return items[:limit]

    async def get_low_confidence(self, threshold: float = 0.6,
                                 limit: int = 50) -> list[ClassificationResult]:
        items = [
            r for r in self._store.values()
            if r.confidence.value < threshold
        ]
        items.sort(key=lambda r: (r.timestamp, r.requirement_id), reverse=True)
        return items[:limit]


class InMemoryRequirementRepository(RequirementRepositoryPort):
    def __init__(self):
        self._store: dict[str, Requirement] = {}

    async def save(self, req: Requirement) -> None:
        self._store[req.id] = req

    async def get_by_id(self, requirement_id: str) -> Requirement | None:
        return self._store.get(requirement_id)

    async def get_recent(self, limit: int = 100) -> list[Requirement]:
        items = sorted(
            self._store.values(),
            key=lambda r: (r.timestamp, r.id),
            reverse=True
        )
        return items[:limit]


class InMemoryFeedbackRepository(FeedbackRepositoryPort):
    def __init__(self):
        self._store: dict[str, dict] = {}
        self._feedback_count = 0
        self._correct_count = 0

    async def save_feedback(self, classification_id: str, corrected_category: str,
                           is_correct: bool, notes: str = None,
                           created_by: str = None) -> None:
        self._store[classification_id] = {
            "classification_id": classification_id,
            "corrected_category": corrected_category,
            "is_correct": is_correct,
            "notes": notes or "",
            "created_by": created_by or "anonymous",
        }
        self._feedback_count += 1
        if is_correct:
            self._correct_count += 1

    async def calculate_accuracy(self) -> float:
        if self._feedback_count == 0:
            return 0.0
        return self._correct_count / self._feedback_count
