import asyncio

from config.config_log import logger


class Server:
    def __init__(self, host="127.0.0.1", port=8888):
        self.host = host
        self.port = port
        pass

    async def listen(self):
        pass

    async def handle_echo(self, reader, writer):
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')

        print(f"Received {message!r} from {addr!r}")

        print(f"Send: {message!r}")
        writer.write(data)
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
