from sqlalchemy import inspect
from sqlalchemy.orm import selectinload

from config.config_log import logger
from config.session import async_session, engine
from model import UserModel, ChatRoomModel, MessageModel

from sqlalchemy.future import select

import asyncio

from server import Server


async def async_main_server():
    await init_data()

    server = Server()

    await server.main()




async def init_data():
    # session = get_db_session()
    async with async_session() as session, session.begin():
        # print(type(session))

        # Создаем тестового пользователя

        # users = []
        # for i in range(5):
        #     users.append(
        #         UserModel(
        #             name=f'user_name{i}',
        #         )
        #     )
        #
        # session.add_all(users)

        thing_relations = inspect(UserModel).relationships.items()
        # stmt = select(UserModel, MessageModel).join(UserModel, UserModel.id==MessageModel.author_id)#.options(selectinload(MessageModel))
        stmt = select(UserModel).options(selectinload(UserModel.messages))

        user_list = await session.execute(stmt)

        users_list_obj = []

        for a1 in user_list.scalars():
            users_list_obj.append(a1)

        logger.info(f'user {len(users_list_obj)}')

        # Создаем тестовый чат

        # chat_rooms = []
        # for i in range(2):
        #     chat_rooms.append(
        #         ChatRoomModel(
        #             name=f'chat_room_name{i}',
        #         )
        #     )
        #
        # session.add_all(chat_rooms)

        stmt = select(ChatRoomModel).options(selectinload(ChatRoomModel.messages))

        chat_room_list = await session.execute(stmt)

        chat_room_list_obj = []

        for a1 in chat_room_list.scalars():
            chat_room_list_obj.append(a1)

        logger.info(f'chat_rooms {len(chat_room_list_obj)}')

        # Создаем тестовые сообщения

        # messages = []
        # for i in range(200):
        #     messages.append(
        #         MessageModel(
        #             message=f'chat_room_name{i}',
        #             chat_room_id=chat_room_list_obj[i % len(chat_room_list_obj)].id,
        #             author_id=users_list_obj[i % len(users_list_obj)].id
        #         )
        #     )
        #
        # session.add_all(messages)

        stmt = select(MessageModel)  # .options(selectinload(A.bs))

        messages_list = await session.execute(stmt)

        messages_list_obj = []

        for a1 in messages_list.scalars():
            messages_list_obj.append(a1)

        logger.info(f'messages {len(messages_list_obj)}')

        # for a1 in result.scalars():
        #     print(a1)
        #
        # result = await session.execute(select(TariffOrderModel).order_by(TariffOrderModel.id))
        #
        # a1 = result.scalars().first()
        #
        # print(a1.type)
        #
        # a1.type = "new data"
        #
        # print(a1.type)

        await session.commit()

        # print(a1.type)

        # await conn.add(OrderModel)
        # await conn.query(OrderModel).all()

        # await conn.execute(
        #     t1.insert(), [{"name": "some name 1"}, {"name": "some name 2"}]
        # )

        # async with engine.connect() as conn:
        #     # select a Result, which will be delivered with buffered
        #     # results
        #     result = await conn.execute(select(t1).where(t1.c.name == "some name 1"))
        #
        #     print(result.fetchall())

        # for AsyncEngine created in function scope, close and
        # clean-up pooled connections
        # await engine.dispose()


asyncio.run(async_main_server())
