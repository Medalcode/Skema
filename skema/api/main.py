import logging

from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import select

from skema.api.middleware import (
    APIKeyMiddleware,
    RateLimitMiddleware,
    RequestIDMiddleware,
    lifespan,
    register_error_handlers,
)
from skema.bootstrap import bootstrap
from skema.core.config import settings
from skema.core.models import Requirement
from skema.dashboard import get_template
from skema.infrastructure.database import get_db
from skema.infrastructure.models import ClassificationModel, FeedbackModel
from skema.infrastructure.repositories import PostgreSQLFeedbackRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Skema API",
    version="0.4.0-async",
    description="Intelligent Requirements Classification Platform with Human Feedback Loop",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(APIKeyMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=settings.RATE_LIMIT_PER_MINUTE)
register_error_handlers(app)


class RequirementRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=5000)
    context: dict = Field(default_factory=dict)


class ClassificationResponse(BaseModel):
    id: str
    category: str
    confidence: float
    model_version: str


class FeedbackRequest(BaseModel):
    classification_id: str
    corrected_category: str | None = None
    is_correct: bool | None = None
    notes: str | None = None


# --- Health ---

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok", "version": "0.4.0-async", "component": "api"}


# --- Classification ---

@app.post(
    "/classify",
    response_model=ClassificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def classify_endpoint(req_dto: RequirementRequest,
                            db: AsyncSession = Depends(get_db)):
    use_case = bootstrap()
    domain_req = Requirement.create(
        text=req_dto.text,
        context=req_dto.context,
    )
    result = await use_case.execute(domain_req)

    return ClassificationResponse(
        id=result.requirement_id,
        category=result.category,
        confidence=result.confidence.value,
        model_version=result.model_version,
    )


# --- Feedback ---

@app.post("/api/feedback", status_code=status.HTTP_200_OK)
async def submit_feedback(feedback: FeedbackRequest,
                          db: AsyncSession = Depends(get_db)):
    repo = PostgreSQLFeedbackRepository(db)
    await repo.save_feedback(
        classification_id=feedback.classification_id,
        corrected_category=feedback.corrected_category or "Unknown",
        is_correct=feedback.is_correct or False,
        notes=feedback.notes,
        created_by="web_user",
    )
    return {"status": "ok", "message": "Feedback saved"}


# --- Dashboard ---

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(ClassificationModel)
            .options(selectinload(ClassificationModel.requirement),
                     selectinload(ClassificationModel.feedback))
            .order_by(ClassificationModel.created_at.desc())
            .limit(20)
        )
        recent = result.unique().scalars().all()

        total_res = await db.execute(
            select(func.count(ClassificationModel.id))
        )
        low_conf_res = await db.execute(
            select(func.count(ClassificationModel.id))
            .filter(ClassificationModel.confidence < 0.6)
        )
        avg_conf_res = await db.execute(
            select(func.avg(ClassificationModel.confidence))
        )

        feedback_repo = PostgreSQLFeedbackRepository(db)
        accuracy = await feedback_repo.calculate_accuracy()

        template = get_template("index.html")
        return template.render(
            stats={
                "total_processed": total_res.scalar(),
                "low_confidence_count": low_conf_res.scalar(),
                "avg_confidence": float(avg_conf_res.scalar() or 0.75),
                "accuracy": accuracy,
            },
            recent_classifications=[
                {
                    "requirement_id": r.requirement_id,
                    "id": r.id,
                    "text": r.requirement.text if r.requirement else "",
                    "category": r.category,
                    "confidence": r.confidence,
                    "feedback": r.feedback is not None,
                }
                for r in recent
            ],
        )
    except Exception as e:
        logger.error(f"Dashboard error: {e}", exc_info=True)
        return HTMLResponse("<h1>Error en Dashboard</h1>", status_code=500)


@app.get("/review", response_class=HTMLResponse)
async def dashboard_review(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(ClassificationModel)
            .options(selectinload(ClassificationModel.requirement))
            .filter(ClassificationModel.confidence < 0.6)
            .order_by(ClassificationModel.created_at.desc())
            .limit(50)
        )
        items = result.unique().scalars().all()

        template = get_template("review.html")
        return template.render(
            low_confidence_items=[
                {
                    "id": item.id,
                    "text": item.requirement.text if item.requirement else "",
                    "category": item.category,
                    "confidence": item.confidence,
                }
                for item in items
            ]
        )
    except Exception as e:
        logger.error(f"Review error: {e}", exc_info=True)
        return HTMLResponse("<h1>Error</h1>", status_code=500)


@app.get("/metrics", response_class=HTMLResponse)
async def dashboard_metrics(db: AsyncSession = Depends(get_db)):
    try:
        total_res = await db.execute(
            select(func.count(ClassificationModel.id))
        )
        feedback_repo = PostgreSQLFeedbackRepository(db)
        accuracy = await feedback_repo.calculate_accuracy()

        cat_res = await db.execute(
            select(ClassificationModel.category,
                   func.count(ClassificationModel.id).label("cnt"))
            .group_by(ClassificationModel.category)
        )
        category_distribution = {cat: count for cat, count in cat_res}

        async def count_range(min_v: float, max_v: float | None) -> int:
            q = select(func.count(ClassificationModel.id)).filter(
                ClassificationModel.confidence >= min_v
            )
            if max_v is not None:
                q = q.filter(ClassificationModel.confidence < max_v)
            r = await db.execute(q)
            return r.scalar() or 0

        confidence_ranges = {
            "0-20%": await count_range(0.0, 0.2),
            "20-40%": await count_range(0.2, 0.4),
            "40-60%": await count_range(0.4, 0.6),
            "60-80%": await count_range(0.6, 0.8),
            "80-100%": await count_range(0.8, None),
        }

        tf_res = await db.execute(
            select(func.count(FeedbackModel.id))
        )
        avg_res = await db.execute(
            select(func.avg(ClassificationModel.confidence))
        )

        template = get_template("metrics.html")
        return template.render(
            stats={
                "total_processed": total_res.scalar(),
                "total_feedback": tf_res.scalar(),
                "accuracy": accuracy,
                "avg_confidence": float(avg_res.scalar() or 0.75),
            },
            category_distribution=category_distribution,
            confidence_distribution=confidence_ranges,
        )
    except Exception as e:
        logger.error(f"Metrics error: {e}", exc_info=True)
        return HTMLResponse("<h1>Error</h1>", status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)
