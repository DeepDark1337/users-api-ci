"""Хранилище пользователей."""

from dataclasses import dataclass


@dataclass
class User:
    """Пользователь в хранилище. В API наружу не отдаётся (см. schemas.UserOut)."""

    id: int
    username: str
    display_name: str
    password_hash: str


class InMemoryUserRepository:
    """Хранилище пользователей в памяти: для учебного API и тестов.

    Интерфейс (add/get/get_by_username/list_all/update/delete) специально простой,
    чтобы позже заменить реализацию на PostgreSQL без изменения API.
    """

    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._next_id = 1

    def add(self, username: str, display_name: str, password_hash: str) -> User:
        """Создать пользователя и выдать ему следующий свободный id."""
        user = User(self._next_id, username, display_name, password_hash)
        self._users[user.id] = user
        self._next_id += 1
        return user

    def get(self, user_id: int) -> User | None:
        """Вернуть пользователя по id или None."""
        return self._users.get(user_id)

    def get_by_username(self, username: str) -> User | None:
        """Найти пользователя по логину без учёта регистра: alice и Alice — один логин."""
        wanted = username.casefold()
        return next((u for u in self._users.values() if u.username.casefold() == wanted), None)

    def list_all(self) -> list[User]:
        """Все пользователи в порядке создания."""
        return sorted(self._users.values(), key=lambda u: u.id)

    def update(self, user_id: int, **fields) -> User | None:
        """Изменить переданные поля пользователя. None — если пользователя нет."""
        user = self._users.get(user_id)
        if user is None:
            return None
        for name, value in fields.items():
            setattr(user, name, value)
        return user

    def delete(self, user_id: int) -> bool:
        """Удалить пользователя. False — если удалять было некого."""
        return self._users.pop(user_id, None) is not None
