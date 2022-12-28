import asyncio
import os
import time
from dataclasses import dataclass

import aiohttp
# import aioredis
import pytest
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from config.session import async_session
from model import ChatRoomModel, UserModel

# from elasticsearch import AsyncElasticsearch
# from multidict import CIMultiDictProxy
#
# from .config import config


@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='session')
async def users():
    async with async_session() as session, session.begin():
        stmt = select(UserModel).options(selectinload(UserModel.messages))

        user_list = await session.execute(stmt)

        users_list_obj = []

        for a1 in user_list.scalars():
            users_list_obj.append(a1)

        if not users_list_obj:

            # users = []
            for i in range(5):
                users_list_obj.append(
                    UserModel(
                        name=f'user_{i}',
                    )
                )

            session.add_all(users_list_obj)

        return users_list_obj

@pytest.fixture(scope='session')
async def chats():
    async with async_session() as session, session.begin():
        stmt = select(ChatRoomModel).options(selectinload(ChatRoomModel.messages))

        chat_room_list = await session.execute(stmt)

        chat_room_list_obj = []

        for a1 in chat_room_list.scalars():
            chat_room_list_obj.append(a1)

        if not chat_room_list_obj:

            # chat_room_list_obj = []
            for i in range(2):
                chat_room_list_obj.append(
                    ChatRoomModel(
                        name=f'chat_room_name{i}',
                    )
                )

            session.add_all(chat_room_list_obj)

        return chat_room_list_obj
