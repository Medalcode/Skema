from typing import Dict, Optional
from skema.core.ports.interfaces import ClassificationRepositoryPort
from skema.core.domain.models import ClassificationResult

class InMemoryClassificationRepository(ClassificationRepositoryPort):
    """
    Adaptador en memoria para persistir RESULTADOS.
    """
    def __init__(self):
        self._storage: Dict[str, ClassificationResult] = {}

    def save(self, result: ClassificationResult) -> None:
        print(f"[Repo] Saving Result: {result.requirement_id} -> {result.category}")
        self._storage[result.requirement_id] = result

    def get_by_requirement_id(self, req_id: str) -> Optional[ClassificationResult]:
        return self._storage.get(req_id)
