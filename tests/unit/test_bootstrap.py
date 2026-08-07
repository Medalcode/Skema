import os
import pytest
from unittest.mock import MagicMock

from skema.bootstrap import (
    bootstrap,
    get_classification_repository,
    get_classifier,
    get_feedback_repository,
    get_requirement_repository,
)
from skema.adapters.classifiers import DummyClassifierAdapter, HybridClassifierAdapter
from skema.adapters.storage import (
    InMemoryClassificationRepository,
    InMemoryFeedbackRepository,
    InMemoryRequirementRepository,
)
from skema.infrastructure.repositories import (
    PostgreSQLClassificationRepository,
    PostgreSQLFeedbackRepository,
    PostgreSQLRequirementRepository,
)


def test_get_classifier_dummy(monkeypatch):
    monkeypatch.setenv("CLASSIFIER_MODEL", "dummy")
    classifier = get_classifier()
    assert isinstance(classifier, DummyClassifierAdapter)


def test_get_classifier_hybrid(monkeypatch):
    monkeypatch.setenv("CLASSIFIER_MODEL", "hybrid")
    classifier = get_classifier()
    assert isinstance(classifier, HybridClassifierAdapter)


def test_repositories_without_session():
    req_repo = get_requirement_repository(None)
    class_repo = get_classification_repository(None)
    fb_repo = get_feedback_repository(None)

    assert isinstance(req_repo, InMemoryRequirementRepository)
    assert isinstance(class_repo, InMemoryClassificationRepository)
    assert isinstance(fb_repo, InMemoryFeedbackRepository)


def test_repositories_with_session():
    mock_session = MagicMock()
    req_repo = get_requirement_repository(mock_session)
    class_repo = get_classification_repository(mock_session)
    fb_repo = get_feedback_repository(mock_session)

    assert isinstance(req_repo, PostgreSQLRequirementRepository)
    assert isinstance(class_repo, PostgreSQLClassificationRepository)
    assert isinstance(fb_repo, PostgreSQLFeedbackRepository)


def test_bootstrap_orchestrator():
    use_case = bootstrap(None)
    assert use_case.classifier is not None
    assert isinstance(use_case.repository, InMemoryClassificationRepository)
