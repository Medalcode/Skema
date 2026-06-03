# main.py - API REST con Dashboard
import logging
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select
from datetime import datetime

# Imports Limpios (Bootstrap + Domain)
from skema.core.models import Requirement
from skema.bootstrap import bootstrap
from skema.infrastructure.database import init_db, get_db, engine, Base
from skema.infrastructure.models import (
    RequirementModel, 
    ClassificationModel, 
    FeedbackModel
)
from skema.dashboard import get_template
from skema.core.config import settings

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Configuración Inicial ---
app = FastAPI(
    title="Skema API",
    version="0.3.0-async",
    description="Intelligent Requirements Classification Platform with Human Feedback Loop"
)

# Inicializa base de datos
@app.on_event("startup")
async def startup():
    await init_db()
    logger.info("✅ Database initialized")

# --- DTOs (Data Transfer Objects) ---

class RequirementRequest(BaseModel):
    text: str = Field(..., min_length=5, description="El texto crudo del requerimiento")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Datos contextuales opcionales")

class ClassificationResponse(BaseModel):
    id: str
    category: str
    confidence: float
    model_version: str

class FeedbackRequest(BaseModel):
    classification_id: str
    corrected_category: Optional[str] = None
    is_correct: Optional[bool] = None
    notes: Optional[str] = None

# --- Endpoints de Health ---

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check para Kubernetes/Load Balancers"""
    return {"status": "ok", "version": "0.3.0-async", "component": "api"}

# --- Endpoints de Clasificación ---

@app.post(
    "/classify",
    response_model=ClassificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Clasificar un nuevo requerimiento"
)
async def classify_endpoint(req_dto: RequirementRequest, db: AsyncSession = Depends(get_db)):
    """
    Recibe un requerimiento de texto, lo procesa con el motor de inferencia
    híbrido (Reglas + Embeddings) y guarda el resultado en PostgreSQL.
    """
    try:
        container = bootstrap(session=db)
        
        domain_req = Requirement.create(
            text=req_dto.text,
            metadata=req_dto.metadata
        )
        
        result = await container.classify_requirement.execute(domain_req)
        
        return ClassificationResponse(
            id=result.requirement_id,
            category=result.category,
            confidence=result.confidence.value,
            model_version=result.model_version
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Classification error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification error: {str(e)}"
        )

# --- Endpoints de Feedback ---

@app.post("/api/feedback", status_code=status.HTTP_200_OK)
async def submit_feedback(feedback: FeedbackRequest, db: AsyncSession = Depends(get_db)):
    try:
        container = bootstrap(session=db)
        await container.feedback_repository.save_feedback(
            classification_id=feedback.classification_id,
            corrected_category=feedback.corrected_category or "Unknown",
            is_correct=feedback.is_correct or False,
            notes=feedback.notes,
            created_by="web_user"
        )
        return {"status": "ok", "message": "Feedback saved"}
    except Exception as e:
        logger.error(f"Feedback error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# --- Endpoints del Dashboard (HTML) ---

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(db: AsyncSession = Depends(get_db)):
    try:
        container = bootstrap(session=db)
        
        result = await db.execute(
            select(ClassificationModel).order_by(ClassificationModel.created_at.desc()).limit(20)
        )
        recent = result.scalars().all()
        
        total_res = await db.execute(select(func.count(ClassificationModel.id)))
        total = total_res.scalar()
        
        low_conf_res = await db.execute(
            select(func.count(ClassificationModel.id)).filter(ClassificationModel.confidence < 0.6)
        )
        low_conf = low_conf_res.scalar()
        
        avg_conf_res = await db.execute(select(func.avg(ClassificationModel.confidence)))
        avg_conf_result = avg_conf_res.scalar()
        avg_conf = float(avg_conf_result) if avg_conf_result else 0.75
        
        accuracy = await container.feedback_repository.calculate_accuracy()
        
        stats = {
            "total_processed": total,
            "low_confidence_count": low_conf,
            "avg_confidence": avg_conf,
            "accuracy": accuracy
        }
        
        template = get_template("index.html")
        return template.render(
            stats=stats,
            recent_classifications=[{
                "id": r.id,
                "text": r.requirement.text,
                "category": r.category,
                "confidence": r.confidence,
                "feedback": r.feedback
            } for r in recent]
        )
    except Exception as e:
        logger.error(f"Dashboard error: {e}", exc_info=True)
        return f"<h1>Error en Dashboard</h1><p>{str(e)}</p>"

@app.get("/review", response_class=HTMLResponse)
async def dashboard_review(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(ClassificationModel).filter(
                ClassificationModel.confidence < 0.6
            ).order_by(ClassificationModel.created_at.desc()).limit(50)
        )
        low_conf_items = result.scalars().all()
        
        template = get_template("review.html")
        return template.render(
            low_confidence_items=[{
                "id": item.id,
                "text": item.requirement.text,
                "category": item.category,
                "confidence": item.confidence
            } for item in low_conf_items]
        )
    except Exception as e:
        logger.error(f"Dashboard error: {e}", exc_info=True)
        return f"<h1>Error</h1><p>{str(e)}</p>"

@app.get("/metrics", response_class=HTMLResponse)
async def dashboard_metrics(db: AsyncSession = Depends(get_db)):
    try:
        total_res = await db.execute(select(func.count(ClassificationModel.id)))
        total = total_res.scalar()
        
        container = bootstrap(session=db)
        accuracy = await container.feedback_repository.calculate_accuracy()
        
        cat_res = await db.execute(
            select(ClassificationModel.category, func.count(ClassificationModel.id))
            .group_by(ClassificationModel.category)
        )
        category_dist = cat_res.all()
        category_distribution = {cat: count for cat, count in category_dist}
        
        async def count_range(min_val, max_val):
            q = select(func.count(ClassificationModel.id))
            if max_val is not None:
                q = q.filter((ClassificationModel.confidence >= min_val) & (ClassificationModel.confidence < max_val))
            else:
                q = q.filter(ClassificationModel.confidence >= min_val)
            r = await db.execute(q)
            return r.scalar()
        
        confidence_ranges = {
            "0-20%": await count_range(0.0, 0.2),
            "20-40%": await count_range(0.2, 0.4),
            "40-60%": await count_range(0.4, 0.6),
            "60-80%": await count_range(0.6, 0.8),
            "80-100%": await count_range(0.8, None),
        }
        
        tf_res = await db.execute(select(func.count(FeedbackModel.id)))
        total_feedback = tf_res.scalar()
        
        avg_res = await db.execute(select(func.avg(ClassificationModel.confidence)))
        avg_conf_result = avg_res.scalar()
        avg_conf = float(avg_conf_result) if avg_conf_result else 0.75
        
        stats = {
            "total_processed": total,
            "total_feedback": total_feedback,
            "accuracy": accuracy,
            "avg_confidence": avg_conf
        }
        
        template = get_template("metrics.html")
        return template.render(
            stats=stats,
            category_distribution=category_distribution,
            confidence_distribution=confidence_ranges
        )
    except Exception as e:
        logger.error(f"Dashboard error: {e}", exc_info=True)
        return f"<h1>Error</h1><p>{str(e)}</p>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)

