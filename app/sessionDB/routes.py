from fastapi import FastAPI, Depends
from app.sessionDB.database import async_session_maker, init_db
from app.sessionDB.models import Session, Message
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
