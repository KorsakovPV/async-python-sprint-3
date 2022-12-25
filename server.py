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
        pass

    async def listen(self):
        pass

    # async def print_http_headers(url):
    #     url = urllib.parse.urlsplit(url)
    #     if url.scheme == 'https':
    #         reader, writer = await asyncio.open_connection(
    #             url.hostname, 443, ssl=True)
    #     else:
    #         reader, writer = await asyncio.open_connection(
    #             url.hostname, 80)
    #
    #     query = (
    #         f"HEAD {url.path or '/'} HTTP/1.0\r\n"
    #         f"Host: {url.hostname}\r\n"
    #         f"\r\n"
    #     )
    #
    #     writer.write(query.encode('latin-1'))
    #     while True:
    #         line = await reader.readline()
    #         if not line:
    #             break
    #
    #         line = line.decode('latin1').rstrip()
    #         if line:
    #             print(f'HTTP header> {line}')
    #
    #     # Ignore the body, close the socket
    #     writer.close()

    # async def readexactly(self, bytes_count: int) -> bytes:
    #     """
    #     Функция приёма определённого количества байт
    #     """
    #     b = b''
    #     while len(b) < bytes_count:  # Пока не получили нужное количество байт
    #         # part = self.connection.recv(bytes_count - len(b))  # Получаем оставшиеся байты
    #         part = self.reader.read(bytes_count - len(b))  # Получаем оставшиеся байты
    #         # print(52, part.decode())
    #         if not part:  # Если из сокета ничего не пришло, значит его закрыли с другой стороны
    #             raise IOError("Соединение потеряно")
    #         b += part
    #     return b

    async def reliable_receive(self) -> bytes:
        """
        Функция приёма данных
        Обратите внимание, что возвращает тип bytes
        """
        b = b''
        while True:
            part_len = int.from_bytes(await self.reader.readexactly(2),
                                      "big")  # Определяем длину ожидаемого куска
            if part_len == 0:  # Если пришёл кусок нулевой длины, то приём окончен
                return b
            b += await self.reader.readexactly(part_len)  # Считываем сам кусок

    async def handle_echo(self, reader, writer):
        self.reader = reader
        self.writer = writer

        while True:
            f = self.loop.run_until_complete(self.reliable_receive())
            print(f)
            # message_bytes = await self.reliable_receive()

            # message_bytes = await self.reader.read()
            # data = await reader.read(0x1f)

            # if not data:
            #     break
            #
            # message = message_bytes.decode()
            # print(message)
            addr = writer.get_extra_info('peername')
            print(addr)
            # # Сохраняем сообщение в базу
            # # print(f"Received {message!r} from {addr!r}")
            # # print(len(message))






            # message_dict = json.loads(message_bytes)
            # print(message_dict)
            # message = MessageModel(
            #     message=message_dict.get('message'),
            #     chat_room_id=message_dict.get('chat_room_id'),
            #     author_id=message_dict.get('author_id'),
            # )
            # async with async_session() as session, session.begin():
            #     session.add_all([message])
            #     await session.commit()
            # # print(message)
            # #
            # # # print(f"Send: {message!r}")
            # # writer.write(data)
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
