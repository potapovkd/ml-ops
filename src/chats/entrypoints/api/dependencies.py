"""Модуль зависимостей для точки входа в API."""

from typing import Annotated

from fastapi import Depends
from langchain_community.retrievers import BM25Retriever

from base.config import (
    get_bm25_retriever_path,
    get_llm_url,
    get_max_tokens_for_model, get_n_relevant_docs,
)
from base.dependencies import SessionFactoryDependency
from base.utils import load_retriever
from chats.services.services import ChatService, LLMService
from chats.services.unit_of_work import ChatSqlAlchemyUnitOfWork


def get_chat_service(
    session_factory: SessionFactoryDependency,
) -> ChatService:
    """Получение сервиса чатов."""
    return ChatService(uow=ChatSqlAlchemyUnitOfWork(session_factory))


ChatServiceDependency = Annotated[ChatService, Depends(get_chat_service)]


bm25_retriever = load_retriever(get_bm25_retriever_path())


def get_bm25_retriever() -> BM25Retriever:
    """Получение ретривера BM25."""
    return bm25_retriever


def get_llm_service_with_bm25(
    llama_url: Annotated[str, Depends(get_llm_url)],
    store: Annotated[BM25Retriever, Depends(get_bm25_retriever)],
) -> LLMService:
    """Получение сервиса большой языковой модели с BM25 в качестве RAG."""
    return LLMService(
        llama_url=llama_url,
        store=store,
        max_tokens=get_max_tokens_for_model(),
        n_relevant_docs=get_n_relevant_docs(),
    )


LLMServiceBM25Dependency = Annotated[
    LLMService, Depends(get_llm_service_with_bm25)
]
