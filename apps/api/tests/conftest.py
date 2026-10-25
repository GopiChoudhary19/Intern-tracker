import os

os.environ["INTERN_TRACKER_DEMO_MODE"] = "demo"
os.environ["INTERN_TRACKER_ADMIN_TOKEN"] = "test-admin-token"

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.demo_store import DEMO_STORE
from app.main import app


@pytest.fixture(autouse=True)
def fresh_demo_store():
    # every test starts from the seeded demo data
    DEMO_STORE.__init__()
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth():
    return {"Authorization": f"Bearer {settings.demo_token}"}


@pytest.fixture
def admin():
    return {"X-Admin-Token": "test-admin-token"}
