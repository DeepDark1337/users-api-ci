"""Хеширование паролей. Используется argon2id — тот же алгоритм, что в мессенджере."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Вернуть хеш пароля. Соль генерируется автоматически и хранится внутри хеша."""
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Проверить пароль по сохранённому хешу."""
    try:
        return _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False
