# backend/app/models/user.py
from typing import Optional
from sqlmodel import SQLModel, Field

from app.models.base import TimestampMixin
from app.models.enums import UserRole

class User(TimestampMixin, SQLModel, table=True):
    __tablename__ = "users"

    id:             Optional[int] = Field(default=None, primary_key=True)
    email:          str = Field(index=True, unique=True, nullable=False)
    password_hash:  str = Field(nullable=False)

    role: UserRole = Field(default=UserRole.operator, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
