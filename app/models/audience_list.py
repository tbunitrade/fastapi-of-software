# backend/app/models/audience_list.py
from __future__ import annotations

from typing import Optional
from sqlmodel import SQLModel, Field
from app.models.base import TimestampMixin


class AudienceList(TimestampMixin, SQLModel, table=True):
    __tablename__ = "audience_lists"

    id: Optional[int] = Field(default=None, primary_key=True)

    of_account_id: int = Field(foreign_key="of_accounts.id", index=True)
    name: str = Field(nullable=False, index=True)

    kind: str = Field(default="manual", nullable=False)  # manual сейчас, позже rules
    is_active: bool = Field(default=True, nullable=False)