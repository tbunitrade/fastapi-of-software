from __future__ import annotations

from typing import Any, Dict, Optional
import httpx

from app.core.config import settings


class ProviderClient:
    def __init__(self) -> None:
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client:
            return self._client

        headers: Dict[str, str] = {"Content-Type": "application/json"}

        # Bearer token из .env
        if settings.PROVIDER_API_KEY:
            token = (
                settings.PROVIDER_API_KEY
                if not settings.PROVIDER_API_KEY_PREFIX
                else f"{settings.PROVIDER_API_KEY_PREFIX} {settings.PROVIDER_API_KEY}"
            )
            headers[settings.PROVIDER_API_KEY_HEADER] = token

        self._client = httpx.AsyncClient(
            base_url=settings.PROVIDER_BASE_URL.rstrip("/"),
            timeout=settings.PROVIDER_TIMEOUT_SECONDS,
            headers=headers,
        )
        return self._client

    async def aclose(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def post_json(
            self,
            path: str,
            *,
            json: Dict[str, Any],
    ) -> Dict[str, Any]:
        c = await self._get_client()
        r = await c.post(path, json=json)
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, dict) else {"data": data}

    async def get_json(
            self,
            path: str,
            *,
            params: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        c = await self._get_client()
        r = await c.get(path, params=params or {})
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, dict) else {"data": data}