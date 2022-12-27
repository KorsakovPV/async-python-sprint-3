from client import Client
from server import Server


class TestIntegration:

    def test_integration(self, users, chats):

        server = Server()

        await server.main()

        for user in users:
            for chat in chats:

                client = Client(
                    user_id=str(user.id),
                    chat_room_id=str(chat.id),
                )

                await client.connect()
