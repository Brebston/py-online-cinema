from datetime import datetime, timezone

from celery_app import celery_app
from database.session_postgresql import sync_postgresql_engine
from sqlalchemy import delete
from sqlalchemy.orm import Session

from database.models.accounts import ActivationTokenModel, PasswordResetTokenModel, RefreshTokenModel


@celery_app.task(name="tasks.cleanup.cleanup_expired_tokens")
def cleanup_expired_tokens() -> int:
    now = datetime.now(timezone.utc)
    with Session(sync_postgresql_engine) as session:
        total = 0
        for model in (ActivationTokenModel, PasswordResetTokenModel, RefreshTokenModel):
            res = session.execute(delete(model).where(model.expires_at <= now))
            total += res.rowcount or 0
        session.commit()
        return total