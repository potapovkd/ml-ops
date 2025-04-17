"""Эндпойнты модуля чата и сообщений."""

import logging

from fastapi import (
    APIRouter,
)

from base.dependencies import (
    TokenDependency,
    UserServiceDependency,
)
from base.entities import TransactionType
from base.exceptions import (
    EmptyMessageException,
    InsufficientFundsException,
)
from chats.domain.models import (
    Chat,
    ChatType,
    ChatTypeChoice,
    Message,
    MessageData,
    MessageResponse,
    MessageRequest,
)
from chats.entrypoints.api.dependencies import (
    ChatServiceDependency,
    LLMServiceBM25Dependency,
)
from users.domain.models import TransactionData

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=list[Chat], status_code=200)
async def get_chat_list(
    service: ChatServiceDependency,
    data_from_token: TokenDependency,
):
    """Получение списка чатов пользователя."""
    return await service.get_chats(data_from_token.id)


@router.post("/", response_model=Chat, status_code=201)
async def create_chat(
    service: ChatServiceDependency,
    data_from_token: TokenDependency,
    chat_type: ChatType,
) -> Chat:
    """Создание чата."""
    return await service.add_chat(data_from_token.id, chat_type)


@router.get("/{chat_id}/", response_model=list[Message], status_code=200)
async def get_messages(
    chat_id: int,
    service: ChatServiceDependency,
    data_from_token: TokenDependency,
):
    """Получение сообщений из чата."""
    return await service.get_messages(chat_id, data_from_token.id)


@router.post("/chat/{chat_id}/", response_model=MessageResponse)
async def chat(
    chat_id: int,
    request: MessageRequest,
    chat_service: ChatServiceDependency,
    llm_service_with_bm25: LLMServiceBM25Dependency,
    data_from_token: TokenDependency,
    user_service: UserServiceDependency,
):
    """Эндпойнт чата."""
    if not request.message:
        raise EmptyMessageException("Сообщение не может быть пустым.")
    user_id_from_token = data_from_token.id
    balance = await user_service.get_user_balance(user_id_from_token)
    if balance < 10:
        raise InsufficientFundsException("Недостаточно средств на балансе.")
    chat_info = await chat_service.get_chat(chat_id)
    await chat_service.add_message(
        chat_id,
        MessageData(
            role="user",
            content=request.message,
        ),
        user_id_from_token,
    )
    await user_service.add_transaction_for_user(
        user_id_from_token,
        TransactionData(amount=10, transaction_type=TransactionType.EXPENSE),
    )
    llm_service = llm_service_with_bm25
    if chat_info.type == ChatTypeChoice.WITH_LLM:
        model_response = await llm_service.get_model_answer(
            request.message,
            await chat_service.get_messages_without_meta(
                chat_id, user_id_from_token
            ),
        )
    else:
        model_response = await llm_service.get_only_rag_answer(request.message)
    await chat_service.add_message(
        chat_id,
        model_response,
        user_id_from_token,
    )
    return MessageResponse(content=model_response.content)
