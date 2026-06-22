import pytest

from skema.adapters.classifiers import DummyClassifierAdapter
from skema.adapters.storage import InMemoryClassificationRepository
from skema.core.models import ConfidenceScore, Requirement
from skema.core.use_cases import ClassifyRequirementUseCase


@pytest.fixture
def use_case():
    classifier = DummyClassifierAdapter()
    storage = InMemoryClassificationRepository()
    return ClassifyRequirementUseCase(classifier, storage)


async def test_flow_use_case(use_case):
    req = Requirement.create(text="System must report errors via PDF")

    result = await use_case.execute(req)

    assert result.category == "Reporting"

    stored = await use_case.repository.get_by_requirement_id(result.requirement_id)
    assert stored is not None
    assert stored.requirement_id == result.requirement_id


def test_confidence_score_validation():
    with pytest.raises(ValueError):
        ConfidenceScore(1.5)
