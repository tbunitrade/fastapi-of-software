from __future__ import annotations

from typing import Optional
from sqlmodel import SQLModel, Field
from app.models.base import TimestampMixin


class AudienceListMember(TimestampMixin, SQLModel, table=True):
    __tablename__ = "audience_list_members"

    id: Optional[int] = Field(default=None, primary_key=True)

    audience_list_id: int = Field(foreign_key="audience_lists.id", index=True)
    provider_user_id: int = Field(index=True, nullable=False)