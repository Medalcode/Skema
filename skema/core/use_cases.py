import logging
from dataclasses import dataclass

from skema.core.interfaces import ClassificationRepositoryPort, ClassifierPort
from skema.core.models import ClassificationResult, Requirement

logger = logging.getLogger(__name__)


@dataclass
class ClassifyRequirementUseCase:
    classifier: ClassifierPort
    repository: ClassificationRepositoryPort

    async def execute(self, req: Requirement) -> ClassificationResult:
        try:
            result = await self.classifier.classify(req)
            await self.repository.save(result)
            return result
        except Exception as e:
            logger.error(f"Classification failed: {e}", exc_info=True)
            raise
