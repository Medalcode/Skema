import unittest
from skema.core.domain.models import Requirement, ClassificationResult, ConfidenceScore
from skema.core.application.use_cases import ClassifyRequirementUseCase
from skema.adapters.classifiers.dummy_adapter import DummyClassifierAdapter
from skema.adapters.storage.memory_adapter import InMemoryClassificationRepository

class TestHexagonalArchitecture(unittest.TestCase):
    
    def setUp(self):
        self.classifier = DummyClassifierAdapter()
        self.storage = InMemoryClassificationRepository()
        self.use_case = ClassifyRequirementUseCase(self.classifier, self.storage)

    def test_flow_use_case(self):
        """
        Verifica el Caso de Uso completo: Recepción -> Clasificación -> Guardado
        """
        # 1. Input
        text_input = "System must report errors via PDF"
        req = Requirement.create(text=text_input)
        
        # 2. Execution (The Action)
        result = self.use_case.execute(req)
        
        # 3. Verification
        # Check Result
        self.assertEqual(result.category, "Reporting")
        
        # Check Side Effect (Persistence)
        stored = self.storage.get_by_requirement_id(result.requirement_id)
        self.assertIsNotNone(stored)
        self.assertEqual(stored.requirement_id, result.requirement_id)

    def test_confidence_score_validation(self):
        with self.assertRaises(ValueError):
            ConfidenceScore(1.5)

if __name__ == '__main__':
    unittest.main()
