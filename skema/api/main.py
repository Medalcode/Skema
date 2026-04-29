# main.py - API REST con Dashboard
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from skema.bootstrap import bootstrap

# Imports Limpios (Bootstrap + Domain)
from skema.core.models import Requirement
from skema.dashboard import get_template
from skema.infrastructure.database import get_db, init_db
from skema.infrastructure.models import ClassificationModel, FeedbackModel

# --- Configuración Inicial ---
app = FastAPI(
    title="Skema API",
    version="0.2.0-mvp",
    description="Intelligent Requirements Classification Platform with Human Feedback Loop"
)

# Inicializa base de datos (graceful on serverless)
@app.on_event("startup")
def startup():
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database init skipped: {e}")

# --- DTOs (Data Transfer Objects) ---

class RequirementRequest(BaseModel):
    text: str = Field(..., min_length=5, description="El texto crudo del requerimiento")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Datos contextuales opcionales")

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

# --- Endpoints de Health ---

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Health check para Kubernetes/Load Balancers"""
    return {"status": "ok", "version": "0.2.0-mvp", "component": "api"}

# --- Endpoints de Clasificación ---

@app.post(
    "/classify",
    response_model=ClassificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Clasificar un nuevo requerimiento"
)
def classify_endpoint(req_dto: RequirementRequest, db: Session = Depends(get_db)):
    """
    Recibe un requerimiento de texto, lo procesa con el motor de inferencia
    híbrido (Reglas + Embeddings) y guarda el resultado en PostgreSQL.
    """
    try:
        # 1. Bootstrap con sesión actual
        container = bootstrap(session=db)

        # 2. Adaptación (DTO -> Domain)
        domain_req = Requirement.create(
            text=req_dto.text,
            metadata=req_dto.metadata
        )

        # 3. Delegación (Use Case)
        result = container.classify_requirement.execute(domain_req)

        # 4. Respuesta
        return ClassificationResponse(
            id=result.requirement_id,
            category=result.category,
            confidence=result.confidence.value,
            model_version=result.model_version
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification error: {str(e)}"
        )

# --- Endpoints de Feedback ---

@app.post("/api/feedback", status_code=status.HTTP_200_OK)
def submit_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Registra feedback humano sobre una clasificación.
    Esto permite:
    - Calcular precisión real
    - Detectar drift del modelo
    - Recolectar datos para reentrenamiento
    """
    try:
        container = bootstrap(session=db)
        container.feedback_repository.save_feedback(
            classification_id=feedback.classification_id,
            corrected_category=feedback.corrected_category or "Unknown",
            is_correct=feedback.is_correct or False,
            notes=feedback.notes,
            created_by="web_user"  # En prod, sería el usuario autenticado
        )
        return {"status": "ok", "message": "Feedback saved"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# --- Endpoints del Dashboard (HTML) ---

@app.get("/", response_class=JSONResponse)
def api_root():
    """API root with available endpoints"""
    return {
        "name": "Skema API",
        "version": "0.2.0-mvp",
        "description": "Intelligent Requirements Classification Platform",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "classify": "POST /classify",
            "feedback": "POST /api/feedback",
            "dashboard": "/dashboard",
            "review": "/review",
            "metrics": "/metrics"
        }
    }

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_home(db: Session = Depends(get_db)):
    """Dashboard principal - últimas clasificaciones y estadísticas"""
    try:
        container = bootstrap(session=db)

        # Obtén últimas clasificaciones
        recent = db.query(ClassificationModel).order_by(
            ClassificationModel.created_at.desc()
        ).limit(20).all()

        # Estadísticas
        total = db.query(ClassificationModel).count()
        low_conf = db.query(ClassificationModel).filter(
            ClassificationModel.confidence < 0.6
        ).count()

        avg_conf_result = db.query(func.avg(ClassificationModel.confidence)).scalar() or 0.75
        avg_conf = float(avg_conf_result) if avg_conf_result else 0.75

        accuracy = container.feedback_repository.calculate_accuracy()

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
        return f"<h1>Error en Dashboard</h1><p>{str(e)}</p>"

@app.get("/review", response_class=HTMLResponse)
def dashboard_review(db: Session = Depends(get_db)):
    """Dashboard de revisión - clasificaciones de baja confianza"""
    try:
        # Obtén items de baja confianza
        low_conf_items = db.query(ClassificationModel).filter(
            ClassificationModel.confidence < 0.6
        ).order_by(
            ClassificationModel.created_at.desc()
        ).limit(50).all()

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
        return f"<h1>Error</h1><p>{str(e)}</p>"

@app.get("/metrics", response_class=HTMLResponse)
def dashboard_metrics(db: Session = Depends(get_db)):
    """Dashboard de métricas - precisión, distribución, drift"""
    try:
        # Estadísticas generales
        total = db.query(ClassificationModel).count()

        container = bootstrap(session=db)
        accuracy = container.feedback_repository.calculate_accuracy()

        # Distribución por categoría
        category_dist = db.query(
            ClassificationModel.category,
            func.count(ClassificationModel.id)
        ).group_by(ClassificationModel.category).all()

        category_distribution = {cat: count for cat, count in category_dist}

        # Distribución de confianza (histogramas)
        confidence_ranges = {
            "0-20%": db.query(ClassificationModel).filter(ClassificationModel.confidence < 0.2).count(),
            "20-40%": db.query(ClassificationModel).filter(
                (ClassificationModel.confidence >= 0.2) & (ClassificationModel.confidence < 0.4)
            ).count(),
            "40-60%": db.query(ClassificationModel).filter(
                (ClassificationModel.confidence >= 0.4) & (ClassificationModel.confidence < 0.6)
            ).count(),
            "60-80%": db.query(ClassificationModel).filter(
                (ClassificationModel.confidence >= 0.6) & (ClassificationModel.confidence < 0.8)
            ).count(),
            "80-100%": db.query(ClassificationModel).filter(ClassificationModel.confidence >= 0.8).count(),
        }

        total_feedback = db.query(FeedbackModel).count()
        avg_conf_result = db.query(func.avg(ClassificationModel.confidence)).scalar() or 0.75
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
        return f"<h1>Error</h1><p>{str(e)}</p>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

