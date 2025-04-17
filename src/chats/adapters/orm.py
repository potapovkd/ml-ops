"""Модуль реализации ORM."""

from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from base.config import ChatTypeChoice
from base.orm import Base


class ChatORM(Base):
    """Модель чата."""

    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[ChatTypeChoice] = mapped_column(
        default=ChatTypeChoice.ONLY_RAG
    )
    user: Mapped["UserORM"] = relationship(back_populates="chats")
    messages: Mapped[list["MessageORM"]] = relationship(
        back_populates="chat", lazy="selectin"
    )

    @property
    def first_message(self):
        """Вывод первого сообщения."""
        if self.messages:
            return self.messages[0].content
        return "Пустой чат"

    @property
    def last_message_timestamp(self):
        """Вывод времени последнего сообщения."""
        if self.messages:
            return self.messages[-1].timestamp
        return None


class MessageORM(Base):
    """Модель сообщения."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey(
            "chats.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    role: Mapped[str]
    content: Mapped[str]
    timestamp: Mapped[datetime] = mapped_column(
        default=func.now(), nullable=False
    )

    chat: Mapped["ChatORM"] = relationship(back_populates="messages")
