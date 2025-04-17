"""Эндпойнты модуля пользователей."""

from fastapi import APIRouter
from fastapi.responses import Response

from base.data_structures import (
    AccessTokenDTO,
    JWTPayloadDTO,
    TokenPairDTO,
)
from base.dependencies import (
    JWTHandlerDependency,
    TokenDependency,
    UserServiceDependency,
)
from base.entities import TransactionType
from ...domain.models import UserCredentials, TransactionData

router = APIRouter()


@router.post("/", status_code=204)
async def create_user(
    service: UserServiceDependency,
    request: UserCredentials,
) -> None:
    """Создание пользователя."""
    await service.add_user(
        UserCredentials(email=request.email, password=request.password)
    )


@router.post("/login/")
async def login(
    response: Response,
    service: UserServiceDependency,
    creds: UserCredentials,
    jwt_handler: JWTHandlerDependency,
) -> TokenPairDTO:
    """Аутентификация пользователя."""
    user = await service.login_user(credentials=creds)
    token_pair = jwt_handler.create_token_pair(JWTPayloadDTO(id=user.id))
    response.set_cookie(
        key="jwt_token",
        value=token_pair.access_token,
        httponly=True,
        secure=True,
    )
    return token_pair


@router.post("/refresh/")
async def refresh(
    response: Response,
    jwt_handler: JWTHandlerDependency,
    refresh_token: TokenDependency,
) -> AccessTokenDTO:
    """Формирование access токена при помощи refresh."""
    access_token = jwt_handler.create_new_access_token_by_refresh_token(
        refresh_token
    )
    response.set_cookie(
        key="jwt_token",
        value=access_token.access_token,
        httponly=True,
        secure=True,
    )
    return access_token


@router.post("/pay/")
async def pay(
    amount: float,
    data_from_token: TokenDependency,
    service: UserServiceDependency,
):
    """Пополнение баланса."""
    user_id_from_token = data_from_token.id
    transaction_data = TransactionData(
        amount=amount, transaction_type=TransactionType.INCOME
    )
    await service.add_transaction_for_user(
        user_id_from_token, transaction_data
    )


@router.get("/balance/")
async def balance(
    data_from_token: TokenDependency,
    service: UserServiceDependency,
):
    """Получение баланса."""
    user_id_from_token = data_from_token.id
    return await service.get_user_balance(user_id_from_token)


@router.get("/transactions/")
async def get_transactions(
    data_from_token: TokenDependency,
    service: UserServiceDependency,
):
    """Получение истории транзакций."""
    return await service.get_transactions_for_user(data_from_token.id)
