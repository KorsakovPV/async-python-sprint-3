import asyncio
import json

import aiohttp


class Client:
    def __init__(
            self,
            user_id,
            chat_room_id,
            server_host="127.0.0.1",
            server_port=8888
    ):
        self.user_id = user_id
        self.chat_room_id = chat_room_id
        self.server_host = server_host
        self.server_port = server_port

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.server_host, self.server_port)

        # while True:
        for i in range(20):
            await self.send(self.reader, self.writer, 1)

        print('Close the connection')
        self.writer.close()

    async def send(self, reader, writer, i):
        message = json.dumps(
            {
                'message': f'Сообщение {i} от {self.user_id}',
                'chat_room_id': self.chat_room_id,
                'author_id': self.user_id,
            }
        )+'\n'
        print(message)
        # self.reliable_send(data=message)
        # self.writer.writelines(message)
        self.writer.write(message.encode())
        # self.writer.write_eof()
        await asyncio.sleep(5)
        # print(f'Send: {message!r}')
        # writer.write(message.encode())
        # print(json.loads(message))
        # print(type(message))
        await self.writer.drain()




client = Client(
    user_id='81c95c92-8a18-4b22-8ffe-b4163443162f',
    chat_room_id='9b8466d0-df95-4ec9-b9a3-b011577bf046'
)

asyncio.run(client.connect())

