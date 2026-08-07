"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-21 22:15:00.000000
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "requirements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("text", sa.Text(), nullable=False, index=True),
        sa.Column("context", sa.JSON(), nullable=True),
        sa.Column("source", sa.String(50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
        sa.CheckConstraint("length(text) <= 5000", name="ck_req_text_length"),
    )

    op.create_table(
        "classifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "requirement_id",
            sa.String(36),
            sa.ForeignKey("requirements.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("category", sa.String(100), nullable=False, index=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
        sa.CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="ck_cls_confidence_range",
        ),
        sa.CheckConstraint(
            "length(category) > 0",
            name="ck_cls_category_not_empty",
        ),
    )

    op.create_table(
        "feedback",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "classification_id",
            sa.String(36),
            sa.ForeignKey("classifications.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("corrected_category", sa.String(100), nullable=False),
        sa.Column("confidence_was_correct", sa.Boolean(), default=False),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
    )

    op.create_table(
        "metrics",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "date",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
        sa.Column("total_processed", sa.Integer(), default=0),
        sa.Column("total_correct", sa.Integer(), default=0),
        sa.Column("avg_confidence", sa.Float(), default=0.0),
        sa.Column("low_confidence_count", sa.Integer(), default=0),
        sa.Column("model_version", sa.String(50), nullable=False),
        sa.CheckConstraint(
            "total_processed >= 0",
            name="ck_metrics_processed_nonneg",
        ),
        sa.CheckConstraint(
            "avg_confidence >= 0.0 AND avg_confidence <= 1.0",
            name="ck_metrics_confidence_range",
        ),
    )


def downgrade() -> None:
    op.drop_table("metrics")
    op.drop_table("feedback")
    op.drop_table("classifications")
    op.drop_table("requirements")
