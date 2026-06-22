import logging
import os

from skema.adapters.storage import (
    InMemoryClassificationRepository,
    InMemoryFeedbackRepository,
    InMemoryRequirementRepository,
)
from skema.core.interfaces import (
    ClassificationRepositoryPort,
    ClassifierPort,
    FeedbackRepositoryPort,
    RequirementRepositoryPort,
)
from skema.core.use_cases import ClassifyRequirementUseCase

logger = logging.getLogger(__name__)


def get_classifier() -> ClassifierPort:
    classifier_model = os.getenv("CLASSIFIER_MODEL", "hybrid").lower()
    if classifier_model == "dummy":
        from skema.adapters.classifiers import DummyClassifierAdapter
        logger.info("Using DummyClassifierAdapter")
        return DummyClassifierAdapter()
    else:
        from skema.adapters.classifiers import HybridClassifierAdapter
        logger.info("Using HybridClassifierAdapter")
        return HybridClassifierAdapter.create()


def get_requirement_repository() -> RequirementRepositoryPort:
    return InMemoryRequirementRepository()


def get_classification_repository() -> ClassificationRepositoryPort:
    return InMemoryClassificationRepository()


def get_feedback_repository() -> FeedbackRepositoryPort:
    return InMemoryFeedbackRepository()


def bootstrap() -> ClassifyRequirementUseCase:
    classifier = get_classifier()
    classification_repo = get_classification_repository()
    return ClassifyRequirementUseCase(
        classifier=classifier,
        repository=classification_repo,
    )
