import asyncio
from asyncio import AbstractEventLoop
from dataclasses import dataclass
from functools import cached_property
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from _pytest.monkeypatch import MonkeyPatch
from sqlalchemy import text
from sqlalchemy.engine import URL, make_url
# from my_async_app.db import Base, create_engine, create_sessionmaker
# from my_async_app.fastapi_app import app
# from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (AsyncConnection, AsyncEngine, AsyncSession, AsyncTransaction,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeMeta

from config.config import settings
from config.session import create_engine, create_sessionmaker
from model import Base

settings.database_url = f'{settings.database_url}_test'

@dataclass
class DBUtils:
    url: str

    @cached_property
    def postgres_engine(self) -> AsyncEngine:
        url_params = self._parsed_url._asdict()
        url_params['database'] = 'postgres'
        url_with_postgres_db = URL.create(**url_params)
        return create_async_engine(url_with_postgres_db, isolation_level='AUTOCOMMIT')

    @cached_property
    def db_engine(self) -> AsyncEngine:
        return create_async_engine(self.url, isolation_level='AUTOCOMMIT')

    async def create_database(self) -> None:
        query = text(f"CREATE DATABASE {self._parsed_url.database} ENCODING 'utf8'")
        async with self.postgres_engine.connect() as conn:
            await conn.execute(query)

    async def create_tables(self, base: DeclarativeMeta) -> None:
        async with self.db_engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)

    async def drop_database(self) -> None:
        query = text(f'DROP DATABASE {self._parsed_url.database}')
        async with self.postgres_engine.begin() as conn:
            await conn.execute(query)

    async def database_exists(self) -> bool:
        query = text('SELECT 1 FROM pg_database WHERE datname = :database')
        async with self.postgres_engine.connect() as conn:
            query_result = await conn.execute(query, {'database': self._parsed_url.database})
        result = query_result.scalar()
        return bool(result)

    @cached_property
    def _parsed_url(self) -> URL:
        return make_url(self.url)


async def create_db(url: str, base: DeclarativeMeta) -> None:
    db_utils = DBUtils(url=url)

    try:
        if await db_utils.database_exists():
            await db_utils.drop_database()

        await db_utils.create_database()
        await db_utils.create_tables(base)
    finally:
        await db_utils.postgres_engine.dispose()
        await db_utils.db_engine.dispose()




@pytest.fixture(scope='session')
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def _create_db() -> None:
    await create_db(url=settings.database_url, base=Base)


@pytest_asyncio.fixture()
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_engine()
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture()
async def db_connection(engine: AsyncEngine) -> AsyncGenerator[AsyncConnection, None]:
    async with engine.connect() as connection:
        yield connection


@pytest_asyncio.fixture(autouse=True)
async def db_transaction(db_connection: AsyncConnection) -> AsyncGenerator[AsyncTransaction, None]:
    """
    Recipe for using transaction rollback in tests
    https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites  # noqa
    """
    async with db_connection.begin() as transaction:
        yield transaction
        await transaction.rollback()


@pytest_asyncio.fixture(autouse=True)
async def session(
        db_connection: AsyncConnection,
        monkeypatch: MonkeyPatch
) -> AsyncGenerator[AsyncSession, None]:
    session_maker = create_sessionmaker(db_connection)
    monkeypatch.setattr('my_async_app.some_functions.Session', session_maker)

    async with session_maker() as session:
        yield session

# @pytest_asyncio.fixture()
# async def client() -> AsyncGenerator[AsyncClient, None]:
#     async with AsyncClient(app=app, base_url='http://test') as client:
#         yield client
