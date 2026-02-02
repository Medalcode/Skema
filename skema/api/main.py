# main.py - API
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

# Imports Limpios (Bootstrap + Domain)
from skema.core.domain.models import Requirement
from skema.bootstrap import bootstrap

# --- Configuración Inicial ---
app = FastAPI(
    title="Skema API", 
    version="0.1.0-alpha",
    description="Intelligent Requirements Classification Platform"
)

# Composition Root (Inyección)
container = bootstrap()

# --- DTOs (Data Transfer Objects) ---
# Capa de Presentación: Estos objetos son "contratos" con el cliente HTTP.
# No son el dominio. Pueden tener nombres diferentes o validaciones extra.

class RequirementRequest(BaseModel):
    text: str = Field(..., min_length=5, description="El texto crudo del requerimiento")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Datos contextuales opcionales")

class ClassificationResponse(BaseModel):
    id: str
    category: str
    confidence: float
    model_version: str

# --- Endpoints ---

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Health check simple para Kubernetes/Load Balancers"""
    return {"status": "ok", "version": "0.1.0-alpha"}

@app.post(
    "/classify", 
    response_model=ClassificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Clasificar un nuevo requerimiento"
)
def classify_endpoint(req_dto: RequirementRequest):
    """
    Recibe un requerimiento de texto, lo procesa con el motor de inferencia activo
    y guarda el resultado.
    """
    try:
        # 1. Adaptación (Mapper: DTO -> Domain)
        # Nota: Aquí atrapamos errores de validación del dominio (ej. texto vacío)
        domain_req = Requirement.create(
            text=req_dto.text, 
            metadata=req_dto.metadata
        )
        
        # 2. Delegación (Llamada al Application Service)
        result = container.classify_requirement.execute(domain_req)
        
        # 3. Adaptación (Mapper: Domain -> DTO)
        return ClassificationResponse(
            id=result.requirement_id,
            category=result.category,
            confidence=result.confidence.value, # Unpack del Value Object
            model_version=result.model_version
        )

    except ValueError as e:
        # Errores de Dominio -> HTTP 400 Bad Request
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )
    except Exception as e:
        # Errores Inesperados -> HTTP 500 Internal Server Error
        # En producción, aquí agregaríamos un log.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal processing error"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
