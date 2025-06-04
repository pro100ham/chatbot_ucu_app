from datetime import datetime, timedelta
from sqlalchemy import select, update
from app.sessionDB.models import Session
from app.sessionDB.database import async_session_maker

SESSION_TIMEOUT_MINUTES = 10

async def get_or_create_active_session(user_id: str, model: str) -> int:
    async with async_session_maker() as db:
        # 1. Закрити сесії старші за таймаут
        timeout_threshold = datetime.utcnow() - timedelta(minutes=SESSION_TIMEOUT_MINUTES)
        await db.execute(
            update(Session)
            .where(Session.end_time.is_(None), Session.start_time < timeout_threshold)
            .values(end_time=datetime.utcnow())
        )

        # 2. Закрити сесії інших моделей
        await db.execute(
            update(Session)
            .where(Session.end_time.is_(None), Session.user_id == user_id, Session.LLM != model)
            .values(end_time=datetime.utcnow())
        )
        await db.commit()

        # 3. Спроба знайти активну сесію
        result = await db.execute(
            select(Session)
            .where(Session.user_id == user_id, Session.LLM == model, Session.end_time.is_(None))
            .order_by(Session.start_time.desc())
        )
        existing_session = result.scalars().first()

        if existing_session:
            return existing_session.id

        # 4. Створення нової сесії
        new_session = Session(user_id=user_id, LLM=model)
        db.add(new_session)
        await db.flush()
        await db.commit()
        return new_session.id
