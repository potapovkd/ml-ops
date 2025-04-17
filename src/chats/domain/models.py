from datetime import datetime

from pydantic import BaseModel

from base.config import ChatTypeChoice


class ChatType(BaseModel):
    """Тип чата."""

    type: ChatTypeChoice


class Chat(ChatType):
    """Модель чата."""

    id: int
    first_message: str
    last_message_timestamp: datetime | None


class MessageData(BaseModel):
    """Модель данных сообщения."""

    role: str
    content: str


class MessageMetadata(BaseModel):
    """Модель метаданных сообщения."""

    id: int
    chat_id: int
    timestamp: datetime


class Message(MessageData, MessageMetadata):
    """Модель сообщения."""


class MessageRequest(BaseModel):
    message: str


class MessageResponse(BaseModel):
    content: str
