# import asyncio
# from config.config import settings
# from sqlalchemy.ext.asyncio import create_async_engine
#
# # from config.session import engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.ext.asyncio import create_async_engine
# from sqlalchemy.orm import sessionmaker
from model import OrderModel, TariffOrderModel

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

import asyncio

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import sessionmaker

# print(settings.DB_URL)

# DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/asyncalchemy"
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/async_python_sprint_3"

import asyncio

from sqlalchemy.ext.asyncio import create_async_engine


async def async_main():
    engine = create_async_engine(
        DATABASE_URL, echo=True,
    )

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    # async with engine.begin() as conn:
    async with async_session() as session:
        async with session.begin():
            # await conn.run_sync(meta.drop_all)
            # await conn.run_sync(meta.create_all)
            print(type(session))
            tariffs = []
            for i in range(5):
                tariffs.append(
                    TariffOrderModel(
                        type=f'type{i}',
                        tariff_concat_code=f'tariff_concat_code{i}'
                    )
                )

            session.add_all(tariffs)

            stmt = select(TariffOrderModel)#.options(selectinload(A.bs))

            result = await session.execute(stmt)

            for a1 in result.scalars():
                print(a1)

            result = await session.execute(select(TariffOrderModel).order_by(TariffOrderModel.id))

            a1 = result.scalars().first()

            print(a1.type)

            a1.type = "new data"

            print(a1.type)

            await session.commit()

            print(a1.type)

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
    await engine.dispose()


asyncio.run(async_main())
