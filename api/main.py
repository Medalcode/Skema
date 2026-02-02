# main.py - API
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Importaciones del Core y Adaptadores
# Nota: Para que esto funcione, se debe ejecutar desde la raíz del proyecto con `python -m skema.api.main`
# o instalar el paquete en modo editable `pip install -e .`
try:
    from ...core.domain.models import Requerimiento
    from ...adapters.classifiers.dummy_adapter import DummyClassifierAdapter
    from ...adapters.storage.memory_adapter import InMemoryStorageAdapter
except ImportError:
    # Fallback para ejecución simple si no está instalado como paquete
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from skema.core.domain.models import Requerimiento
    from skema.adapters.classifiers.dummy_adapter import DummyClassifierAdapter
    from skema.adapters.storage.memory_adapter import InMemoryStorageAdapter

app = FastAPI(title="Skema API", version="0.1.0-alpha")

# --- Dependency Injection (Manual por ahora) ---
# En un futuro usaremos depends() de FastAPI para mayor flexibilidad
classifier = DummyClassifierAdapter()
storage = InMemoryStorageAdapter()

# --- DTOs de Entrada (Capa de Presentación) ---
# Separamos el modelo de la API del modelo de Dominio
class RequerimientoRequest(BaseModel):
    texto: str
    metadata: dict = {}

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0-alpha"}

@app.post("/clasificar")
def clasificar(req_dto: RequerimientoRequest):
    # 1. Adaptar entrada a Dominio
    # Usamos el factory method del dominio para generar ID y timestamp
    req_dominio = Requerimiento.crear_nuevo(texto=req_dto.texto, metadata=req_dto.metadata)
    
    # 2. Invocar lógica de negocio (Inferencia)
    resultado = classifier.clasificar(req_dominio)
    
    # 3. Persistencia
    storage.guardar(resultado)
    
    # 4. Retornar respuesta
    return {
        "id": resultado.requerimiento_id,
        "categoria": resultado.categoria,
        "confianza": resultado.confianza,
        "modelo": resultado.modelo_utilizado
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
