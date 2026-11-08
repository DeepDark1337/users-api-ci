"""Тесты API управления пользователями (ПР4, TDD). Каждый тест появился раньше кода, который он проверяет."""

import pytest
from fastapi.testclient import TestClient

from users_api.app import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def create(client, username="alice", display_name="Alice", password="secret123"):
    return client.post(
        "/users",
        json={"username": username, "display_name": display_name, "password": password},
    )


# Итерация 1
def test_create_user_returns_201_and_id(client):
    response = create(client)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["username"] == "alice"
    assert body["display_name"] == "Alice"


# Итерация 2
def test_get_user_by_id(client):
    created = create(client).json()
    response = client.get(f"/users/{created['id']}")
    assert response.status_code == 200
    assert response.json()["username"] == "alice"


# Итерация 3
def test_get_unknown_user_returns_404(client):
    assert client.get("/users/999").status_code == 404


# Итерация 4
def test_password_is_not_returned(client):
    created = create(client).json()
    fetched = client.get(f"/users/{created['id']}").json()
    for body in (created, fetched):
        assert "password" not in body
        assert "password_hash" not in body


# Итерация 5
def test_password_is_stored_as_hash(client):
    from users_api.security import verify_password

    created = create(client, password="secret123").json()
    stored = client.app.state.repository.get(created["id"])
    assert stored.password_hash != "secret123"
    assert stored.password_hash.startswith("$argon2")
    assert verify_password("secret123", stored.password_hash)
    assert not verify_password("wrong-pass", stored.password_hash)


# Итерация 6
def test_duplicate_username_returns_409(client):
    create(client)
    response = create(client, display_name="Другая Алиса")
    assert response.status_code == 409
    assert client.get("/users/2").status_code == 404  # второй пользователь не создан


# Итерация 7
@pytest.mark.parametrize("username", ["ab", "a" * 33, "with space", "кирилл", "", "bad-name"])
def test_invalid_username_returns_422(client, username):
    assert create(client, username=username).status_code == 422


# Итерация 8
@pytest.mark.parametrize("password", ["", "12345"])
def test_short_password_returns_422(client, password):
    assert create(client, password=password).status_code == 422


def test_password_of_six_chars_is_accepted(client):
    assert create(client, password="123456").status_code == 201


# Итерация 9
@pytest.mark.parametrize("display_name", ["", "   ", "x" * 65])
def test_invalid_display_name_returns_422(client, display_name):
    assert create(client, display_name=display_name).status_code == 422


def test_display_name_is_trimmed(client):
    assert create(client, display_name="  Alice  ").json()["display_name"] == "Alice"


# Итерация 10
def test_list_users_in_creation_order(client):
    for name in ("alice", "bob", "carol"):
        create(client, username=name, display_name=name.title())
    response = client.get("/users")
    assert response.status_code == 200
    assert [u["username"] for u in response.json()] == ["alice", "bob", "carol"]


# Итерация 11
def test_update_display_name(client):
    user = create(client).json()
    response = client.patch(f"/users/{user['id']}", json={"display_name": "Алиса"})
    assert response.status_code == 200
    assert response.json()["display_name"] == "Алиса"
    assert client.get(f"/users/{user['id']}").json()["display_name"] == "Алиса"


# Итерация 12
def test_update_unknown_user_returns_404(client):
    assert client.patch("/users/999", json={"display_name": "Кто-то"}).status_code == 404


def test_update_username_to_taken_returns_409(client):
    create(client, username="alice")
    bob = create(client, username="bob", display_name="Bob").json()
    assert client.patch(f"/users/{bob['id']}", json={"username": "alice"}).status_code == 409


def test_update_username(client):
    user = create(client).json()
    response = client.patch(f"/users/{user['id']}", json={"username": "alice_new"})
    assert response.status_code == 200
    assert response.json()["username"] == "alice_new"


# Итерация 13
def test_update_password(client):
    from users_api.security import verify_password

    user = create(client, password="secret123").json()
    response = client.patch(f"/users/{user['id']}", json={"password": "new-secret"})
    assert response.status_code == 200
    assert "password" not in response.json()
    stored = client.app.state.repository.get(user["id"])
    assert verify_password("new-secret", stored.password_hash)
    assert not verify_password("secret123", stored.password_hash)


# Итерация 14
def test_delete_user(client):
    user = create(client).json()
    assert client.delete(f"/users/{user['id']}").status_code == 204
    assert client.get(f"/users/{user['id']}").status_code == 404


def test_delete_unknown_user_returns_404(client):
    assert client.delete("/users/999").status_code == 404


# Итерация 15
def test_username_is_unique_case_insensitive(client):
    create(client, username="alice")
    assert create(client, username="Alice").status_code == 409
    bob = create(client, username="bob", display_name="Bob").json()
    assert client.patch(f"/users/{bob['id']}", json={"username": "ALICE"}).status_code == 409
