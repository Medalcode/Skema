import pytest
from skema.core.models import ClassificationResult, ConfidenceScore, Requirement
from skema.infrastructure.repositories import (
    PostgreSQLClassificationRepository,
    PostgreSQLFeedbackRepository,
    PostgreSQLRequirementRepository,
)


async def test_pg_requirement_save_and_get(db_session):
    repo = PostgreSQLRequirementRepository(db_session)
    req = Requirement.create(text="Add export to CSV")

    await repo.save(req)

    loaded = await repo.get_by_id(req.id)
    assert loaded is not None
    assert loaded.text == "Add export to CSV"
    assert loaded.context == {"_test": True} or loaded.context == {}


async def test_pg_classification_save_and_get(db_session):
    class_repo = PostgreSQLClassificationRepository(db_session)
    req_repo = PostgreSQLRequirementRepository(db_session)

    req = Requirement.create(text="Server is down")
    await req_repo.save(req)

    result = ClassificationResult(
        requirement_id=req.id,
        category="Infrastructure",
        confidence=ConfidenceScore(0.95),
        model_version="test-v1",
    )
    await class_repo.save(result)

    loaded = await class_repo.get_by_requirement_id(req.id)
    assert loaded is not None
    assert loaded.category == "Infrastructure"
    assert loaded.confidence.value == pytest.approx(0.95)


async def test_pg_feedback_save_and_accuracy(db_session):
    req_repo = PostgreSQLRequirementRepository(db_session)
    class_repo = PostgreSQLClassificationRepository(db_session)
    feedback_repo = PostgreSQLFeedbackRepository(db_session)

    req = Requirement.create(text="Bug in payment")
    await req_repo.save(req)

    result = ClassificationResult(
        requirement_id=req.id,
        category="Bug",
        confidence=ConfidenceScore(0.80),
        model_version="test-v1",
    )
    await class_repo.save(result)

    await feedback_repo.save_feedback(
        classification_id=result.requirement_id,
        corrected_category="Bug",
        is_correct=True,
        notes="",
    )

    accuracy = await feedback_repo.calculate_accuracy()
    assert accuracy == 1.0


async def test_pg_get_recent_returns_ordered(db_session):
    repo = PostgreSQLRequirementRepository(db_session)
    req1 = Requirement.create(text="First")
    req2 = Requirement.create(text="Second")

    await repo.save(req1)
    await repo.save(req2)

    recent = await repo.get_recent(limit=10)
    assert len(recent) == 2
    assert recent[0].id == req2.id


async def test_pg_low_confidence_filter(db_session):
    req_repo = PostgreSQLRequirementRepository(db_session)
    class_repo = PostgreSQLClassificationRepository(db_session)

    req = Requirement.create(text="Low conf test")
    await req_repo.save(req)

    high = ClassificationResult(
        requirement_id=req.id,
        category="Feature",
        confidence=ConfidenceScore(0.95),
        model_version="v1",
    )
    await class_repo.save(high)

    req2 = Requirement.create(text="Low conf test 2")
    await req_repo.save(req2)
    low = ClassificationResult(
        requirement_id=req2.id,
        category="General",
        confidence=ConfidenceScore(0.30),
        model_version="v1",
    )
    await class_repo.save(low)

    low_conf = await class_repo.get_low_confidence(threshold=0.6)
    assert len(low_conf) == 1
    assert low_conf[0].confidence.value == pytest.approx(0.30)
