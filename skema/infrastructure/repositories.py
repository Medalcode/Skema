"""
PostgreSQL Adapter implementations for repository ports.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from skema.core.interfaces import RequirementRepositoryPort, ClassificationRepositoryPort
from skema.core.models import Requirement, ClassificationResult
from skema.infrastructure.models import RequirementModel, ClassificationModel, FeedbackModel


class PostgreSQLRequirementRepository(RequirementRepositoryPort):
    """Implementa persistencia de Requerimientos en PostgreSQL asíncrono"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, req: Requirement) -> None:
        """Guarda un requerimiento crudo"""
        model = RequirementModel(
            id=req.id,
            text=req.text,
            metadata_json=req.metadata,
        )
        self.session.add(model)
        await self.session.commit()
    
    async def get_by_id(self, id: str) -> Optional[Requirement]:
        """Recupera un requerimiento por ID"""
        result = await self.session.execute(select(RequirementModel).filter_by(id=id))
        model = result.scalars().first()
        return model.to_domain() if model else None
    
    async def get_recent(self, limit: int = 100) -> List[Requirement]:
        """Obtiene últimos N requerimientos"""
        result = await self.session.execute(
            select(RequirementModel).order_by(RequirementModel.created_at.desc()).limit(limit)
        )
        models = result.scalars().all()
        return [m.to_domain() for m in models]


class PostgreSQLClassificationRepository(ClassificationRepositoryPort):
    """Implementa persistencia de Clasificaciones en PostgreSQL asíncrono"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, result: ClassificationResult) -> None:
        """Guarda un resultado de clasificación"""
        model = ClassificationModel(
            requirement_id=result.requirement_id,
            category=result.category,
            confidence=result.confidence.value,
            model_version=result.model_version,
        )
        self.session.add(model)
        await self.session.commit()
    
    async def get_by_requirement_id(self, req_id: str) -> Optional[ClassificationResult]:
        """Obtiene la clasificación de un requerimiento"""
        result = await self.session.execute(
            select(ClassificationModel).filter_by(requirement_id=req_id)
        )
        model = result.scalars().first()
        return model.to_domain() if model else None
    
    async def get_recent(self, limit: int = 100) -> List[ClassificationResult]:
        """Obtiene últimas N clasificaciones"""
        result = await self.session.execute(
            select(ClassificationModel).order_by(ClassificationModel.created_at.desc()).limit(limit)
        )
        models = result.scalars().all()
        return [m.to_domain() for m in models]
    
    async def get_low_confidence(self, threshold: float = 0.6, limit: int = 50) -> List[ClassificationResult]:
        """Obtiene clasificaciones con baja confianza (para revisión humana)"""
        result = await self.session.execute(
            select(ClassificationModel).filter(
                ClassificationModel.confidence < threshold
            ).order_by(ClassificationModel.created_at.desc()).limit(limit)
        )
        models = result.scalars().all()
        return [m.to_domain() for m in models]


class FeedbackRepository:
    """Gestiona feedback humano y métricas de forma asíncrona"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save_feedback(self, classification_id: str, corrected_category: str, 
                      is_correct: bool, notes: str = None, created_by: str = None) -> None:
        """Guarda feedback de un usuario sobre una clasificación"""
        feedback = FeedbackModel(
            classification_id=classification_id,
            corrected_category=corrected_category,
            confidence_was_correct=is_correct,
            notes=notes,
            created_by=created_by,
        )
        self.session.add(feedback)
        await self.session.commit()
    
    async def get_feedback_for_requirement(self, req_id: str) -> Optional[FeedbackModel]:
        """Obtiene feedback para un requerimiento"""
        result = await self.session.execute(
            select(FeedbackModel).join(ClassificationModel).filter(
                ClassificationModel.requirement_id == req_id
            )
        )
        return result.scalars().first()
    
    async def get_recent_feedback(self, limit: int = 50) -> List[FeedbackModel]:
        """Obtiene feedback reciente"""
        result = await self.session.execute(
            select(FeedbackModel).order_by(FeedbackModel.created_at.desc()).limit(limit)
        )
        return result.scalars().all()
    
    async def calculate_accuracy(self) -> float:
        """Calcula accuracy basado en feedback"""
        result_total = await self.session.execute(select(func.count(FeedbackModel.id)))
        total = result_total.scalar()
        if total == 0:
            return 0.0
        
        result_correct = await self.session.execute(
            select(func.count(FeedbackModel.id)).filter(FeedbackModel.confidence_was_correct == True)
        )
        correct = result_correct.scalar()
        return correct / total
