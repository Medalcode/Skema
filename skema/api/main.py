# main.py - API
from fastapi import FastAPI
from pydantic import BaseModel

# Imports estándar (Requiere PYTHONPATH=. o instalación)
from skema.core.domain.models import Requerimiento
from skema.adapters.classifiers.dummy_adapter import DummyClassifierAdapter
from skema.adapters.storage.memory_adapter import InMemoryStorageAdapter

app = FastAPI(title="Skema API", version="0.1.0-alpha")

# Inyección de Dependencias
classifier = DummyClassifierAdapter()
storage = InMemoryStorageAdapter()

class RequerimientoRequest(BaseModel):
    texto: str
    metadata: dict = {}

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0-alpha"}

@app.post("/clasificar")
def clasificar(req_dto: RequerimientoRequest):
    req_dominio = Requerimiento.crear_nuevo(texto=req_dto.texto, metadata=req_dto.metadata)
    resultado = classifier.clasificar(req_dominio)
    storage.guardar(resultado)
    
    return {
        "id": resultado.requerimiento_id,
        "categoria": resultado.categoria,
        "confianza": resultado.confianza,
        "modelo": resultado.modelo_utilizado
    }
