# backend/app/models/campaign_run.py
from typing import Optional, Literal, Any
from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import TimestampMixin


class CampaignRun(TimestampMixin, SQLModel, table=True):
    __tablename__ = "campaign_runs"

    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="campaigns.id", index=True, nullable=False)

    provider_queue_id: Optional[str] = Field(default=None, index=True, nullable=True)  # хранить string
    status: Literal["created", "queued", "ready", "done", "failed", "canceled"] = Field(
        default="created", nullable=False
    )

    pending: Optional[int] = Field(default=None, nullable=True)
    sent_count: Optional[int] = Field(default=None, nullable=True)
    viewed_count: Optional[int] = Field(default=None, nullable=True)

    has_error: bool = Field(default=False, nullable=False)
    is_canceled: bool = Field(default=False, nullable=False)
    can_unsend: bool = Field(default=False, nullable=False)
    unsend_seconds: Optional[int] = Field(default=None, nullable=True)

    api_response: Optional[Any] = Field(default=None, sa_column=Column(JSONB), nullable=True)
    last_polled_at: Optional[datetime] = Field(default=None, nullable=True)