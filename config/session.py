from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config.config import settings

engine = create_async_engine(
    settings.DB_URL,
    # echo=True,
)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


# TODO Спросить у наставника какие есть хорошие практики получения сессия в асинхронном коде.
# async def get_db_session() -> AsyncGenerator[Session, None]:
#     async with async_session() as session, session.begin():
#         yield session
#     # await engine.dispose()
