# backend/app/core/crypto.py
from __future__ import annotations

import base64
import hashlib
from typing import Optional

from app.core.config import settings

try:
    from cryptography.fernet import Fernet
except Exception:  # pragma: no cover
    Fernet = None


def _fernet() -> "Fernet":
    if Fernet is None:
        raise RuntimeError("cryptography is not installed. Run: pip install cryptography")

    # Derive stable 32-byte key from SECRET_KEY
    secret = (getattr(settings, "SECRET_KEY", "") or "").encode("utf-8")
    if not secret:
        raise RuntimeError("settings.SECRET_KEY is empty; cannot encrypt api keys.")

    digest = hashlib.sha256(secret).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_api_key(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("api_key is empty")
    f = _fernet()
    token = f.encrypt(raw.encode("utf-8")).decode("utf-8")
    return "enc:" + token


def decrypt_api_key(value: Optional[str]) -> str:
    value = (value or "").strip()
    if not value:
        return ""

    # backward compat: old rows like TEMP_RAW_KEY
    if not value.startswith("enc:"):
        return value

    f = _fernet()
    token = value[4:]
    return f.decrypt(token.encode("utf-8")).decode("utf-8")