import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


# from job import JobStatus


class MassageCreateSchema(BaseModel):
    message: str
    chat_room_id: UUID
    author_id: UUID


class MassageGetSchema(BaseModel):
    chat_room_id: UUID
    get_message_from: float | None
    get_message_to: float | None


# class CommentCreateSchema(BaseModel):
#     message_id: UUID


class CommentCreateSchema(BaseModel):
    comment: str
    message_id: UUID
    author_id: UUID

