from datetime import datetime

from pydantic import BaseModel



class Chat(BaseModel):
    """Модель чата."""

    id: int
    user_id: int


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
