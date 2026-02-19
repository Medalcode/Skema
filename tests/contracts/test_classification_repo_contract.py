import pytest

from skema.adapters.storage.memory_adapter import InMemoryClassificationRepository
from skema.core.domain.models import Requirement, ClassificationResult, ConfidenceScore


def test_inmemory_classification_repository_contract():
    repo = InMemoryClassificationRepository()

    req = Requirement.create("Export report failed when user clicks export")
    result = ClassificationResult(
        requirement_id=req.id,
        category="Reporting",
        confidence=ConfidenceScore(0.85),
        model_version="DummyRules-v2"
    )

    repo.save(result)

    loaded = repo.get_by_requirement_id(req.id)
    assert loaded is not None
    assert loaded.requirement_id == result.requirement_id
    assert loaded.category == result.category
    assert loaded.model_version == result.model_version
    assert loaded.confidence.value == pytest.approx(0.85)
