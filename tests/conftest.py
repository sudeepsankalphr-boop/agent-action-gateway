import pytest
from fastapi.testclient import TestClient
from app.core import config as config_module
from app.core.database import init_db
from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(config_module.settings, "DB_PATH", str(tmp_path / "test.db"))
    init_db()
    with TestClient(app) as c:
        yield c
