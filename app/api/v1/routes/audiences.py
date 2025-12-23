# backend/app/api/v1/routes/audiences.py
from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select, col
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.api.deps import get_current_active_user
from app.db.session import get_session
from app.models.of_account import OFAccount
from app.models.user import User
from app.models.audience_list import AudienceList
from app.models.audience_list_member import AudienceListMember


router = APIRouter()


# ----- DTOs -----
class BuiltinAudience(BaseModel):
    key: str
    label: str
    requires_period: bool = False


class CustomAudience(BaseModel):
    id: int
    name: str
    count: int
    is_active: bool


class AudienceOptionsResponse(BaseModel):
    builtin: List[BuiltinAudience]
    custom: List[CustomAudience]


class CreateCustomListRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class AddMembersRequest(BaseModel):
    provider_user_ids: List[int] = Field(min_length=1, max_length=500)

def _normalize_provider_user_ids(raw: List[int]) -> List[int]:
    # int() + фильтр пустых/0 + дедуп (порядок сохраняем)
    out: List[int] = []
    for x in (raw or []):
        try:
            v = int(x)
        except Exception:
            continue
        if v > 0:
            out.append(v)

    seen = set()
    uniq: List[int] = []
    for v in out:
        if v in seen:
            continue
        seen.add(v)
        uniq.append(v)

    return uniq


# ----- endpoints -----
@router.get("/{of_account_id}", response_model=AudienceOptionsResponse)
def list_audiences(
        of_account_id: int,
        _: User = Depends(get_current_active_user),
        session: Session = Depends(get_session),
):
    acc = session.get(OFAccount, of_account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="OF account not found")
    builtin = [
        BuiltinAudience(key="fans", label="Fans"),
        BuiltinAudience(key="following", label="Following"),
        BuiltinAudience(key="tagged", label="Tagged"),
        BuiltinAudience(key="recent", label="Recent", requires_period=True),
    ]

    stmt = (
        select(
            AudienceList.id,
            AudienceList.name,
            AudienceList.is_active,
            func.count(AudienceListMember.id).label("cnt"),
        )
        .join(
            AudienceListMember,
            col(AudienceListMember.audience_list_id) == col(AudienceList.id),
            isouter=True,
            )
        .where(col(AudienceList.of_account_id) == of_account_id)
        .group_by(col(AudienceList.id))
        .order_by(col(AudienceList.id).desc())
    )
    rows = session.exec(stmt).all()

    custom = [
        CustomAudience(id=r.id, name=r.name, count=int(r.cnt or 0), is_active=r.is_active)
        for r in rows
    ]
    return AudienceOptionsResponse(builtin=builtin, custom=custom)


@router.post("/{of_account_id}/custom", response_model=CustomAudience)
# def create_custom_list(
#         of_account_id: int,
#         body: CreateCustomListRequest,
#         _: User = Depends(get_current_active_user),
#         session: Session = Depends(get_session),
# ):
#     lst = AudienceList(of_account_id=of_account_id, name=body.name.strip())
#     session.add(lst)
#     session.commit()
#     session.refresh(lst)
#     return CustomAudience(id=lst.id, name=lst.name, count=0, is_active=lst.is_active)

def create_custom_list(
        of_account_id: int,
        body: CreateCustomListRequest,
        _: User = Depends(get_current_active_user),
        session: Session = Depends(get_session),
):
    acc = session.get(OFAccount, of_account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="OF account not found")

    lst = AudienceList(of_account_id=of_account_id, name=body.name.strip())
    session.add(lst)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Integrity error creating audience list")

    session.refresh(lst)
    return CustomAudience(id=lst.id, name=lst.name, count=0, is_active=lst.is_active)


@router.post("/custom/{list_id}/members")
def add_members(
        list_id: int,
        body: AddMembersRequest,
        _: User = Depends(get_current_active_user),
        session: Session = Depends(get_session),
):
    lst = session.get(AudienceList, list_id)
    if not lst:
        raise HTTPException(status_code=404, detail="Audience list not found")

    ids = _normalize_provider_user_ids(body.provider_user_ids)
    if not ids:
        raise HTTPException(status_code=422, detail="provider_user_ids is empty after normalization")

    rows = [{"audience_list_id": list_id, "provider_user_id": v} for v in ids]

    stmt = (
        pg_insert(AudienceListMember.__table__)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["audience_list_id", "provider_user_id"])
    )

    try:
        result = session.exec(stmt)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Integrity error adding members")
    except Exception:
        session.rollback()
        raise

    created = int(getattr(result, "rowcount", 0) or 0)
    return {"ok": True, "created": created}
# def add_members(
#         list_id: int,
#         body: AddMembersRequest,
#         _: User = Depends(get_current_active_user),
#         session: Session = Depends(get_session),
# ):
#     lst = session.get(AudienceList, list_id)
#     if not lst:
#         raise HTTPException(status_code=404, detail="Audience list not found")
#
#     # вставляем без дублей (уникальный индекс защитит)
#     created = 0
#     for uid in body.provider_user_ids:
#         m = AudienceListMember(audience_list_id=list_id, provider_user_id=int(uid))
#         session.add(m)
#         try:
#             session.commit()
#             created += 1
#         except IntegrityError:
#             session.rollback() # дубликат или constraint
#         except Exception:
#             session.rollback()
#             raise
#
#     return {"ok": True, "created": created}


@router.get("/custom/{list_id}/members")
def list_members(
        list_id: int,
        _: User = Depends(get_current_active_user),
        session: Session = Depends(get_session),
):

    stmt = (
        select(AudienceListMember)
        .where(col(AudienceListMember.audience_list_id) == list_id)
        .order_by(col(AudienceListMember.id).desc())
    )
    items = session.exec(stmt).all()
    return {"ok": True, "items": [{"id": i.id, "provider_user_id": i.provider_user_id} for i in items]}


@router.delete("/custom/{list_id}/members/{member_id}")
def delete_member(
        list_id: int,
        member_id: int,
        _: User = Depends(get_current_active_user),
        session: Session = Depends(get_session),
):
    m = session.get(AudienceListMember, member_id)
    if not m or m.audience_list_id != list_id:
        raise HTTPException(status_code=404, detail="Member not found")
    session.delete(m)
    session.commit()
    return {"ok": True}