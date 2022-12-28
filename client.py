import datetime
import json
import secrets

from sqlalchemy.orm import selectinload

from config.config_log import logger
from model import UserModel, ChatRoomModel

from sqlalchemy.future import select

import asyncio

from config.session import async_session

import aiohttp


class Client:
    def __init__(
            self,
            user_id,
            chat_room_id,
            server_host="127.0.0.1",
            server_port=8888,
            get_messages_in_time=5 * 60
    ):
        self.user_id = user_id
        self.chat_room_id = chat_room_id
        self.server_host = server_host
        self.server_port = server_port
        self.get_message_from = datetime.datetime.now(
            tz=datetime.timezone.utc).timestamp() - get_messages_in_time
        self.get_message_to = 0

    async def connect(self):
        for i in range(20):
            logger.info('Open the connection')
            reader, writer = await asyncio.open_connection(self.server_host,
                                                           self.server_port)

            await self.send(reader, writer, 1)
            writer.close()

        logger.info("Close the connection")

    async def send(self, reader, writer, i):
        self.get_message_to = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
        message = json.dumps(
            {
                'message': f'Сообщение {i} от {self.user_id}',
                'chat_room_id': self.chat_room_id,
                'author_id': self.user_id,
                'get_message_from': self.get_message_from,
                'get_message_to': self.get_message_to,
            }
        ) + '\n'
        writer.write(message.encode())

        self.datetime_last_request = datetime.datetime.now()
        await writer.drain()
        logger.info(f"Отправлено сообщение для чата {self.chat_room_id}")
        data = await reader.readline()
        logger.info(f"Получены сообщения {data} для чата {self.chat_room_id}")

        logger.info('Close the connection')
        writer.close()
        self.get_message_from = self.get_message_to

        await asyncio.sleep(5)


async def get_users():
    async with async_session() as session, session.begin():
        stmt = select(UserModel).options(selectinload(UserModel.messages))

        user_list = await session.execute(stmt)

        users_list_obj = []

        for a1 in user_list.scalars():
            users_list_obj.append(a1)

        if not users_list_obj:

            for i in range(5):
                users_list_obj.append(
                    UserModel(
                        name=f'user_{i}',
                    )
                )

            session.add_all(users_list_obj)

        return users_list_obj


async def get_chats():
    async with async_session() as session, session.begin():
        stmt = select(ChatRoomModel).options(selectinload(ChatRoomModel.messages))

        chat_room_list = await session.execute(stmt)

        chat_room_list_obj = []

        for a1 in chat_room_list.scalars():
            chat_room_list_obj.append(a1)

        if not chat_room_list_obj:

            for i in range(2):
                chat_room_list_obj.append(
                    ChatRoomModel(
                        name=f'chat_room_name{i}',
                    )
                )

            session.add_all(chat_room_list_obj)

        return chat_room_list_obj


async def client_main():
    users = await get_users()
    chats = await get_chats()

    user = secrets.choice(users)
    chat = secrets.choice(chats)

    logger.info(f"Запуск клиента пользователя {user.name} для чата {chat.name}")

    client = Client(
        user_id=str(user.id),
        chat_room_id=str(chat.id),
    )

    await client.connect()


if __name__ == "__main__":
    asyncio.run(client_main())
