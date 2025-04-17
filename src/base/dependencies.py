"""Модуль основных зависимостей."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from users.services.services import UserService
from users.services.unit_of_work import UserSqlAlchemyUnitOfWork
from .config import (
    get_access_token_expires_minutes,
    get_postgres_url,
    get_refresh_token_expires_hours,
    get_secret_key,
    show_sql_logs,
)
from .data_structures import JWTPayloadDTO
from .utils import JWTHandler

engine = create_async_engine(get_postgres_url(), echo=show_sql_logs())


def get_session_factory() -> async_sessionmaker:
    """Получение фабрики сессий."""
    return async_sessionmaker(bind=engine, autoflush=False, autocommit=False)


SessionFactoryDependency = Annotated[
    async_sessionmaker, Depends(get_session_factory)
]

SecretKeyDependency = Annotated[get_secret_key, Depends(get_secret_key)]


def get_jwt_handler(
    secret_key: SecretKeyDependency,
    access_token_expire_minutes: Annotated[
        int, Depends(get_access_token_expires_minutes)
    ],
    refresh_token_expire_hours: Annotated[
        int, Depends(get_refresh_token_expires_hours)
    ],
) -> JWTHandler:
    """Получение JWT-хендлера."""
    return JWTHandler(
        secret_key=secret_key,
        access_token_expire_minutes=access_token_expire_minutes,
        refresh_token_expire_hours=refresh_token_expire_hours,
    )


JWTHandlerDependency = Annotated[JWTHandler, Depends(get_jwt_handler)]


def get_access_token(
    access_token: Annotated[
        HTTPAuthorizationCredentials, Depends(HTTPBearer())
    ],
    jwt_handler: JWTHandlerDependency,
) -> JWTPayloadDTO:
    """Зависимость access токена."""
    return jwt_handler.get_data_from_access_token(access_token.credentials)


TokenDependency = Annotated[JWTPayloadDTO, Depends(get_access_token)]

from typing import Annotated

from fastapi import Depends


def get_service(
    session_factory: SessionFactoryDependency,
    secret_key: SecretKeyDependency,
) -> UserService:
    """Получение сервиса."""
    return UserService(
        uow=UserSqlAlchemyUnitOfWork(session_factory),
        secret_key=secret_key,
    )


UserServiceDependency = Annotated[UserService, Depends(get_service)]
