# backend/app/api/v1/routes/admin_access.py
from fastapi import APIRouter, Depends
from app.api.deps import get_current_admin_user
from app.models.user import User

router = APIRouter()

@router.post("/{id}/accounts")
def set_operator_accounts(id: int, _: User = Depends(get_current_admin_user)):
    return {"todo": "set operator->accounts", "operator_id": id}