import pytest

from app.config import Settings
from app.service import CoffeeMachineService
from app.storage import JSONStateStorage, MemoryStateStorage, SQLiteStateStorage


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_json_storage_round_trip(tmp_path):
    path = tmp_path / "state.json"
    settings = Settings(200, 100, path, "json")
    service = CoffeeMachineService(JSONStateStorage(path), settings)

    await service.brew("espresso")

    loaded = CoffeeMachineService(JSONStateStorage(path), settings)
    status = await loaded.status()

    assert status["water"]["level"] == 176
    assert status["coffee"]["level"] == 92


@pytest.mark.anyio
async def test_sqlite_storage_round_trip(tmp_path):
    path = tmp_path / "state.db"
    settings = Settings(200, 100, path, "sqlite")
    service = CoffeeMachineService(SQLiteStateStorage(path), settings)

    await service.brew("americano")

    loaded = CoffeeMachineService(SQLiteStateStorage(path), settings)
    status = await loaded.status()

    assert status["water"]["level"] == 52  # 200 - 148
    assert status["coffee"]["level"] == 84  # 100 - 16


@pytest.mark.anyio
async def test_memory_storage_requires_no_disk(tmp_path):
    path = tmp_path / "unused.json"
    settings = Settings(100, 50, path, "memory")
    storage = MemoryStateStorage()
    service = CoffeeMachineService(storage, settings)

    await service.brew("espresso")
    status = await service.status()

    assert status["water"]["level"] == 76
    assert status["coffee"]["level"] == 42
    assert not path.exists()
