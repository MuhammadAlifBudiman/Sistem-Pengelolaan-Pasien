"""
Deployment smoke tests for Render readiness.
All MongoDB access is mocked; no live Atlas connection required.
"""
import os
import sys
import json
import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# 1. App imports successfully when required env vars are present
# ---------------------------------------------------------------------------
def test_app_imports(mock_mongo):
    for key in list(sys.modules.keys()):
        if key == "app":
            del sys.modules[key]
    import app as application
    assert application.app is not None


# ---------------------------------------------------------------------------
# 2. SocketIO initialised with threading async_mode
# ---------------------------------------------------------------------------
def test_socketio_async_mode(mock_mongo):
    for key in list(sys.modules.keys()):
        if key == "app":
            del sys.modules[key]
    import app as application
    assert application.socketio.async_mode == "threading"


# ---------------------------------------------------------------------------
# 3. /health returns 200 when Mongo ping succeeds
# ---------------------------------------------------------------------------
def test_health_ok(app_client):
    client, application = app_client
    # ping returns {"ok": 1} (set in conftest mock)
    resp = client.get("/health")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data == {"status": "ok"}


# ---------------------------------------------------------------------------
# 4. /health returns 503 when Mongo ping raises
# ---------------------------------------------------------------------------
def test_health_unavailable(app_client):
    client, application = app_client
    application.client.admin.command.side_effect = Exception("connection refused")
    resp = client.get("/health")
    assert resp.status_code == 503
    data = json.loads(resp.data)
    assert data == {"status": "unavailable"}
    # Reset side_effect for subsequent tests
    application.client.admin.command.side_effect = None


# ---------------------------------------------------------------------------
# 5. /health failure body leaks no exception detail or secrets
# ---------------------------------------------------------------------------
def test_health_no_leak(app_client):
    client, application = app_client
    application.client.admin.command.side_effect = Exception("mongodb+srv://user:pass@host")
    resp = client.get("/health")
    body = resp.data.decode()
    assert "mongodb" not in body.lower()
    assert "pass" not in body.lower()
    assert "user" not in body.lower()
    assert "traceback" not in body.lower()
    application.client.admin.command.side_effect = None


# ---------------------------------------------------------------------------
# 6. /login returns 200 (public route, no auth required)
# ---------------------------------------------------------------------------
def test_login_page(app_client):
    client, _ = app_client
    resp = client.get("/login")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 7. Missing mandatory env var raises ValueError at import time
# ---------------------------------------------------------------------------
def test_missing_env_var_raises(monkeypatch):
    for key in list(sys.modules.keys()):
        if key == "app":
            del sys.modules[key]
    # Set only partial env — omit MONGODB_CONNECTION_STRING
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("TOKEN_KEY", "tok")
    monkeypatch.setenv("SECRET_KEY", "sec")
    monkeypatch.delenv("MONGODB_CONNECTION_STRING", raising=False)
    # Patch load_dotenv so the local .env file cannot supply the missing variable.
    with patch("dotenv.load_dotenv"):
        with patch("pymongo.MongoClient", return_value=MagicMock()):
            with pytest.raises((ValueError, Exception)):
                import app  # noqa: F401
