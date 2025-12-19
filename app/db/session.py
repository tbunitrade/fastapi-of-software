# backend/app/db/session.py
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URI, pool_pre_ping=True)


def init_db() -> None:
    # ВАЖНО: импортируем модели, чтобы они зарегистрировались в metadata
    from app.models.user import User
    from app.models.of_account import OFAccount
    from app.models.operator_access import OperatorAccountAccess
    from app.models.campaign import Campaign
    from app.models.campaign_run import CampaignRun

    # python -c "from app.db.session import init_db, SQLModel; init_db(); print(len(SQLModel.metadata.tables)); print(list(SQLModel.metadata.tables.keys()))"


    SQLModel.metadata.create_all(engine)

    # Уникальность пары (operator_id, of_account_id)
    # Идемпотентно и безопасно для повторных запусков
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS ux_operator_account_access_operator_of
            ON operator_account_access (operator_id, of_account_id);
        """))


def get_session():
    with Session(engine) as session:
        yield session