from fastapi.testclient import TestClient

from app.api import health
from app.main import app

client = TestClient(app)


def test_liveness():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


class _FakeSession:
    def __init__(self, fail: bool = False):
        self.fail = fail

    def execute(self, *_a, **_k):
        if self.fail:
            raise RuntimeError("db down")


def _override(session):
    app.dependency_overrides[health.get_session] = lambda: session


def test_ready_ok(monkeypatch):
    monkeypatch.setattr(health, "check_redis", lambda: None)
    _override(_FakeSession())
    try:
        assert client.get("/health/ready").json() == {"status": "ready"}
    finally:
        app.dependency_overrides.clear()


def test_ready_db_failure_returns_503(monkeypatch):
    monkeypatch.setattr(health, "check_redis", lambda: None)
    _override(_FakeSession(fail=True))
    try:
        r = client.get("/health/ready")
        assert r.status_code == 503
        assert "db down" not in r.text  # no internal details leaked
    finally:
        app.dependency_overrides.clear()
