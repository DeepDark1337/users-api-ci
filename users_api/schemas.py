"""Схемы запросов и ответов API (Pydantic)."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

# Логин: латиница, цифры и подчёркивание, 3–32 символа (как VARCHAR(32) в мессенджере).
Username = Annotated[str, Field(pattern=r"^[A-Za-z0-9_]{3,32}$")]
Password = Annotated[str, Field(min_length=6, max_length=128)]
# Отображаемое имя: пробелы по краям убираются, после этого 1–64 символа.
DisplayName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]


class UserCreate(BaseModel):
    username: Username
    display_name: DisplayName
    password: Password


class UserUpdate(BaseModel):
    """Частичное обновление: передаются только меняющиеся поля."""

    username: Username | None = None
    display_name: DisplayName | None = None
    password: Password | None = None


class UserOut(BaseModel):
    """Пользователь в ответе API. Пароля и хеша здесь нет намеренно."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str
