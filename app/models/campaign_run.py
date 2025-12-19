# backend/app/models/campaign_run.py
from typing import Optional, Any
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import TimestampMixin
from app.models.enums import CampaignRunStatus


class CampaignRun(TimestampMixin, SQLModel, table=True):
    __tablename__ = "campaign_runs"

    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="campaigns.id", index=True, nullable=False)

    provider_queue_id: Optional[str] = Field(default=None, index=True)

    status: CampaignRunStatus = Field(default=CampaignRunStatus.created, nullable=False )

    pending: Optional[int] = Field(default=None)
    sent_count: Optional[int] = Field(default=None)
    viewed_count: Optional[int] = Field(default=None)

    has_error: bool = Field(default=False, nullable=False)
    is_canceled: bool = Field(default=False, nullable=False)
    can_unsend: bool = Field(default=False, nullable=False)
    unsend_seconds: Optional[int] = Field(default=None)

    api_response: Optional[Any] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    last_polled_at: Optional[datetime] = Field(default=None)