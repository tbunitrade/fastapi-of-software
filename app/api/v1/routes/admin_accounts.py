# backend/app/api/v1/routes/admin_accounts.py
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.deps import get_current_active_user
from app.db.session import get_session
from app.models.user import User
from app.models.of_account import OFAccount

router = APIRouter()

@router.get("")
def list_accounts(
        _: User = Depends(get_current_active_user),
        session: Session = Depends(get_session),
):
    items = session.exec(select(OFAccount).order_by(OFAccount.id.desc())).all()
    return {"items": [i.model_dump() for i in items]}