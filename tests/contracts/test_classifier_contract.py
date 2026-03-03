import pytest

from skema.adapters.classifiers import DummyClassifierAdapter
from skema.core.models import Requirement, ClassificationResult, ConfidenceScore


def test_dummy_classifier_contract():
    """Contrato mínimo: `classify` acepta `Requirement` y devuelve `ClassificationResult` con `ConfidenceScore` válido."""
    adapter = DummyClassifierAdapter()
    req = Requirement.create("The server has high latency and slow response")
    result = adapter.classify(req)

    assert isinstance(result, ClassificationResult)
    assert result.requirement_id == req.id
    assert isinstance(result.confidence, ConfidenceScore)
    assert 0.0 <= result.confidence.value <= 1.0
    assert isinstance(result.category, str) and len(result.category) > 0
    assert isinstance(result.model_version, str) and len(result.model_version) > 0
