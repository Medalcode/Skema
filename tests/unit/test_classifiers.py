from skema.adapters.classifiers import DummyClassifierAdapter, HybridClassifierAdapter
from skema.core.models import Requirement


async def test_dummy_classifier_rules():
    classifier = DummyClassifierAdapter()
    req = Requirement.create(text="we need to fix the login page")

    result = await classifier.classify(req)
    assert result.category == "Authentication"
    assert result.confidence.value == 0.9


async def test_hybrid_classifier_keyword():
    classifier = HybridClassifierAdapter()
    req = Requirement.create(text="fatal crash in production")

    result = await classifier.classify(req)
    assert result.category == "Bug"
    assert result.confidence.value >= 0.85


async def test_hybrid_classifier_semantic():
    classifier = HybridClassifierAdapter()
    req = Requirement.create(text="optimize slow database queries to reduce latency")

    result = await classifier.classify(req)
    assert result.category == "Performance"
    assert result.confidence.value >= 0.85
