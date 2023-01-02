import asyncio
import datetime
import json

from sqlalchemy.future import select

from config.config_log import logger
from config.session import async_session
from model import ConnectedChatRoomModel, MessageModel
from schemas import MassageCreateSchema, MassageGetSchema


class Server:
    def __init__(self, host='127.0.0.1', port=8888, number_of_last_available_messages=20):
        self.host = host
        self.port = port
        self.loop = asyncio.get_event_loop()
        self.number_of_last_available_messages = number_of_last_available_messages

    async def handle_echo(self, reader, writer):
        """

        :param reader:
        :param writer:
        :return:
        """
        self.reader = reader
        self.writer = writer

        while message_bytes := await self.reader.readline():


            addr = writer.get_extra_info('peername')
            logger.info(f'Входящее подключение с адреса {addr}')

            # message_dict = json.loads(message_bytes)
            value_for_create = MassageCreateSchema(**json.loads(message_bytes))
            message = value_for_create.message
            author_id = value_for_create.author_id

            value_for_sent = MassageGetSchema(**json.loads(message_bytes))

            get_message_from = value_for_sent.get_message_from
            get_message_to = value_for_sent.get_message_to
            chat_room_id = value_for_sent.chat_room_id

            connect_to_chat_at = await self.check_connect_to_chat_room(
                user_id=author_id,
                chat_room_id=chat_room_id
            )

            if connect_to_chat_at:
                await self.create_message_in_db(author_id, chat_room_id, message)

                message_json = await self.send_message_to_client(
                    author_id,
                    chat_room_id,
                    get_message_from,
                    get_message_to,
                    connect_to_chat_at
                )

                writer.write(message_json.encode())
            await writer.drain()

        logger.info('Close the connection')
        writer.close()

    async def send_message_to_client(
            self,
            author_id,
            chat_room_id,
            get_message_from,
            get_message_to,
            connect_to_chat_at,
    ):
        message_json, messages_list_obj = await self.messages_for_sent_client(
            chat_room_id,
            get_message_from,
            get_message_to,
            connect_to_chat_at
        )
        logger.info(
            f'Пользователю {author_id} отправлено '
            f'{len(messages_list_obj)} сообщений из чата {chat_room_id}'
        )
        return message_json

    @staticmethod
    async def create_message_in_db(author_id, chat_room_id, message):
        logger.info(
            f'Пришло сообщение {message} от пользователя '
            f'{author_id}  в чат {chat_room_id}'
        )
        message = MessageModel(
            message=message,
            chat_room_id=chat_room_id,
            author_id=author_id,
        )
        async with async_session() as session, session.begin():
            session.add_all([message])
            await session.commit()

    async def messages_for_sent_client(
            self,
            chat_room_id,
            get_message_from,
            get_message_to,
            connect_to_chat_at
    ):
        get_message_from_max_datetime = datetime.datetime.fromtimestamp(
            get_message_to - 60 * 60, tz=datetime.timezone.utc)
        get_message_from_datetime = datetime.datetime.fromtimestamp(
            get_message_from, tz=datetime.timezone.utc)
        get_message_to_datetime = datetime.datetime.fromtimestamp(
            get_message_to, tz=datetime.timezone.utc
        )
        stmt = select(MessageModel).filter(
            MessageModel.chat_room_id == chat_room_id,
            MessageModel.created_at > connect_to_chat_at,
            MessageModel.created_at > get_message_from_max_datetime,
            MessageModel.created_at > get_message_from_datetime,
            MessageModel.created_at <= get_message_to_datetime,
        ).order_by(MessageModel.created_at.desc()).limit(self.number_of_last_available_messages)
        async with async_session() as session, session.begin():
            messages_list = await session.execute(stmt)
        messages_list_obj = []
        for a1 in messages_list.scalars():
            messages_list_obj.append(a1.to_dict)
        message_json = json.dumps(messages_list_obj) + '\n'
        return message_json, messages_list_obj

    async def main(self):
        logger.info('Стартуем сервер')

        server = await asyncio.start_server(
            self.handle_echo, self.host, self.port)

        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        logger.info(f'Serving on {addrs}')

        async with server:
            await server.serve_forever()

    @staticmethod
    async def check_connect_to_chat_room(user_id, chat_room_id) -> float | None:
        stmt = select(ConnectedChatRoomModel).filter(
            ConnectedChatRoomModel.chat_room_id == chat_room_id,
            ConnectedChatRoomModel.user_id == user_id,
        )
        async with async_session() as session, session.begin():
            link_user_chat_list = await session.execute(stmt)

        link_user_chat_list_obj = []

        for a1 in link_user_chat_list.scalars():
            link_user_chat_list_obj.append(a1)

        if link_user_chat_list_obj:
            return link_user_chat_list_obj[0].created_at
        return None


async def async_main_server():
    server = Server()

    await server.main()


if __name__ == '__main__':
    asyncio.run(async_main_server())
