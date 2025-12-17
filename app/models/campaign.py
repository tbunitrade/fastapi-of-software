# backend/app/models/campaign.py
from typing import Optional, Literal, Any
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import TimestampMixin


class Campaign(TimestampMixin, SQLModel, table=True):
    __tablename__ = "campaigns"

    id: Optional[int] = Field(default=None, primary_key=True)

    of_account_id: int = Field(foreign_key="of_accounts.id", index=True)
    created_by: int = Field(foreign_key="users.id", index=True)

    title: str = Field(default="", nullable=False)
    text: str = Field(nullable=False)

    user_lists: Any = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False),
    )
    excluded_lists: Any = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False),
    )
    user_ids: Any = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False),
    )

    locked_text: bool = Field(default=False, nullable=False)
    price: Optional[int] = Field(default=None)

    media_files: Optional[Any] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
    )
    previews: Optional[Any] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
    )

    scheduled_at: Optional[datetime] = Field(default=None)

    status: Literal["draft", "scheduled", "sending", "done", "failed", "canceled"] = Field(
        default="draft",
        nullable=False,
    )
