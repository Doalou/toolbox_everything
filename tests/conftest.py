"""Fixtures partagées pour les tests Toolbox Everything."""

from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("FLASK_ENV", "testing")
os.environ["RATELIMIT_STORAGE_URI"] = "memory://"


@pytest.fixture(scope="session")
def app():
    from app.services.main import create_app

    flask_app = create_app()
    flask_app.config.update(TESTING=True, DEBUG=False)
    return flask_app


@pytest.fixture()
def client(app):
    return app.test_client()
