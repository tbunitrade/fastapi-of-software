# backend/app/api/deps.py
from fastapi import Depends

from app.core.rbac import require_admin, require_operator_or_admin
from app.models.user import User

# В Full Stack FastAPI Template это уже есть. Подставишь реальный импорт:
# from app.api.deps import get_current_user  (в template может называться иначе)
def get_current_user() -> User:
    # заглушка на Step 1, чтобы роуты стартовали
    # на Step 1 можно возвращать фейкового админа, либо сразу подключить template JWT
    return User(id=1, email="admin@example.com", password_hash="x", role="admin", is_active=True)


def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    return require_operator_or_admin(user)


def get_current_admin_user(user: User = Depends(get_current_user)) -> User:
    return require_admin(user)