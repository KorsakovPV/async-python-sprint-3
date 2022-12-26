import asyncio
import json

from config.config_log import logger
from config.session import async_session
from model import MessageModel


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
            print(message_bytes)

            if not message_bytes:
                break

            addr = writer.get_extra_info('peername')
            print(addr)

            message_dict = json.loads(message_bytes)
            message = MessageModel(
                message=message_dict.get('message'),
                chat_room_id=message_dict.get('chat_room_id'),
                author_id=message_dict.get('author_id'),
            )
            async with async_session() as session, session.begin():
                session.add_all([message])
                await session.commit()

                # # print(f"Send: {message!r}")
                # writer.write(data)
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
