"""
Shared fixtures for deployment smoke tests.
MongoDB is monkeypatched to avoid requiring a live Atlas connection.
"""
import os
import pytest
from unittest.mock import MagicMock, patch


def _set_required_env(monkeypatch):
    monkeypatch.setenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("TOKEN_KEY", "test_token_key")
    monkeypatch.setenv("SECRET_KEY", "test_secret_key_very_long_random_string")


@pytest.fixture
def mock_mongo(monkeypatch):
    """Patch MongoClient so no real connection is made."""
    _set_required_env(monkeypatch)
    mock_client = MagicMock()
    mock_client.admin.command.return_value = {"ok": 1}
    with patch("pymongo.MongoClient", return_value=mock_client):
        yield mock_client


@pytest.fixture
def app_client(mock_mongo):
    """Flask test client with mocked MongoDB."""
    import importlib
    import sys
    # Remove cached module so env vars are re-read on import
    for key in list(sys.modules.keys()):
        if key in ("app",):
            del sys.modules[key]

    import app as application
    application.app.config["TESTING"] = True
    with application.app.test_client() as client:
        yield client, application
