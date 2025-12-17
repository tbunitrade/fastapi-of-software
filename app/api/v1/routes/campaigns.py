# backend/app/api/v1/routes/campaigns.py

from fastapi import APIRouter, Depends
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("")
def create_campaign(_: User = Depends(get_current_active_user)):
    return {"todo": "create campaign"}

@router.get("")
def list_campaigns(_: User = Depends(get_current_active_user)):
    return {"todo": "list campaigns"}

@router.get("/{id}")
def get_campaign(id: int, _: User = Depends(get_current_active_user)):
    return {"todo": "get campaign", "id": id}

@router.patch("/{id}")
def update_campaign(id: int, _: User = Depends(get_current_active_user)):
    return {"todo": "update campaign", "id": id}

@router.post("/{id}/send-now")
def send_now(id: int, _: User = Depends(get_current_active_user)):
    return {"todo": "send now", "id": id}

@router.post("/{id}/schedule")
def schedule(id: int, _: User = Depends(get_current_active_user)):
    return {"todo": "schedule (set scheduled_at + provider create)", "id": id}

@router.post("/{id}/cancel")
def cancel(id: int, _: User = Depends(get_current_active_user)):
    return {"todo": "cancel (provider delete if queue exists)", "id": id}

@router.get("/{id}/runs")
def list_runs_for_campaign(id: int, _: User = Depends(get_current_active_user)):
    return {"todo": "list runs for campaign", "campaign_id": id}