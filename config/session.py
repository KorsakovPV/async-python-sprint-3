from typing import Generator
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from config.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Session, sessionmaker

# engine = create_engine(settings.DB_URL)
engine = create_async_engine(
    settings.DB_URL,
    echo=True,
)

# create AsyncSession with expire_on_commit=False
async_session = AsyncSession(engine, expire_on_commit=False)

# sessionmaker version
async_session = async_sessionmaker(engine, expire_on_commit=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    engine.dispose()
    # with SessionLocal.begin() as db_session:
    async with engine.begin() as conn:
        yield conn
        conn.close()
