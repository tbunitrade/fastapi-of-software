# backend/app/api/v1/routes/of_accounts.py
from fastapi import APIRouter, Depends
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("")
def list_available_accounts(_: User = Depends(get_current_active_user)):
    return {"todo": "list accounts visible to operator/admin"}