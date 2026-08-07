from skema.core.interfaces import ClassificationRepositoryPort, ClassifierPort
from skema.core.models import ClassificationResult, ConfidenceScore, Requirement
from skema.core.use_cases import ClassifyRequirementUseCase


class FakeClassifier(ClassifierPort):
    def __init__(self, fixed_category: str = "TestCategory"):
        self.fixed_category = fixed_category
        self.called = False

    async def classify(self, req: Requirement) -> ClassificationResult:
        self.called = True
        return ClassificationResult(
            requirement_id=req.id,
            category=self.fixed_category,
            confidence=ConfidenceScore(0.99),
            model_version="Fake-v1",
        )


class FakeRepository(ClassificationRepositoryPort):
    def __init__(self):
        self.saved_results: dict[str, ClassificationResult] = {}

    async def save(self, result: ClassificationResult) -> None:
        self.saved_results[result.requirement_id] = result

    async def get_by_requirement_id(self, req_id: str) -> ClassificationResult | None:
        return self.saved_results.get(req_id)

    async def get_recent(self, limit: int = 100) -> list[ClassificationResult]:
        return list(self.saved_results.values())[:limit]

    async def get_low_confidence(self, threshold: float = 0.6,
                                 limit: int = 50) -> list[ClassificationResult]:
        return [
            r for r in self.saved_results.values()
            if r.confidence.value < threshold
        ][:limit]


async def test_execute_orchestrates_flow_correctly():
    fake_clf = FakeClassifier(fixed_category="Critical")
    fake_repo = FakeRepository()
    use_case = ClassifyRequirementUseCase(fake_clf, fake_repo)

    req = Requirement.create("System crash")

    result = await use_case.execute(req)

    assert fake_clf.called
    assert result.category == "Critical"

    stored = await fake_repo.get_by_requirement_id(req.id)
    assert stored is not None
    assert stored.category == "Critical"
