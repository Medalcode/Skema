import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, CheckConstraint, Column, DateTime, Float, ForeignKey,
    Integer, JSON, String, Text,
)
from sqlalchemy.orm import relationship

from skema.infrastructure.database import Base


class RequirementModel(Base):
    __tablename__ = "requirements"
    __table_args__ = (
        CheckConstraint("length(text) <= 5000", name="ck_req_text_length"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(Text, nullable=False, index=True)
    context = Column(JSON, nullable=True)
    source = Column(String(50), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )

    classifications = relationship(
        "ClassificationModel", back_populates="requirement",
        cascade="all, delete-orphan"
    )

    def to_domain(self):
        from skema.core.models import Requirement
        return Requirement(
            id=self.id,
            text=self.text,
            context=self.context or {},
            source=self.source,
            timestamp=self.created_at,
        )


class ClassificationModel(Base):
    __tablename__ = "classifications"
    __table_args__ = (
        CheckConstraint("confidence >= 0.0 AND confidence <= 1.0",
                        name="ck_cls_confidence_range"),
        CheckConstraint("length(category) > 0", name="ck_cls_category_not_empty"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    requirement_id = Column(
        String(36), ForeignKey("requirements.id"), nullable=False, index=True
    )
    category = Column(String(100), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    model_version = Column(String(50), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )

    requirement = relationship("RequirementModel", back_populates="classifications")
    feedback = relationship("FeedbackModel", back_populates="classification", uselist=False)

    def to_domain(self):
        from skema.core.models import ClassificationResult, ConfidenceScore
        return ClassificationResult(
            requirement_id=self.requirement_id,
            category=self.category,
            confidence=ConfidenceScore(self.confidence),
            model_version=self.model_version,
            timestamp=self.created_at,
        )


class FeedbackModel(Base):
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    classification_id = Column(
        String(36), ForeignKey("classifications.id"), nullable=False, unique=True
    )
    corrected_category = Column(String(100), nullable=False)
    confidence_was_correct = Column(Boolean, default=False)
    notes = Column(String(500), nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )

    classification = relationship("ClassificationModel", back_populates="feedback")

    def is_correct(self):
        return self.confidence_was_correct

    def improvement_needed(self):
        return not self.confidence_was_correct


class MetricsModel(Base):
    __tablename__ = "metrics"
    __table_args__ = (
        CheckConstraint("total_processed >= 0", name="ck_metrics_processed_nonneg"),
        CheckConstraint("avg_confidence >= 0.0 AND avg_confidence <= 1.0",
                        name="ck_metrics_confidence_range"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )
    total_processed = Column(Integer, default=0)
    total_correct = Column(Integer, default=0)
    avg_confidence = Column(Float, default=0.0)
    low_confidence_count = Column(Integer, default=0)
    model_version = Column(String(50), nullable=False)

    def accuracy(self):
        if self.total_processed == 0:
            return 0.0
        return self.total_correct / self.total_processed
