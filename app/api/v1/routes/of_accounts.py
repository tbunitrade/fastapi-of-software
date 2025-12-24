# backend/app/api/v1/routes/of_accounts.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app.api.deps import get_current_active_user
from app.db.session import get_session
from app.models.user import User
from app.models.of_account import OFAccount
from app.core.crypto import encrypt_api_key

router = APIRouter()

def _public_acc(a: OFAccount) -> dict:
    return {
        "id": a.id,
        "name": a.name,
        "account_code": a.account_code,
        "is_active": a.is_active,
    }

@router.get("")
def list_available_accounts(
        _: User = Depends(get_current_active_user),
        session: Session = Depends(get_session),
):
    items = session.exec(select(OFAccount).order_by(OFAccount.id.desc())).all()
    return {"items": [_public_acc(i) for i in items]}


class CreateOFAccountRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    account_code: str = Field(min_length=1, max_length=200)  # acct_...
    api_key: str = Field(min_length=5, max_length=5000)       # <-- NEW
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
        api_key_encrypted=encrypt_api_key(body.api_key),  # <-- NEW
        is_active=body.is_active,
    )
    session.add(acc)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail={
                "message": "create_account failed",
                "orig": str(getattr(e, "orig", e)),
            },
        )
    session.refresh(acc)
    return {"ok": True, "item": _public_acc(acc)}


# @router.get("")
# def list_available_accounts(
#         _: User = Depends(get_current_active_user),
#         session: Session = Depends(get_session),
# ):
#     items = session.exec(select(OFAccount).order_by(OFAccount.id.desc())).all()
#     return {"items": [i.model_dump() for i in items]}
#
#
# class CreateOFAccountRequest(BaseModel):
#     name: str = Field(min_length=1, max_length=200)
#     account_code: str = Field(min_length=1, max_length=200)  # acct_...
#     is_active: bool = True
#
#
# @router.post("")
# def create_account(
#         body: CreateOFAccountRequest,
#         _: User = Depends(get_current_active_user),
#         session: Session = Depends(get_session),
# ):
#     acc = OFAccount(
#         name=body.name.strip(),
#         account_code=body.account_code.strip(),
#         is_active=body.is_active,
#     )
#     session.add(acc)
#     try:
#         session.commit()
#     # except IntegrityError:
#     #     session.rollback()
#     #     raise HTTPException(status_code=409, detail="account_code already exists")
#
#     except IntegrityError as e:
#         session.rollback()
#         raise HTTPException(
#             status_code=409,
#             detail={
#                 "message": "create_account failed",
#                 "orig": str(getattr(e, "orig", e)),
#             },
#         )
#     session.refresh(acc)
#     return {"ok": True, "item": acc.model_dump()}


def _dependency_counts(session: Session, account_id: int) -> dict:
    """
    Возвращает количества зависимостей, которые мешают удалить of_accounts.
    Таблицы берём из твоей схемы: audience_lists, audience_list_members, campaigns, campaign_runs, operator_account_access.
    """
    deps = {
        "operator_account_access": 0,
        "audience_lists": 0,
        "audience_list_members": 0,
        "campaigns": 0,
        "campaign_runs": 0,
    }

    deps["operator_account_access"] = int(
        session.exec(
            text("select count(*) from operator_account_access where of_account_id = :id"),
            {"id": account_id},
        ).one()
    )

    deps["audience_lists"] = int(
        session.exec(
            text("select count(*) from audience_lists where of_account_id = :id"),
            {"id": account_id},
        ).one()
    )

    deps["audience_list_members"] = int(
        session.exec(
            text("""
                 select count(*)
                 from audience_list_members m
                          join audience_lists l on l.id = m.audience_list_id
                 where l.of_account_id = :id
                 """),
            {"id": account_id},
        ).one()
    )

    deps["campaigns"] = int(
        session.exec(
            text("select count(*) from campaigns where of_account_id = :id"),
            {"id": account_id},
        ).one()
    )

    deps["campaign_runs"] = int(
        session.exec(
            text("""
                 select count(*)
                 from campaign_runs r
                          join campaigns c on c.id = r.campaign_id
                 where c.of_account_id = :id
                 """),
            {"id": account_id},
        ).one()
    )

    deps["total"] = sum(v for k, v in deps.items() if k != "total")
    return deps


def _force_delete_account(session: Session, account_id: int) -> dict:
    """
    Физически чистим зависимости и удаляем аккаунт.
    Порядок важен: сначала дочерние таблицы, потом родитель.
    """
    deps_before = _dependency_counts(session, account_id)

    # 1) campaign_runs -> campaigns
    session.exec(
        text("""
             delete from campaign_runs
             where campaign_id in (select id from campaigns where of_account_id = :id)
             """),
        {"id": account_id},
    )
    session.exec(
        text("delete from campaigns where of_account_id = :id"),
        {"id": account_id},
    )

    # 2) audience_list_members -> audience_lists
    session.exec(
        text("""
             delete from audience_list_members
             where audience_list_id in (select id from audience_lists where of_account_id = :id)
             """),
        {"id": account_id},
    )
    session.exec(
        text("delete from audience_lists where of_account_id = :id"),
        {"id": account_id},
    )

    # 3) access
    session.exec(
        text("delete from operator_account_access where of_account_id = :id"),
        {"id": account_id},
    )

    # 4) finally account
    session.exec(
        text("delete from of_accounts where id = :id"),
        {"id": account_id},
    )

    session.commit()
    return {"deleted": deps_before}


@router.delete("/{account_id}")
def delete_account(
        account_id: int,
        force: bool = Query(False),
        _: User = Depends(get_current_active_user),
        session: Session = Depends(get_session),
):
    acc = session.get(OFAccount, account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    # 1) без force — только “предупреждение” со списком зависимостей
    deps = _dependency_counts(session, account_id)
    if not force and deps["total"] > 0:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Account has related records. Confirm force delete to cleanup DB.",
                "account_id": account_id,
                "account_code": acc.account_code,
                "will_delete": deps,
                "how_to_force": f"/api/v1/of-accounts/{account_id}?force=true",
            },
        )

    # 2) force=true — чистим БД
    if force:
        summary = _force_delete_account(session, account_id)
        return {"ok": True, "forced": True, "account_id": account_id, **summary}

    # 3) если зависимостей нет — удаляем обычным способом
    try:
        session.delete(acc)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Account has related records; delete/cleanup them first",
        )

    return {"ok": True, "forced": False, "account_id": account_id}