"""Тест новой функции из ветки development: эндпоинт проверки работоспособности."""

from fastapi.testclient import TestClient

from users_api import __version__
from users_api.app import create_app


def test_health_returns_ok_and_version():
    response = TestClient(create_app()).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}
