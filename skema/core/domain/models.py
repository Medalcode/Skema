from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

@dataclass(frozen=True)
class Requerimiento:
    """
    Representa un requerimiento de entrada en el sistema.
    Es inmutable para evitar efectos secundarios durante el procesamiento.
    """
    id: str
    texto: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def crear_nuevo(cls, texto: str, metadata: Optional[Dict[str, Any]] = None) -> 'Requerimiento':
        return cls(
            id=str(uuid.uuid4()),
            texto=texto,
            metadata=metadata or {}
        )

@dataclass(frozen=True)
class ResultadoClasificacion:
    """
    Resultado estandarizado de un proceso de clasificación.
    """
    requerimiento_id: str
    categoria: str
    confianza: float = 1.0
    modelo_utilizado: str = "unknown"
    timestamp: datetime = field(default_factory=datetime.now)
