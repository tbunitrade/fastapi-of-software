# backend/app/schemas/audience.py
from __future__ import annotations

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator


class AudienceType(str, Enum):
    fans = "fans"
    following = "following"
    tagged = "tagged"
    recent = "recent"
    custom = "custom"
    direct = "direct"  # если фронт иногда захочет передать userIds прямо


class AudienceRef(BaseModel):
    type: AudienceType
    custom_list_id: Optional[int] = None

    # для UI (период), сейчас НЕ обязан отправлять провайдеру
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    # direct mode
    user_ids: Optional[List[int]] = None

    @model_validator(mode="after")
    def _validate(self):
        if self.type == AudienceType.custom and not self.custom_list_id:
            raise ValueError("custom_list_id is required for audience.type=custom")
        if self.type == AudienceType.direct and not self.user_ids:
            raise ValueError("user_ids is required for audience.type=direct")
        return self


class SendMessageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    audience: AudienceRef