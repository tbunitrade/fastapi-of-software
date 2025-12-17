# backend/app/core/rbac.py
from fastapi import HTTPException, status
from app.models.user import User


def require_active_user(user: User) -> User:
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    return user


def require_admin(user: User) -> User:
    require_active_user(user)
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return user


def require_operator_or_admin(user: User) -> User:
    require_active_user(user)
    if user.role not in ("admin", "operator"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return user