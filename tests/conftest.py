from datetime import date

import pytest

from app import create_app
from app.config import TestConfig
from app.services import clock

HOJE = date(2026, 1, 10)


@pytest.fixture(autouse=True)
def hoje_fixo(monkeypatch):
    monkeypatch.setattr(clock, "today", lambda: HOJE)


@pytest.fixture
def hoje():
    return HOJE


@pytest.fixture
def app():
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logado(client):
    client.post("/registro", data={"username": "gustavo", "password": "senha-segura"})
    return client
