from dataclasses import dataclass
from skema.core.models import Requirement, ClassificationResult
from skema.core.interfaces import ClassifierPort, ClassificationRepositoryPort

@dataclass
class ClassifyRequirementUseCase:
    """
    Application Service: ClassifyRequirement
    
    Orquestador del flujo principal de clasificación.
    Su única responsabilidad es coordinar los puertos (Clasificador y Persistencia)
    para cumplir con la intención del usuario.
    """
    classifier: ClassifierPort
    repository: ClassificationRepositoryPort

    async def execute(self, req: Requirement) -> ClassificationResult:
        # 1. Inferencia: Delegamos la "inteligencia" al puerto del clasificador
        result = self.classifier.classify(req)
        
        # 2. Persistencia: Aseguramos que el resultado no se pierda
        await self.repository.save(result)
        
        # 3. Retorno: Devolvemos el resultado para que el presentador (API) lo muestre
        return result
