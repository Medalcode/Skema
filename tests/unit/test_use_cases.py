from typing import Optional, Dict
from skema.core.ports.interfaces import ClassifierPort, ClassificationRepositoryPort
from skema.core.domain.models import Requirement, ClassificationResult, ConfidenceScore

# --- FAKES para Testing Unitario Estricto ---
# A diferencia de un Dummy/Mock, un Fake tiene implementación funcional pero simplificada.
# No hardcodeamos lógica de negocio, solo comportamiento controlado.

class FakeClassifier(ClassifierPort):
    def __init__(self, fixed_category: str = "TestCategory"):
        self.fixed_category = fixed_category
        self.called = False

    def classify(self, req: Requirement) -> ClassificationResult:
        self.called = True
        return ClassificationResult(
            requirement_id=req.id,
            category=self.fixed_category,
            confidence=ConfidenceScore(0.99),
            model_version="Fake-v1"
        )

class FakeRepository(ClassificationRepositoryPort):
    def __init__(self):
        self.saved_results: Dict[str, ClassificationResult] = {}

    def save(self, result: ClassificationResult) -> None:
        self.saved_results[result.requirement_id] = result

    def get_by_requirement_id(self, req_id: str) -> Optional[ClassificationResult]:
        return self.saved_results.get(req_id)

# --- TESTS ---

import unittest
from skema.core.application.use_cases import ClassifyRequirementUseCase

class TestClassifyUseCase(unittest.TestCase):
    
    def test_execute_orchestrates_flow_correctly(self):
        # 1. Arrange (Setup con Fakes)
        fake_clf = FakeClassifier(fixed_category="Critical")
        fake_repo = FakeRepository()
        use_case = ClassifyRequirementUseCase(fake_clf, fake_repo)
        
        req = Requirement.create("System crash")

        # 2. Act
        result = use_case.execute(req)

        # 3. Assert (Verificar Orquestación)
        
        # Clasificador fue llamado?
        self.assertTrue(fake_clf.called)
        self.assertEqual(result.category, "Critical")
        
        # Resultado fue persistido?
        stored = fake_repo.get_by_requirement_id(req.id)
        self.assertIsNotNone(stored)
        self.assertEqual(stored.category, "Critical")
