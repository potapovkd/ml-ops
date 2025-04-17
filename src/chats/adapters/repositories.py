"""Модуль реализации паттерна репозиторий."""

import abc

import httpx
from langchain_community.retrievers import BM25Retriever
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.exceptions import DoesntExistException, PermissionException
from .orm import ChatORM, MessageORM
from ..domain.models import Chat, ChatType, Message, MessageData

DOESNT_EXISTS_EXC_MESSAGE = "Чат не найден."
PERMISSION_EXC_MESSAGE = "Невозможно получить доступ."


class ChatAbstractDatabaseRepository(abc.ABC):
    """Абстрактный репозиторий базы данных."""

    @abc.abstractmethod
    async def get(self, chat_id: int) -> Chat:
        """Получение объекта-чата из БД."""

    @abc.abstractmethod
    async def add(self, user_id: int, chat_type: ChatType) -> Chat:
        """Добавление объекта-чата в БД."""

    @abc.abstractmethod
    async def delete(self, chat_id: int, user_id: int | None = None) -> None:
        """Удаление объекта-чата из БД."""

    @abc.abstractmethod
    async def get_chats_by_user_id(self, user_id: int) -> list[Chat]:
        """Получение списка объектов-чатов для пользователя из БД."""

    @abc.abstractmethod
    async def add_message_to_chat(
        self,
        chat_id: int,
        message_data: MessageData,
        user_id: int | None = None,
    ) -> None:
        """Добавление объекта-сообщения для чата в БД."""

    @abc.abstractmethod
    async def get_messages_by_chat_id(
        self, chat_id: int, user_id: int
    ) -> list[Message]:
        """Получение списка объектов-сообщений из чата."""


class ChatSQLAlchemyRepository(ChatAbstractDatabaseRepository):
    """Репозиторий базы данных SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        """Инициализация репозитория."""
        self.session = session

    async def _get(
        self,
        chat_id: int,
        user_id: int | None = None,
        raise_exc: bool = True,
    ) -> ChatORM | None:
        """
        Получение объекта-чата из БД.

        С возможностью выброса исключения.
        """
        chat = await self.session.execute(
            select(ChatORM).filter_by(
                id=chat_id,
            )
        )
        chat = chat.scalars().one_or_none()
        if not chat and raise_exc:
            raise DoesntExistException(DOESNT_EXISTS_EXC_MESSAGE)
        if user_id and chat.user_id != user_id:
            raise PermissionException(PERMISSION_EXC_MESSAGE)
        return chat

    async def get(self, chat_id: int) -> Chat:
        """Получение объекта-чата из БД."""
        chat = await self._get(chat_id=chat_id)
        return Chat(**chat.to_dict_with_property())

    async def add(self, user_id: int, chat_type: ChatType) -> Chat:
        """Добавление объекта-чата в БД."""
        chat = ChatORM(
            user_id=user_id,
            type=chat_type.type,
        )
        self.session.add(chat)
        await self.session.flush()
        await self.session.refresh(chat)
        return Chat(**chat.to_dict_with_property())

    async def delete(self, chat_id: int, user_id: int | None = None) -> None:
        """Удаление объекта-чата из БД."""
        chat = await self._get(chat_id=chat_id, user_id=user_id)
        await self.session.delete(chat)

    async def get_chats_by_user_id(self, user_id: int) -> list[Chat]:
        """Получение списка объектов-чатов для пользователя из БД."""
        chats = await self.session.execute(
            select(ChatORM).filter_by(
                user_id=user_id,
            )
        )
        return [
            Chat(**chat.to_dict_with_property())
            for chat in chats.scalars().all()
        ]

    async def add_message_to_chat(
        self,
        chat_id: int,
        message_data: MessageData,
        user_id: int | None = None,
    ) -> None:
        """Добавление объекта-сообщения для чата в БД."""
        await self._get(chat_id=chat_id, user_id=user_id)
        message = MessageORM(
            chat_id=chat_id,
            **message_data.model_dump(),
        )
        self.session.add(message)

    async def get_messages_by_chat_id(
        self, chat_id: int, user_id: int
    ) -> list[Message]:
        """Получение списка объектов-сообщений из чата."""
        await self._get(chat_id=chat_id, user_id=user_id)
        messages = await self.session.execute(
            select(MessageORM).filter_by(
                chat_id=chat_id,
            )
        )
        return [
            Message(**message.__dict__) for message in messages.scalars().all()
        ]


class LLMAbstractRepository(abc.ABC):
    """Абстрактный репозиторий большой языковой модели."""

    @abc.abstractmethod
    def get_answer(self, context: list[MessageData]) -> MessageData:
        """Получение ответа на переданный контекст."""

    @abc.abstractmethod
    def get_context(
        self, messages: list[MessageData], n_tokens: int
    ) -> list[MessageData]:
        """Получение контекста допустимого размера."""


class LlamaCppRepository(LLMAbstractRepository):
    """Репозиторий, взаимодействующий с микросервисом Llama."""

    def __init__(self, base_url: str):
        """Инициализация репозитория."""
        self.base_url = base_url

    async def get_answer(self, context: list[MessageData]) -> MessageData:
        """Получение ответа от микросервиса Llama."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/get_answer",
                json={
                    "context": [message.model_dump() for message in context]
                },
                timeout=300,
            )
            response.raise_for_status()
            data = response.json()
            return MessageData(**data["message"])

    async def get_context(
        self, messages: list[MessageData], n_tokens: int
    ) -> list[MessageData]:
        """Получение контекста от микросервиса Llama."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/get_context",
                json={
                    "messages": [message.model_dump() for message in messages],
                    "n_tokens": n_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()
            return [MessageData(**msg) for msg in data["context"]]


class RAGAbstractsRepository(abc.ABC):
    """Абстрактный репозиторий RAG-системы."""

    @abc.abstractmethod
    async def get_relevant_context(self, query: str, n_docs: int) -> str:
        """Получение контекста из n_docs релевантных документов."""

    @staticmethod
    def get_augmented_prompt(query: str, context: str) -> str:
        """Дополнение запроса релевантным контекстом."""
        return f"""
            Используя информацию ниже, ответь на следующий запрос:
            Контекст:
            {context}
            Вопрос:
            {query}
        """


class BM25RetrieverRepository(RAGAbstractsRepository):
    """Репозитоорий ретривера BM25."""

    def __init__(self, retriever: BM25Retriever):
        """Инициализация репозитория."""
        self.retriever = retriever

    async def get_relevant_context(self, query: str, n_docs: int) -> str:
        """Поиск релевантных фрагментов текста через BM25Retriever."""
        relevant_documents = self.retriever.get_relevant_documents(query)
        relevant_documents = relevant_documents[:n_docs]
        return "\n".join([doc.page_content for doc in relevant_documents])
