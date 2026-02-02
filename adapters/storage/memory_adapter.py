from typing import Dict, Optional
from ...core.ports.interfaces import RepositorioResultadosPort
from ...core.domain.models import ResultadoClasificacion

class InMemoryStorageAdapter(RepositorioResultadosPort):
    """
    Almacenamiento volátil en memoria. 
    Ideal para tests y prototipado rápido.
    """
    def __init__(self):
        self._storage: Dict[str, ResultadoClasificacion] = {}

    def guardar(self, resultado: ResultadoClasificacion) -> None:
        print(f"[StorageAdapter] Guardando en memoria: {resultado.requerimiento_id} -> {resultado.categoria}")
        self._storage[resultado.requerimiento_id] = resultado

    def obtener_por_id(self, id: str) -> Optional[ResultadoClasificacion]:
        return self._storage.get(id)
