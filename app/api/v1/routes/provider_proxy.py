from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.deps import get_current_active_user
from app.integrations.provider_client import ProviderClient
from app.models.user import User
from app.core.config import settings

router = APIRouter()


class SendRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)


@router.post("/{account_id}/send")
async def send_message(
        account_id: str,
        body: SendRequest,
        _: User = Depends(get_current_active_user),
):
    client = ProviderClient()
    try:
        remote_account = settings.PROVIDER_CLIENT_ID or account_id

        # ВАЖНО: заменишь "/RESOURCE" на реальный endpoint твоего провайдера
        data = await client.post_json(
            f"/api/{remote_account}/mass-messaging",
            json={"text": body.text},
        )
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
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
            "offset": offset,
            "query": query,
        }
        # вычищаем None
        params = {k: v for k, v in params.items() if v is not None}

        # Пример: /api/{account_id}/messages/overview
        data = await client.get_json(
            f"/api/{settings.PROVIDER_CLIENT_ID}/messages/overview",
            params=params,
        )
        return {"ok": True, "data": data}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    finally:
        await client.aclose()