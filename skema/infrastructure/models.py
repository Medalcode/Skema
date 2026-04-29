"""
SQLAlchemy ORM models for persistence.
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from skema.infrastructure.database import Base


class RequirementModel(Base):
    """Tabla para almacenar requerimientos crudos (entrada)"""
    __tablename__ = "requirements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(String(2000), nullable=False, index=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    source = Column(String(50), nullable=True)  # github, jira, email, etc

    # Relationship
    classifications = relationship("ClassificationModel", back_populates="requirement", cascade="all, delete-orphan")

    def to_domain(self):
        """Convierte de ORM a Domain Model"""
        from skema.core.models import Requirement
        return Requirement(
            id=self.id,
            text=self.text,
            metadata=self.metadata_json or {},
        )


class ClassificationModel(Base):
    """Tabla para almacenar resultados de clasificación"""
    __tablename__ = "classifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    requirement_id = Column(String(36), ForeignKey("requirements.id"), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    confidence = Column(Float, nullable=False)  # 0.0 - 1.0
    model_version = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship
    requirement = relationship("RequirementModel", back_populates="classifications")
    feedback = relationship("FeedbackModel", back_populates="classification", uselist=False)

    def to_domain(self):
        """Convierte de ORM a Domain Model"""
        from skema.core.models import ClassificationResult, ConfidenceScore
        return ClassificationResult(
            requirement_id=self.requirement_id,
            category=self.category,
            confidence=ConfidenceScore(self.confidence),
            model_version=self.model_version,
        )


class FeedbackModel(Base):
    """
    Tabla para feedback humano.
    
    Cada corrección humana es una oportunidad de aprendizaje.
    El sistema puede usar esto para:
    - Medir precisión real
    - Re-entrenar modelos
    - Detectar drift
    - Mejorar confianza
    """
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    classification_id = Column(String(36), ForeignKey("classifications.id"), nullable=False, unique=True)
    corrected_category = Column(String(100), nullable=False)
    confidence_was_correct = Column(Boolean, default=False)
    notes = Column(String(500), nullable=True)
    created_by = Column(String(100), nullable=True)  # Usuario que hizo la corrección
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship
    classification = relationship("ClassificationModel", back_populates="feedback")

    def is_correct(self):
        """¿La clasificación automática fue correcta?"""
        return self.confidence_was_correct

    def improvement_needed(self):
        """¿El modelo necesitaba mejorar?"""
        return not self.confidence_was_correct


class MetricsModel(Base):
    """
    Agregación de métricas por día/período.
    
    Se usa para:
    - Dashboard de salud del sistema
    - Detectar degradación de precisión
    - Alertas en tiempo real
    """
    __tablename__ = "metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(DateTime, default=datetime.utcnow, index=True)
    total_processed = Column(Integer, default=0)
    total_correct = Column(Integer, default=0)
    avg_confidence = Column(Float, default=0.0)
    low_confidence_count = Column(Integer, default=0)  # confidence < 0.6
    model_version = Column(String(50), nullable=False)

    def accuracy(self):
        """Calcula accuracy del periodo"""
        if self.total_processed == 0:
            return 0.0
        return self.total_correct / self.total_processed
