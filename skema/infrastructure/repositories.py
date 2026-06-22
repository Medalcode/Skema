import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from skema.core.interfaces import (
    ClassificationRepositoryPort,
    FeedbackRepositoryPort,
    RequirementRepositoryPort,
)
from skema.core.models import ClassificationResult, ConfidenceScore, Requirement
from skema.infrastructure.models import (
    ClassificationModel,
    FeedbackModel,
    RequirementModel,
)

logger = logging.getLogger(__name__)


class PostgreSQLRequirementRepository(RequirementRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, req: Requirement) -> None:
        try:
            model = RequirementModel(
                id=req.id,
                text=req.text,
                context=req.context,
                source=req.source,
            )
            self.session.add(model)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to save requirement: {e}", exc_info=True)
            raise

    async def get_by_id(self, requirement_id: str) -> Requirement | None:
        try:
            result = await self.session.execute(
                select(RequirementModel).filter_by(id=requirement_id)
            )
            model = result.scalars().first()
            return model.to_domain() if model else None
        except Exception as e:
            logger.error(f"Failed to get requirement {requirement_id}: {e}", exc_info=True)
            raise

    async def get_recent(self, limit: int = 100) -> list[Requirement]:
        try:
            result = await self.session.execute(
                select(RequirementModel)
                .order_by(RequirementModel.created_at.desc())
                .limit(limit)
            )
            models = result.scalars().all()
            return [m.to_domain() for m in models]
        except Exception as e:
            logger.error(f"Failed to get recent requirements: {e}", exc_info=True)
            raise


class PostgreSQLClassificationRepository(ClassificationRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, result: ClassificationResult) -> None:
        try:
            model = ClassificationModel(
                requirement_id=result.requirement_id,
                category=result.category,
                confidence=result.confidence.value,
                model_version=result.model_version,
            )
            self.session.add(model)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to save classification: {e}", exc_info=True)
            raise

    async def get_by_requirement_id(self, req_id: str) -> ClassificationResult | None:
        try:
            result = await self.session.execute(
                select(ClassificationModel).filter_by(requirement_id=req_id)
            )
            model = result.scalars().first()
            return model.to_domain() if model else None
        except Exception as e:
            logger.error(f"Failed to get classification for {req_id}: {e}", exc_info=True)
            raise

    async def get_recent(self, limit: int = 100) -> list[ClassificationResult]:
        try:
            result = await self.session.execute(
                select(ClassificationModel)
                .order_by(ClassificationModel.created_at.desc())
                .limit(limit)
            )
            models = result.scalars().all()
            return [m.to_domain() for m in models]
        except Exception as e:
            logger.error(f"Failed to get recent classifications: {e}", exc_info=True)
            raise

    async def get_low_confidence(self, threshold: float = 0.6,
                                 limit: int = 50) -> list[ClassificationResult]:
        try:
            result = await self.session.execute(
                select(ClassificationModel)
                .filter(ClassificationModel.confidence < threshold)
                .order_by(ClassificationModel.created_at.desc())
                .limit(limit)
            )
            models = result.scalars().all()
            return [m.to_domain() for m in models]
        except Exception as e:
            logger.error(f"Failed to get low confidence: {e}", exc_info=True)
            raise


class PostgreSQLFeedbackRepository(FeedbackRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_feedback(self, classification_id: str, corrected_category: str,
                           is_correct: bool, notes: str = None,
                           created_by: str = None) -> None:
        try:
            feedback = FeedbackModel(
                classification_id=classification_id,
                corrected_category=corrected_category,
                confidence_was_correct=is_correct,
                notes=notes,
                created_by=created_by,
            )
            self.session.add(feedback)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to save feedback: {e}", exc_info=True)
            raise

    async def calculate_accuracy(self) -> float:
        try:
            result_total = await self.session.execute(
                select(func.count(FeedbackModel.id))
            )
            total = result_total.scalar()
            if total == 0:
                return 0.0

            result_correct = await self.session.execute(
                select(func.count(FeedbackModel.id))
                .filter(FeedbackModel.confidence_was_correct.is_(True))
            )
            correct = result_correct.scalar()
            return correct / total
        except Exception as e:
            logger.error(f"Failed to calculate accuracy: {e}", exc_info=True)
            raise
