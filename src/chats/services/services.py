"""Бизнес-логика."""

from langchain_community.retrievers import BM25Retriever

from ..adapters.repositories import (
    BM25RetrieverRepository,
    LlamaCppRepository,
)
from ..domain.models import Chat, ChatType, Message, MessageData
from ..services.unit_of_work import ChatAbstractUnitOfWork


class ChatService:
    """Сервис для работы с чатами и сообщениями."""

    def __init__(self, uow: ChatAbstractUnitOfWork):
        """Инициализация сервиса."""
        self._uow = uow

    async def get_chat(self, chat_id: int) -> Chat:
        """Получение чата."""
        async with self._uow as uow:
            return await uow.chats.get(chat_id)

    async def add_chat(self, user_id: int, chat_type: ChatType) -> Chat:
        """Создание чата."""
        async with self._uow as uow:
            chat = await uow.chats.add(user_id, chat_type)
            await uow.commit()
            return chat  # noqa R504

    async def delete_chat(self, chat_id: int, user_id: int) -> None:
        """Удаление чата."""
        async with self._uow as uow:
            await uow.chats.delete(chat_id, user_id)
            await uow.commit()

    async def add_message(
        self,
        chat_id: int,
        message_data: MessageData,
        user_id: int,
    ) -> None:
        """Добавление в чат сообщения."""
        async with self._uow as uow:
            await uow.chats.add_message_to_chat(
                chat_id,
                message_data,
                user_id,
            )
            await uow.commit()

    async def get_messages(self, chat_id: int, user_id: int) -> list[Message]:
        """Получение сообщений в чате."""
        async with self._uow as uow:
            return await uow.chats.get_messages_by_chat_id(chat_id, user_id)

    async def get_chats(self, user_id: int) -> list[Chat]:
        """Получение списка чатов пользователя."""
        async with self._uow as uow:
            return await uow.chats.get_chats_by_user_id(user_id)

    async def get_messages_without_meta(
        self, chat_id: int, user_id: int
    ) -> list[MessageData]:
        """Получение сообщений в чате."""
        async with self._uow as uow:
            messages = await uow.chats.get_messages_by_chat_id(
                chat_id, user_id
            )
        return [MessageData(**message.model_dump()) for message in messages]


class LLMService:
    """Сервис для работы с большими языковыми моделями."""

    def __init__(
        self,
        llama_url: str,
        store: BM25Retriever,
        max_tokens: int,
        n_relevant_docs: int,
    ):
        """Инициализация сервиса."""
        self.model = LlamaCppRepository(llama_url)
        self.rag = BM25RetrieverRepository(store)
        self.max_tokens = max_tokens
        self.n_relevant_docs = n_relevant_docs

    async def _get_augmented_prompt_with_relevant_docs(
        self,
        query: str,
    ) -> str:
        """Получить аугментированный релевантными документами запрос."""
        relevant_context_from_store = await self.rag.get_relevant_context(
            query, self.n_relevant_docs
        )
        return self.rag.get_augmented_prompt(
            query,
            relevant_context_from_store,
        )

    async def _get_context_from_relevant_docs(
        self,
        query: str,
    ) -> str:
        """Получить контекст из релевантных документов запрос."""
        return await self.rag.get_relevant_context(query, self.n_relevant_docs)

    async def get_model_answer(
        self,
        query: str,
        history: list[MessageData],
    ) -> MessageData:
        """Получить ответ модели по контексту."""
        prompt = await self._get_augmented_prompt_with_relevant_docs(query)
        history.append(
            MessageData(
                role="user",
                content=prompt,
            )
        )
        context = await self.model.get_context(history, self.max_tokens)
        return await self.model.get_answer(context)

    async def get_only_rag_answer(
        self,
        query: str,
    ) -> MessageData:
        """Получить только результат работы RAG."""
        context = await self._get_context_from_relevant_docs(query)
        return MessageData(
            role="assistant",
            content=context,
        )
