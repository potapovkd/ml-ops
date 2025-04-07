"""Объектная модель приложения."""

import abc
from datetime import datetime
from typing import Literal

import httpx
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from pydantic import BaseModel, EmailStr


class UserCredentials(BaseModel):
    """Модель учетных данных пользователя."""

    email: EmailStr
    password: str


class UserMetadata(BaseModel):
    """Модель метаданных пользователя."""

    id: int
    created_at: datetime


class User(UserCredentials, UserMetadata):
    """Модель пользователя."""


class AccountBalance(BaseModel):
    """Модель данных личного счета пользователя."""

    id: int
    user_id: int


class Transaction(BaseModel):
    """Модель данных транзакции."""

    id: int
    account_id: int
    amount: float
    transaction_type: Literal["income", "expense"]


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


class LlamaCppModelAbstractRepository(abc.ABC):
    """
    Интерфейс для модели, совместимой с llama-cpp-python.

    Абстрактная реализация позволяет унифицировать интерфейс
    независимо от конкретной реализации ML-части сервиса.

    Например, конкретные реализации методов могут работать с python объектом
    типа Llama. Или же отправлять запрос на отдельный микросервис LLM модели.
    """

    @abc.abstractmethod
    def get_answer(self, message_history: list[MessageData]) -> MessageData:
        """Получение ответа модели по переданной истории сообщений."""

    @abc.abstractmethod
    def get_context(
        self,
        message_history: list[MessageData],
        n_tokens: int,
    ) -> MessageData:
        """
        Получение контекста допустимой длины.

        По размеру контекстного окна.
        """


class ChatAbstractRepository(abc.ABC):
    """Абстрактный репозиторий базы данных."""

    @abc.abstractmethod
    async def add(self, user_id: int) -> Chat:
        """Добавление чата для пользователя."""

    @abc.abstractmethod
    async def delete(self, chat_id: int, user_id: int) -> None:
        """Удаление чата для пользователя."""

    @abc.abstractmethod
    async def get_chats_by_user_id(self, user_id: int) -> list[Chat]:
        """Получение списка чатов для пользователя."""

    @abc.abstractmethod
    async def add_message_to_chat(
        self,
        chat_id: int,
        message_data: MessageData,
        user_id: int | None = None,
    ) -> None:
        """Добавление сообщения в чат."""

    @abc.abstractmethod
    async def get_messages_by_chat_id(
        self, chat_id: int, user_id: int
    ) -> list[Message]:
        """Получение списка сообщений из чата."""


class LlamaCppRepository(LlamaCppModelAbstractRepository):
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


class FAISSRepository(RAGAbstractsRepository):
    """Репозитоорий векторной БД/ретривера FAISS."""

    def __init__(self, store: FAISS):
        """Инициализация репозитория."""
        self.store = store

    async def get_relevant_context(self, query: str, n_docs: int) -> str:
        """Поиск релевантных фрагментов текста в хранилище FAISS."""
        relevant_documents = await self.store.asimilarity_search(
            query, k=n_docs
        )
        return "\n".join([doc.page_content for doc in relevant_documents])


class BM25RetrieverRepository(RAGAbstractsRepository):
    """Репозиторий ретривера BM25."""

    def __init__(self, retriever: BM25Retriever):
        """Инициализация репозитория."""
        self.retriever = retriever

    async def get_relevant_context(self, query: str, n_docs: int) -> str:
        """Поиск релевантных фрагментов текста через BM25Retriever."""
        relevant_documents = self.retriever.get_relevant_documents(query)
        relevant_documents = relevant_documents[:n_docs]
        return "\n".join([doc.page_content for doc in relevant_documents])
