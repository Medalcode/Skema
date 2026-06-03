import pytest
from skema.adapters.classifiers import DummyClassifierAdapter, HybridClassifierAdapter
from skema.core.models import Requirement

def test_dummy_classifier_rules():
    classifier = DummyClassifierAdapter()
    req = Requirement.create(text="we need to fix the login page")
    
    result = classifier.classify(req)
    assert result.category == "Authentication"
    assert result.confidence.value == 0.9

def test_hybrid_classifier_keyword():
    classifier = HybridClassifierAdapter()
    req = Requirement.create(text="fatal crash in production")
    
    result = classifier.classify(req)
    assert result.category == "Bug"
    assert result.confidence.value >= 0.85

def test_hybrid_classifier_semantic():
    classifier = HybridClassifierAdapter()
    # A phrase that might not match exact keywords but semantically means performance
    req = Requirement.create(text="the application is taking forever to load and response time needs improvement")
    
    result = classifier.classify(req)
    # The confidence might vary, but it should lean towards Performance
    assert result.category == "Performance"
    assert result.confidence.value >= 0.4
