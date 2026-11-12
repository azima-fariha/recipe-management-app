import os

# auth.py reads JWT_SECRET_KEY at import time, mirroring user-service's
# `DATABASE_URL = os.environ["DATABASE_URL"]` pattern for required secrets.
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-key-at-least-32-bytes-long")

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
