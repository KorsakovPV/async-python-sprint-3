import asyncio
import datetime
import json

from config.config_log import logger
from config.session import async_session
from model import MessageModel

from sqlalchemy.orm import selectinload

from config.config_log import logger
from config.session import async_session, engine
from model import UserModel, ChatRoomModel, MessageModel

from sqlalchemy.future import select

import asyncio


class Server:
    def __init__(self, host="127.0.0.1", port=8888):
        self.host = host
        self.port = port
        self.loop = asyncio.get_event_loop()

    async def listen(self):
        pass

    async def handle_echo(self, reader, writer):
        self.reader = reader
        self.writer = writer

        while message_bytes := await self.reader.readline():

            if message_bytes:
                print(message_bytes)

                addr = writer.get_extra_info('peername')
                print(addr)

                message_dict = json.loads(message_bytes)

                # Создаем сообщение
                message = MessageModel(
                    message=message_dict.get('message'),
                    chat_room_id=message_dict.get('chat_room_id'),
                    author_id=message_dict.get('author_id'),
                )
                async with async_session() as session, session.begin():
                    session.add_all([message])
                    await session.commit()
            else:
                break
            get_message_from = datetime.datetime.fromtimestamp(message_dict.get('get_message_from'), tz=datetime.timezone.utc)
            get_message_to = datetime.datetime.fromtimestamp(message_dict.get('get_message_to'), tz=datetime.timezone.utc)
            print(get_message_from, get_message_to)
            # get_message_from = datetime.datetime.utcfromtimestamp(message_dict.get('get_message_from')).strftime('%Y-%m-%d %H:%M:%S')
            # get_message_to = datetime.datetime.utcfromtimestamp(message_dict.get('get_message_from')).strftime('%Y-%m-%d %H:%M:%S')
            # stmt = select(MessageModel).filter(MessageModel.created_by < dt)
            stmt = select(MessageModel).filter(
                # MessageModel.created_at < datetime.datetime.fromtimestamp(1672106816.991352, tz=datetime.timezone.utc),
                # MessageModel.created_at < datetime.datetime.fromtimestamp(1672106816.991352, tz=datetime.timezone.utc),

                MessageModel.chat_room_id == message_dict.get('chat_room_id'),
                MessageModel.created_at > get_message_from,
                MessageModel.created_at <= get_message_to,
            )

            # # .options(selectinload(A.bs))
            async with async_session() as session, session.begin():
                messages_list = await session.execute(stmt)

            messages_list_obj = []

            for a1 in messages_list.scalars():
                messages_list_obj.append(a1.to_dict)

                # # print(f"Send: {message!r}")

            message_json = json.dumps(messages_list_obj) + '\n'

            print(len(messages_list_obj))
            print('Хотим отправить'+message_json)

            writer.write(message_json.encode())
            await writer.drain()

        print("Close the connection")
        writer.close()

    async def main(self):
        logger.info('Стартуем сервер')

        server = await asyncio.start_server(
            self.handle_echo, self.host, self.port)

        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Serving on {addrs}')

        async with server:
            await server.serve_forever()
