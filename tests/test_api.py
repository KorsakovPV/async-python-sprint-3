import asyncio
import datetime
import json
import secrets

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from config.config_log import logger
from config.session import async_session
from model import ChatRoomModel, ConnectedChatRoomModel, UserModel


class TestIntegration:

    def test_integration(self):
        pass

    @pytest.mark.asyncio()
    async def test_fetch_from_db(self, session: AsyncSession) -> None:
        print(session)
        pass
        # async with async_session() as session, session.begin():
        stmt = select(ConnectedChatRoomModel)

        connect_chat_room_list = await session.execute(stmt)

        connect_chat_room_list_obj = []

        for a1 in connect_chat_room_list.scalars():
            connect_chat_room_list_obj.append(a1)

        print(connect_chat_room_list_obj)
