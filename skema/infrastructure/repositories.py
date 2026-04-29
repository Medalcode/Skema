"""
PostgreSQL Adapter implementations for repository ports.
"""


from sqlalchemy.orm import Session

from skema.core.interfaces import ClassificationRepositoryPort, RequirementRepositoryPort
from skema.core.models import ClassificationResult, Requirement
from skema.infrastructure.models import ClassificationModel, FeedbackModel, RequirementModel


class PostgreSQLRequirementRepository(RequirementRepositoryPort):
    """Implementa persistencia de Requerimientos en PostgreSQL"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, req: Requirement) -> None:
        """Guarda un requerimiento crudo"""
        model = RequirementModel(
            id=req.id,
            text=req.text,
            metadata_json=req.metadata,
        )
        self.session.add(model)
        self.session.commit()

    def get_by_id(self, id: str) -> Requirement | None:
        """Recupera un requerimiento por ID"""
        model = self.session.query(RequirementModel).filter_by(id=id).first()
        return model.to_domain() if model else None

    def get_recent(self, limit: int = 100) -> list[Requirement]:
        """Obtiene últimos N requerimientos"""
        models = self.session.query(RequirementModel).order_by(
            RequirementModel.created_at.desc()
        ).limit(limit).all()
        return [m.to_domain() for m in models]


class PostgreSQLClassificationRepository(ClassificationRepositoryPort):
    """Implementa persistencia de Clasificaciones en PostgreSQL"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, result: ClassificationResult) -> None:
        """Guarda un resultado de clasificación"""
        model = ClassificationModel(
            requirement_id=result.requirement_id,
            category=result.category,
            confidence=result.confidence.value,
            model_version=result.model_version,
        )
        self.session.add(model)
        self.session.commit()

    def get_by_requirement_id(self, req_id: str) -> ClassificationResult | None:
        """Obtiene la clasificación de un requerimiento"""
        model = self.session.query(ClassificationModel).filter_by(
            requirement_id=req_id
        ).first()
        return model.to_domain() if model else None

    def get_recent(self, limit: int = 100) -> list[ClassificationResult]:
        """Obtiene últimas N clasificaciones"""
        models = self.session.query(ClassificationModel).order_by(
            ClassificationModel.created_at.desc()
        ).limit(limit).all()
        return [m.to_domain() for m in models]

    def get_low_confidence(self, threshold: float = 0.6, limit: int = 50) -> list[ClassificationResult]:
        """Obtiene clasificaciones con baja confianza (para revisión humana)"""
        models = self.session.query(ClassificationModel).filter(
            ClassificationModel.confidence < threshold
        ).order_by(
            ClassificationModel.created_at.desc()
        ).limit(limit).all()
        return [m.to_domain() for m in models]


class FeedbackRepository:
    """Gestiona feedback humano y métricas"""

    def __init__(self, session: Session):
        self.session = session

    def save_feedback(self, classification_id: str, corrected_category: str,
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
        self.session.commit()

    def get_feedback_for_requirement(self, req_id: str) -> FeedbackModel | None:
        """Obtiene feedback para un requerimiento"""
        return self.session.query(FeedbackModel).join(
            ClassificationModel
        ).filter(ClassificationModel.requirement_id == req_id).first()

    def get_recent_feedback(self, limit: int = 50) -> list[FeedbackModel]:
        """Obtiene feedback reciente"""
        return self.session.query(FeedbackModel).order_by(
            FeedbackModel.created_at.desc()
        ).limit(limit).all()

    def calculate_accuracy(self) -> float:
        """Calcula accuracy basado en feedback"""
        total = self.session.query(FeedbackModel).count()
        if total == 0:
            return 0.0
        correct = self.session.query(FeedbackModel).filter(
            FeedbackModel.confidence_was_correct == True
        ).count()
        return correct / total
