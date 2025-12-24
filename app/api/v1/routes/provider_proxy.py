# backend/app/api/v1/routes/provider_proxy.py
from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.api.deps import get_current_active_user
from app.core.config import settings
from app.db.session import get_session
from app.integrations.provider_client import ProviderClient
from app.models.audience_list_member import AudienceListMember
from app.models.user import User
from app.schemas.audience import SendMessageRequest, AudienceType

router = APIRouter()

BUILTIN_USERLIST_MAP = {
    "fans": "fans",
    "following": "following",
    "tagged": "tagged",
    "recent": "recent",
}


def _normalize_user_ids(raw) -> list[int]:
    out: list[int] = []
    for x in (raw or []):
        try:
            v = int(x)
        except Exception:
            continue
        if v > 0:
            out.append(v)

    seen = set()
    uniq: list[int] = []
    for v in out:
        if v in seen:
            continue
        seen.add(v)
        uniq.append(v)

    return uniq


def _ids_to_strings(ids: list[int]) -> list[str]:
    # “канонично” по доке: array<string>
    return [str(x) for x in ids]


@router.post("/{account_id}/send")
async def send_message(
        account_id: str,
        body: SendMessageRequest,
        _: User = Depends(get_current_active_user),
        session: Session = Depends(get_session),
):
    client = ProviderClient()
    try:
        remote_account = account_id or settings.PROVIDER_CLIENT_ID

        payload: dict = {"text": (body.text or "").strip()}
        if not payload["text"]:
            raise HTTPException(status_code=422, detail="text is empty")

        # 1) builtin lists -> userLists
        if body.audience.type in (
                AudienceType.fans,
                AudienceType.following,
                AudienceType.tagged,
                AudienceType.recent,
        ):
            payload["userLists"] = [BUILTIN_USERLIST_MAP[body.audience.type.value]]

            # период (провайдер может игнорить — но по доке params есть)
            if body.audience.type == AudienceType.recent:
                if body.audience.start_date:
                    payload["startDate"] = body.audience.start_date
                if body.audience.end_date:
                    payload["endDate"] = body.audience.end_date

        # 2) custom list -> load userIds from DB
        elif body.audience.type == AudienceType.custom:
            stmt = select(AudienceListMember.provider_user_id).where(
                AudienceListMember.audience_list_id == body.audience.custom_list_id
            )
            ids = session.exec(stmt).all()

            user_ids = _normalize_user_ids(ids)
            if not user_ids:
                raise HTTPException(status_code=400, detail="Custom list is empty")

            payload["userIds"] = _ids_to_strings(user_ids)

        # 3) direct -> userIds from request
        elif body.audience.type == AudienceType.direct:
            user_ids = _normalize_user_ids(body.audience.user_ids or [])
            if not user_ids:
                raise HTTPException(status_code=422, detail="user_ids is empty after normalization")

            payload["userIds"] = _ids_to_strings(user_ids)

        else:
            raise HTTPException(status_code=400, detail="Unsupported audience type")

        path = settings.PROVIDER_SEND_PATH_TEMPLATE.format(account=remote_account)
        data = await client.post_json(path, json=payload)
        return {"ok": True, "data": data}

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.ConnectError as e:
        raise HTTPException(status_code=502, detail=f"Provider connection error: {e}")
    finally:
        await client.aclose()


@router.get("/{account_id}/overview")
async def overview(
        account_id: str,
        start_date: str | None = Query(None),
        end_date: str | None = Query(None),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        query: str | None = Query(None),
        _: User = Depends(get_current_active_user),
):
    client = ProviderClient()
    try:
        remote_account = account_id or settings.PROVIDER_CLIENT_ID

        params = {k: v for k, v in {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
            "offset": offset,
            "query": query,
        }.items() if v is not None}

        path = settings.PROVIDER_OVERVIEW_PATH_TEMPLATE.format(account=remote_account)
        data = await client.get_json(path, params=params)
        return {"ok": True, "data": data}

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    finally:
        await client.aclose()


# C) Queue list (pending/recent): GET /api/{account}/mass-messaging
@router.get("/{account_id}/queue")
async def list_queue(
        account_id: str,
        _: User = Depends(get_current_active_user),
):
    client = ProviderClient()
    try:
        remote_account = account_id or settings.PROVIDER_CLIENT_ID
        path = settings.PROVIDER_SEND_PATH_TEMPLATE.format(account=remote_account)  # /mass-messaging
        data = await client.get_json(path)
        return {"ok": True, "data": data}
    finally:
        await client.aclose()


# Get content of a mass message: GET /api/{account}/mass-messaging/{id}
@router.get("/{account_id}/queue/{queue_id}")
async def get_queue_item(
        account_id: str,
        queue_id: int,
        _: User = Depends(get_current_active_user),
):
    client = ProviderClient()
    try:
        remote_account = account_id or settings.PROVIDER_CLIENT_ID
        base = settings.PROVIDER_SEND_PATH_TEMPLATE.format(account=remote_account)
        data = await client.get_json(f"{base}/{queue_id}")
        return {"ok": True, "data": data}
    finally:
        await client.aclose()