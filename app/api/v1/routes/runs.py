# backend/app/api/v1/routes/runs.py

from fastapi import APIRouter, Depends
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/{run_id}")
def get_run(run_id: int, _: User = Depends(get_current_active_user)):
    return {"todo": "get run", "run_id": run_id}