# backend/app/db/session.py
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URI, pool_pre_ping=True)

def ensure_constraints() -> None:
    with engine.begin() as conn:
        # 1) operator_account_access: (operator_id, of_account_id) UNIQUE
        conn.execute(text("""
                          CREATE UNIQUE INDEX IF NOT EXISTS ux_operator_account_access_operator_of
                              ON operator_account_access (operator_id, of_account_id);
                          """))

        # 4) campaign_runs.provider_queue_id UNIQUE, but only when NOT NULL
        conn.execute(text("""
                          CREATE UNIQUE INDEX IF NOT EXISTS ux_campaign_runs_provider_queue_id
                              ON campaign_runs (provider_queue_id)
                              WHERE provider_queue_id IS NOT NULL;
                          """))

        # 5) нужно для endpoints
        conn.execute(text("""
                          CREATE UNIQUE INDEX IF NOT EXISTS ux_audience_list_members_list_user
                              ON audience_list_members (audience_list_id, provider_user_id);
                          """))

def init_db() -> None:
    # import models to register in metadata
    from app.models.user import User
    from app.models.of_account import OFAccount
    from app.models.operator_access import OperatorAccountAccess
    from app.models.campaign import Campaign
    from app.models.campaign_run import CampaignRun
    from app.models.audience_list import AudienceList
    from app.models.audience_list_member import AudienceListMember

    SQLModel.metadata.create_all(engine)
    ensure_constraints()

def get_session():
    with Session(engine) as session:
        yield session