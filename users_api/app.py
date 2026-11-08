"""HTTP API управления пользователями.

Эндпоинты:
    POST   /users            — создать пользователя (201, 409 если логин занят, 422 при ошибке данных)
    GET    /users            — список пользователей
    GET    /users/{user_id}  — получить пользователя (404 если нет)
    PATCH  /users/{user_id}  — изменить логин, имя и/или пароль (404, 409, 422)
    DELETE /users/{user_id}  — удалить пользователя (204, 404)
"""

from fastapi import FastAPI, HTTPException

from users_api import __version__
from users_api.repository import InMemoryUserRepository, User
from users_api.schemas import UserCreate, UserOut, UserUpdate
from users_api.security import hash_password

NOT_FOUND = "Пользователь не найден"
USERNAME_TAKEN = "Имя пользователя уже занято"


def create_app(repository: InMemoryUserRepository | None = None) -> FastAPI:
    """Собрать приложение. Хранилище можно передать снаружи (например, в тестах)."""
    app = FastAPI(title="Users API", version=__version__)
    repo = repository or InMemoryUserRepository()
    app.state.repository = repo

    def get_or_404(user_id: int) -> User:
        user = repo.get(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail=NOT_FOUND)
        return user

    def ensure_username_free(username: str, owner_id: int | None = None) -> None:
        owner = repo.get_by_username(username)
        if owner is not None and owner.id != owner_id:
            raise HTTPException(status_code=409, detail=USERNAME_TAKEN)

    @app.post("/users", status_code=201, response_model=UserOut)
    def create_user(payload: UserCreate):
        """Создать пользователя. Пароль сохраняется только в виде хеша."""
        ensure_username_free(payload.username)
        return repo.add(payload.username, payload.display_name, hash_password(payload.password))

    @app.get("/users", response_model=list[UserOut])
    def list_users():
        """Список всех пользователей в порядке создания."""
        return repo.list_all()

    @app.get("/users/{user_id}", response_model=UserOut)
    def get_user(user_id: int):
        """Получить пользователя по id."""
        return get_or_404(user_id)

    @app.patch("/users/{user_id}", response_model=UserOut)
    def update_user(user_id: int, payload: UserUpdate):
        """Частично изменить пользователя: только переданные поля."""
        get_or_404(user_id)
        if payload.username is not None:
            ensure_username_free(payload.username, owner_id=user_id)
        fields = payload.model_dump(exclude_unset=True)
        if "password" in fields:
            fields["password_hash"] = hash_password(fields.pop("password"))
        return repo.update(user_id, **fields)

    @app.delete("/users/{user_id}", status_code=204)
    def delete_user(user_id: int):
        """Удалить пользователя."""
        if not repo.delete(user_id):
            raise HTTPException(status_code=404, detail=NOT_FOUND)

    return app
