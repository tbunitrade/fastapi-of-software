# backend/app/models/of_account.py
from typing import Optional
from sqlmodel import SQLModel, Field
from app.models.base import TimestampMixin

class OFAccount(TimestampMixin, SQLModel, table=True):
    __tablename__ = "of_accounts"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    account_code: str = Field(index=True, unique=True, nullable=False)  # acct_XXXXXXXX

    # Variant B: ключ глобальный в .env, поэтому в аккаунте не обязателен
    api_key_encrypted: Optional[str] = Field(default=None, nullable=True)

    is_active: bool = Field(default=True, nullable=False)

