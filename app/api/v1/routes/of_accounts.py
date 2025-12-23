# backend/app/api/v1/routes/of_accounts.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_current_active_user
from app.db.session import get_session
from app.models.user import User
from app.models.of_account import OFAccount

router = APIRouter()

@router.get("")
def list_available_accounts(
        _: User = Depends(get_current_active_user),
        session: Session = Depends(get_session),
):
    items = session.exec(select(OFAccount).order_by(OFAccount.id.desc())).all()
    return {"items": [i.model_dump() for i in items]}


class CreateOFAccountRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    account_code: str = Field(min_length=1, max_length=200)  # acct_...
    api_key_encrypted: str = Field(min_length=1, max_length=5000)
    is_active: bool = True


@router.post("")
def create_account(
        body: CreateOFAccountRequest,
        _: User = Depends(get_current_active_user),
        session: Session = Depends(get_session),
):
    acc = OFAccount(
        name=body.name.strip(),
        account_code=body.account_code.strip(),
        api_key_encrypted=body.api_key_encrypted,
        is_active=body.is_active,
    )
    session.add(acc)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="account_code already exists")
    session.refresh(acc)
    return {"ok": True, "item": acc.model_dump()}