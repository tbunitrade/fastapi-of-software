# backend/app/models/operator_access.py
from typing import Optional
from sqlmodel import SQLModel, Field
from app.models.base import TimestampMixin

class OperatorAccountAccess(TimestampMixin, SQLModel, table=True):
    __tablename__ = "operator_account_access"

    id: Optional[int] = Field(default=None, primary_key=True)
    operator_id: int = Field(foreign_key="user.id", nullable=False, index=True)
    of_account_id: int = Field(foreign_key="of_accounts.id", nullable=False, index=True)

    # UNIQUE(operator_id, of_account_id) — добавим через alembic позже (или через __table_args__)