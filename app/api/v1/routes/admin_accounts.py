# backend/app/api/v1/routes/admin_accounts.py

from fastapi import APIRouter, Depends, status
from app.api.deps import get_current_admin_user
from app.models.user import User

router = APIRouter()

@router.get("")
def list_accounts(_: User = Depends(get_current_admin_user)):
    return {"todo": "list of_accounts"}

@router.post("", status_code=status.HTTP_201_CREATED)
def create_account(_: User = Depends(get_current_admin_user)):
    return {"todo": "create of_account"}

@router.patch("/{id}")
def update_account(id: int, _: User = Depends(get_current_admin_user)):
    return {"todo": "update of_account", "id": id}