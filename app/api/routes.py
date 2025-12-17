# backend/app/api/routes.py
from fastapi import APIRouter
from app.core.config import settings
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.admin_users import router as admin_users_router
from app.api.v1.routes.admin_accounts import router as admin_accounts_router
from app.api.v1.routes.admin_access import router as admin_access_router
from app.api.v1.routes.of_accounts import router as of_accounts_router
from app.api.v1.routes.campaigns import router as campaigns_router
from app.api.v1.routes.runs import router as runs_router

api_router = APIRouter(prefix=settings.API_V1_STR)

api_router.include_router(health_router, tags=["health"])
api_router.include_router(admin_users_router, prefix="/admin/operators", tags=["admin"])
api_router.include_router(admin_accounts_router, prefix="/admin/of-accounts", tags=["admin"])
api_router.include_router(admin_access_router, prefix="/admin/operators", tags=["admin"])
api_router.include_router(of_accounts_router, prefix="/of-accounts", tags=["accounts"])
api_router.include_router(campaigns_router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(runs_router, prefix="/runs", tags=["runs"])