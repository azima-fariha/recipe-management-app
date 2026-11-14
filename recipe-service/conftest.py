from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture()
def client():
    """TestClient against the real FastAPI app, with the lifespan's external
    dependencies (MongoDB via Beanie, Kafka) stubbed out so tests don't need
    either running. Route/service/mapper logic above that boundary is real.
    """
    import main
    from fastapi.testclient import TestClient

    with (
        patch.object(main, "init_db", new=AsyncMock()),
        patch.object(main.AIOKafkaProducer, "start", new=AsyncMock()),
        patch.object(main.AIOKafkaProducer, "stop", new=AsyncMock()),
    ):
        with TestClient(main.app) as test_client:
            yield test_client
