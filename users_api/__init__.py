"""
# Users API

Учебное API управления пользователями мессенджера (ПР4 — TDD, ПР2 — CI/CD).

## Модули

- `users_api.app` — эндпоинты HTTP API (FastAPI);
- `users_api.schemas` — схемы запросов и ответов, правила проверки данных;
- `users_api.repository` — хранилище пользователей;
- `users_api.security` — хеширование паролей argon2id.

## Быстрый старт

```
pip install -r requirements.txt
uvicorn users_api.app:create_app --factory --reload
```

Интерактивная документация эндпоинтов после запуска: `http://127.0.0.1:8000/docs`.

Эта страница генерируется автоматически из docstring'ов кода при каждом обновлении ветки `main`.
"""

__version__ = "1.1.0"
