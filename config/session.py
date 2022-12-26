from typing import Generator
from config.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

engine = create_async_engine(
    settings.DB_URL,
    # echo=True,
)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# TODO Спросить у наставника какие есть хорошие практики получения сессия в асинхронном коде.
async def get_db_session() -> Generator[Session, None, None]:
    async with async_session() as session, session.begin():
        yield session
    # await engine.dispose()
