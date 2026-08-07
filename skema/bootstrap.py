import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession

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


def get_requirement_repository(session: AsyncSession | None = None) -> RequirementRepositoryPort:
    if session is not None:
        from skema.infrastructure.repositories import PostgreSQLRequirementRepository
        return PostgreSQLRequirementRepository(session)
    return InMemoryRequirementRepository()


def get_classification_repository(
    session: AsyncSession | None = None
) -> ClassificationRepositoryPort:
    if session is not None:
        from skema.infrastructure.repositories import PostgreSQLClassificationRepository
        return PostgreSQLClassificationRepository(session)
    return InMemoryClassificationRepository()


def get_feedback_repository(session: AsyncSession | None = None) -> FeedbackRepositoryPort:
    if session is not None:
        from skema.infrastructure.repositories import PostgreSQLFeedbackRepository
        return PostgreSQLFeedbackRepository(session)
    return InMemoryFeedbackRepository()


def bootstrap(session: AsyncSession | None = None) -> ClassifyRequirementUseCase:
    classifier = get_classifier()
    classification_repo = get_classification_repository(session)
    return ClassifyRequirementUseCase(
        classifier=classifier,
        repository=classification_repo,
    )
