from sqlalchemy import TIMESTAMP, VARCHAR, Column, ForeignKey, UniqueConstraint, func, sql, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import declared_attr, relationship


@as_declarative()
class Base:
    id: Column[UUID] = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()'),
    )

    created_at = Column(TIMESTAMP(timezone=True), server_default=sql.func.current_timestamp())
    created_by = Column(VARCHAR(255), nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.current_timestamp())
    updated_by = Column(VARCHAR(255), nullable=True)

    @declared_attr
    def __tablename__(cls):  # noqa 805
        return cls.__name__.lower()


class UserModel(Base):
    __tablename__ = 'users'

    name = Column(VARCHAR(255), nullable=False)
    messages = relationship('MessageModel', backref='user')  # type: ignore
    comments = relationship('CommentModel', backref='user')  # type: ignore

    @property
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'created_at': self.created_at.timestamp(),
        }


class ChatRoomModel(Base):
    __tablename__ = 'chat_rooms'

    name = Column(VARCHAR(255), nullable=False)
    messages = relationship('MessageModel', backref='chat')  # type: ignore

    def __repr__(self):
        return f'ChatRoom {self.name}'

    @property
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'created_at': self.created_at.timestamp(),
        }


class ConnectedChatRoomModel(Base):
    __tablename__ = 'connected_chat_rooms'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    chat_room_id = Column(UUID(as_uuid=True), ForeignKey('chat_rooms.id'))

    # __table_args__ = (UniqueConstraint('user_id' and 'chat_room_id', name='_user_chat_room_uc'),)

    @property
    def to_dict(self):
        return {
            'user_id': str(self.user_id),
            'chat_room_id': str(self.chat_room_id),
        }


class MessageModel(Base):
    __tablename__ = 'messages'

    message = Column(VARCHAR(255), nullable=False)
    chat_room_id = Column(UUID(as_uuid=True), ForeignKey('chat_rooms.id'))
    author_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    comments = relationship('CommentModel', backref='message')  # type: ignore

    def __repr__(self):
        return f'Author {self.author} message {self.message}'

    @property
    def to_dict(self):
        return {
            'id': str(self.id),
            'message': self.message,
            'chat_room_id': str(self.chat_room_id),
            'author_id': str(self.author_id),
            'created_at': self.created_at.timestamp(),
        }


class CommentModel(Base):
    __tablename__ = 'comments'

    comment = Column(VARCHAR(255), nullable=False)
    message_id = Column(UUID(as_uuid=True), ForeignKey('messages.id'))
    author_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    def __repr__(self):
        return f'Author {self.author} comment {self.comment}'

    @property
    def to_dict(self):
        return {
            'id': str(self.id),
            'comment': self.comment,
            'message_id': str(self.message_id),
            'author_id': str(self.author_id),
            'created_at': self.created_at.timestamp(),
        }