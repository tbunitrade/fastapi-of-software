# backend/app/models/user.py
from email.policy import default
from typing import Optional, Literal
from sqlmodel import SQLModel, Field
from app.models.base import TimestampMixin

class User(TimestampMixin, SQLModel, table=True):
    __tablename__ = "users"

    id:             Optional[int] = Field(default=None, primary_key=True)
    email:          str = Field(index=True, unique=True, nullable=False)
    password_hash:  str = Field(nullable=False)

    role: Literal["admin", "operator"] = Field(default="operator", nullable=False)
    is_active: bool = Field(default=True, nullable=False)