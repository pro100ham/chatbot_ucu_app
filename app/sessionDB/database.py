from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.sessionDB.models import Base
import os

# Отримаємо абсолютний шлях до кореня проєкту
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FOLDER = os.path.join(BASE_DIR, "data")
os.makedirs(DB_FOLDER, exist_ok=True)  # Створюємо папку, якщо її нема

DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(DB_FOLDER, 'chat_sessions.db')}"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
