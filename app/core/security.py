# backend/app/core/security.py
from typing import Optional
from passlib.context import CryptContext

try:
    from cryptography.fernet import Fernet
except Exception:
    Fernet = None  # type: ignore

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def _get_fernet() -> Optional["Fernet"]:
    if not settings.FERNET_KEY or Fernet is None:
        return None
    return Fernet(settings.FERNET_KEY.encode())


def encrypt_secret(plain: str) -> str:
    f = _get_fernet()
    if not f:
        return plain
    return f.encrypt(plain.encode()).decode()


def decrypt_secret(cipher: str) -> str:
    f = _get_fernet()
    if not f:
        return cipher
    return f.decrypt(cipher.encode()).decode()