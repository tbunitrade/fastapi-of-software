# backend/app/api/v1/routes/admin_users.py

from fastapi import APIRouter, Depends, status
from app.api.deps import get_current_admin_user
from app.models.user import User

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
def create_operator(_: User = Depends(get_current_admin_user)):
    return {"todo": "create operator"}

@router.get("")
def list_operators(_: User = Depends(get_current_admin_user)):
    return {"todo": "list operators"}

@router.patch("/{id}")
def update_operator(id: int, _: User = Depends(get_current_admin_user)):
    return {"todo": "update operator", "id": id}