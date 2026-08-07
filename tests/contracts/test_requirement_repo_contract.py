
from skema.adapters.storage import InMemoryRequirementRepository
from skema.core.models import Requirement


async def test_inmemory_requirement_repository_contract():
    repo = InMemoryRequirementRepository()

    req = Requirement.create(text="We need a login page with SSO")

    await repo.save(req)

    loaded = await repo.get_by_id(req.id)
    assert loaded is not None
    assert loaded.id == req.id
    assert loaded.text == req.text
    assert loaded.context == {}

    missing = await repo.get_by_id("nonexistent")
    assert missing is None


async def test_get_recent_respects_limit():
    repo = InMemoryRequirementRepository()
    req1 = Requirement.create(text="First")
    req2 = Requirement.create(text="Second")
    req3 = Requirement.create(text="Third")

    await repo.save(req1)
    await repo.save(req2)
    await repo.save(req3)

    recent = await repo.get_recent(limit=2)
    assert len(recent) == 2

    all_items = await repo.get_recent(limit=10)
    assert len(all_items) == 3
