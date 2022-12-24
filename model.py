from sqlalchemy import VARCHAR, Column, DateTime, sql, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import declared_attr, relationship
from sqlalchemy.sql import func
from sqlalchemy import BOOLEAN, INTEGER, VARCHAR, Column, Date, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
# from __future__ import annotations

import asyncio
import datetime

from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import select
# from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
# from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
# from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import selectinload


@as_declarative()
class Base:
    id: UUID = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()'),
    )

    created_at = Column(DateTime(timezone=True), server_default=sql.func.now())
    created_by = Column(VARCHAR(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(VARCHAR(255), nullable=True)

    @declared_attr
    def __tablename__(cls):  # noqa 805
        return cls.__name__.lower()


class UserModel(Base):
    __tablename__ = 'users'

    name = Column(VARCHAR(255), nullable=False)
    messages = relationship('MessageModel', backref='user')
    comments = relationship('CommentModel', backref='user')



class ChatRoomModel(Base):
    __tablename__ = 'chat_rooms'

    name = Column(VARCHAR(255), nullable=False)
    messages = relationship('MessageModel', backref='chat')

    def __repr__(self):
        return f'ChatRoom {self.name}'


class MessageModel(Base):
    __tablename__ = 'messages'

    message = Column(VARCHAR(255), nullable=False)
    chat_room_id = Column(UUID(as_uuid=True), ForeignKey('chat_rooms.id'))
    author_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    comments = relationship('CommentModel', backref='message')


    def __repr__(self):
        return f'Author {self.author} message {self.message}'


class CommentModel(Base):
    __tablename__ = 'comments'

    comment = Column(VARCHAR(255), nullable=False)
    message_id = Column(UUID(as_uuid=True), ForeignKey('messages.id'))
    author_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    def __repr__(self):
        return f'Author {self.author} comment {self.comment}'
