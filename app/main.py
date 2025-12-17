# backend/app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import init_db
from app.api.routes import api_router

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.CREATE_TABLES_ON_STARTUP:
        init_db()
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
app.include_router(api_router)

