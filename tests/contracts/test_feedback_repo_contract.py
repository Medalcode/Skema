import pytest

from skema.adapters.storage import InMemoryClassificationRepository, InMemoryFeedbackRepository
from skema.core.models import ClassificationResult, ConfidenceScore, Requirement


async def test_feedback_lifecycle():
    feedback_repo = InMemoryFeedbackRepository()
    classification_repo = InMemoryClassificationRepository()

    req = Requirement.create(text="Fix login bug")
    result = ClassificationResult(
        requirement_id=req.id,
        category="Bug",
        confidence=ConfidenceScore(0.85),
        model_version="test-v1",
    )
    await classification_repo.save(result)

    await feedback_repo.save_feedback(
        classification_id=req.id,
        corrected_category="Bug",
        is_correct=True,
        notes="Correct prediction",
    )

    accuracy = await feedback_repo.calculate_accuracy()
    assert accuracy == 1.0


async def test_low_confidence_filter():
    repo = InMemoryClassificationRepository()

    high = ClassificationResult(
        requirement_id="r1", category="Feature",
        confidence=ConfidenceScore(0.95), model_version="v1",
    )
    low = ClassificationResult(
        requirement_id="r2", category="General",
        confidence=ConfidenceScore(0.30), model_version="v1",
    )
    mid = ClassificationResult(
        requirement_id="r3", category="Bug",
        confidence=ConfidenceScore(0.55), model_version="v1",
    )

    await repo.save(high)
    await repo.save(low)
    await repo.save(mid)

    low_conf = await repo.get_low_confidence(threshold=0.6)
    assert len(low_conf) == 2
    assert all(r.confidence.value < 0.6 for r in low_conf)
